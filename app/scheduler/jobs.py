import logging
from datetime import datetime
from typing import Any

from app.core.time import utc_now
from app.domain.entities import (
    CalendarIngestionResult,
    ForwardOutcomeRecordResult,
    ForwardOutcomeResolveResult,
    MarketDataIngestionResult,
    ScheduledDigestDeliveryResult,
    Timeframe,
)
from app.observability.health_checks import run_application_health_check
from app.services.data_freshness_service import DataFreshnessService
from app.services.economic_calendar_ingestion_service import EconomicCalendarIngestionService
from app.services.forward_outcome_service import ForwardOutcomeService
from app.services.health_service import HealthService
from app.services.interest_rate_ingestion_service import InterestRateIngestionService
from app.services.market_data_ingestion_service import MarketDataIngestionService
from app.services.scheduled_digest_delivery_service import ScheduledDigestDeliveryService
from app.services.system_state_service import SystemStateService

logger = logging.getLogger(__name__)


async def update_worker_heartbeat_job(service: SystemStateService) -> None:
    await service.update_worker_heartbeat()
    logger.info("worker_heartbeat_updated")


async def application_health_check_job(health_service: HealthService) -> None:
    result = await run_application_health_check(health_service)
    logger.info("worker_health_check_completed", extra={"database_status": result["database"]})


async def scheduled_digest_delivery_job(
    service: ScheduledDigestDeliveryService,
    *,
    as_of: datetime | None = None,
) -> ScheduledDigestDeliveryResult:
    result = await service.run_tick(as_of=as_of or utc_now())
    logger.info(
        "scheduled_digest_delivery_checked",
        extra={
            "delivered": result.delivered,
            "reason": result.decision.reason.value,
        },
    )
    return result


async def market_data_ingestion_job(
    service: MarketDataIngestionService,
    *,
    as_of: datetime | None = None,
) -> MarketDataIngestionResult:
    result = await service.run_tick(as_of=as_of or utc_now())
    logger.info(
        "market_data_ingestion_checked",
        extra={
            "executed": result.executed,
            "reason": result.decision.reason.value,
            "fetched": result.total_fetched,
            "inserted": result.total_inserted,
            "updated": result.total_updated,
            "failed_items": result.failed_item_count,
        },
    )
    return result


async def economic_calendar_ingestion_job(
    service: EconomicCalendarIngestionService,
    *,
    as_of: datetime | None = None,
) -> CalendarIngestionResult:
    result = await service.run_tick(as_of=as_of or utc_now())
    logger.info(
        "economic_calendar_ingestion_checked",
        extra={
            "executed": result.executed,
            "reason": result.decision.reason.value,
            "fetched": result.fetched_count,
            "inserted": result.inserted_count,
            "updated": result.updated_count,
            "failed": result.failed,
        },
    )
    return result


async def forward_outcome_record_job(
    service: ForwardOutcomeService,
    *,
    as_of: datetime | None = None,
) -> ForwardOutcomeRecordResult:
    result = await service.run_record_tick(as_of=as_of or utc_now())
    logger.info(
        "forward_outcome_recording_checked",
        extra={
            "executed": result.executed,
            "reason": result.reason.value,
            "considered": result.considered_count,
            "recorded": result.recorded_count,
            "already_present": result.already_present_count,
            "without_a_plan": result.windows_without_a_plan,
            "without_data": result.windows_without_data,
            "failed_items": result.failed_item_count,
        },
    )
    return result


async def forward_outcome_resolve_job(
    service: ForwardOutcomeService,
    *,
    as_of: datetime | None = None,
) -> ForwardOutcomeResolveResult:
    result = await service.run_resolve_tick(as_of=as_of or utc_now())
    logger.info(
        "forward_outcome_resolution_checked",
        extra={
            "executed": result.executed,
            "reason": result.reason.value,
            "examined": result.examined_count,
            "resolved": result.resolved_count,
            "still_pending": result.still_pending_count,
        },
    )
    return result


async def daily_universe_ingestion_job(
    ingestion_service: MarketDataIngestionService,
    freshness_service: DataFreshnessService,
    instruments: tuple[str, ...],
) -> MarketDataIngestionResult:
    """Fill the daily universe, then check that it actually got filled.

    The two halves are deliberately one job. A fill that reports success on holed data is precisely
    what Phase 9D-1 found by hand after the fact, so the check runs on the same tick and against the
    same clock — a separate schedule could drift until the check was reading a different day's
    state from the fill that produced it.
    """
    result = await ingestion_service.run_tick(as_of=utc_now())
    logger.info(
        "daily_universe_ingestion_checked",
        extra={
            "executed": result.executed,
            "items": len(result.item_results),
            "failed_items": result.failed_item_count,
            "inserted": result.total_inserted,
            "updated": result.total_updated,
        },
    )
    await freshness_service.check(timeframe=Timeframe.D1, instruments=instruments)
    return result


async def interest_rate_ingestion_job(service: InterestRateIngestionService) -> None:
    stored = await service.refresh()
    logger.info("interest_rate_ingestion_checked", extra={"currencies": stored})


def register_jobs(
    scheduler: Any,
    *,
    system_state_service: SystemStateService,
    health_service: HealthService,
    market_data_ingestion_service: MarketDataIngestionService | None = None,
    market_data_ingestion_interval_minutes: int = 15,
    daily_universe_ingestion_service: MarketDataIngestionService | None = None,
    data_freshness_service: DataFreshnessService | None = None,
    daily_universe_instruments: tuple[str, ...] = (),
    daily_universe_hour_utc: int = 2,
    interest_rate_ingestion_service: InterestRateIngestionService | None = None,
    interest_rate_day_of_week: str = "sun",
    interest_rate_hour_utc: int = 3,
    calendar_ingestion_service: EconomicCalendarIngestionService | None = None,
    calendar_ingestion_interval_minutes: int = 60,
    forward_outcome_service: ForwardOutcomeService | None = None,
    forward_outcome_record_interval_minutes: int = 15,
    forward_outcome_resolve_interval_minutes: int = 15,
) -> None:
    scheduler.add_job(
        update_worker_heartbeat_job,
        "interval",
        seconds=30,
        args=[system_state_service],
        id="worker_heartbeat",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        application_health_check_job,
        "interval",
        seconds=60,
        args=[health_service],
        id="application_health_check",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    if market_data_ingestion_service is not None:
        scheduler.add_job(
            market_data_ingestion_job,
            "interval",
            minutes=market_data_ingestion_interval_minutes,
            args=[market_data_ingestion_service],
            id="market_data_ingestion",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    if daily_universe_ingestion_service is not None and data_freshness_service is not None:
        # A cron trigger, not an interval, and this is the one job where that matters. There is no
        # wall-clock gate inside the ingestion service - cadence is owned entirely by the trigger -
        # so a 1440-minute interval on a worker that restarts every day (a deploy, a crash, a
        # laptop closing) could go its whole life without firing once, and the failure would look
        # exactly like nothing happening. Cron fires on the clock regardless of when the process
        # started.
        scheduler.add_job(
            daily_universe_ingestion_job,
            "cron",
            hour=daily_universe_hour_utc,
            minute=0,
            timezone="UTC",
            args=[
                daily_universe_ingestion_service,
                data_freshness_service,
                daily_universe_instruments,
            ],
            id="daily_universe_ingestion",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    if interest_rate_ingestion_service is not None:
        # Rates move a few times a year, so weekly is generous and costs ten requests.
        scheduler.add_job(
            interest_rate_ingestion_job,
            "cron",
            day_of_week=interest_rate_day_of_week,
            hour=interest_rate_hour_utc,
            minute=0,
            timezone="UTC",
            args=[interest_rate_ingestion_service],
            id="interest_rate_ingestion",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    if calendar_ingestion_service is not None:
        scheduler.add_job(
            economic_calendar_ingestion_job,
            "interval",
            minutes=calendar_ingestion_interval_minutes,
            args=[calendar_ingestion_service],
            id="economic_calendar_ingestion",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    if forward_outcome_service is not None:
        # Two jobs, never one. Recording must not be able to see a candle that a resolution in the
        # same call has already read: keeping them apart is what makes "the plan was fixed first"
        # a property of the schedule rather than of a comment.
        scheduler.add_job(
            forward_outcome_record_job,
            "interval",
            minutes=forward_outcome_record_interval_minutes,
            args=[forward_outcome_service],
            id="forward_outcome_recording",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
        scheduler.add_job(
            forward_outcome_resolve_job,
            "interval",
            minutes=forward_outcome_resolve_interval_minutes,
            args=[forward_outcome_service],
            id="forward_outcome_resolution",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
