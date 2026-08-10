import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncEngine

from app.adapters.factories import (
    ProviderClients,
    create_economic_calendar_provider,
    create_market_data_provider,
    create_provider_clients,
)
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.domain.entities import (
    CalendarIngestionConfig,
    ForwardOutcomeConfig,
    MarketDataIngestionConfig,
    SnapshotScheduleItem,
    Timeframe,
)
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.database_health import SqlAlchemyDatabaseHealth
from app.persistence.session import build_uow_factory
from app.scheduler.jobs import register_jobs, update_worker_heartbeat_job
from app.services.economic_calendar_ingestion_service import EconomicCalendarIngestionService
from app.services.forward_outcome_service import ForwardOutcomeService
from app.services.health_service import HealthService
from app.services.market_data_ingestion_service import MarketDataIngestionService
from app.services.system_state_service import SystemStateService

DEFAULT_INGESTION_PAIR = "EURUSD"

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    configure_logging("worker", settings.log_level)
    engine: AsyncEngine = create_engine(settings.database_dsn())
    session_factory = create_session_factory(engine)
    uow_factory = build_uow_factory(session_factory)
    system_state_service = SystemStateService(uow_factory)
    health_service = HealthService(
        settings=settings,
        database_health=SqlAlchemyDatabaseHealth(engine),
        system_state_service=system_state_service,
    )

    market_data_wanted = settings.market_data_enabled and settings.market_data_ingestion_enabled
    calendar_wanted = settings.calendar_enabled and settings.calendar_ingestion_enabled

    provider_clients: ProviderClients | None = None
    ingestion_service: MarketDataIngestionService | None = None
    calendar_ingestion_service: EconomicCalendarIngestionService | None = None
    if market_data_wanted or calendar_wanted:
        provider_clients = create_provider_clients(settings)
    if market_data_wanted and provider_clients is not None:
        ingestion_service = MarketDataIngestionService(
            config=_build_ingestion_config(settings),
            provider=create_market_data_provider(
                settings,
                client=provider_clients.market_data,
            ),
            uow_factory=uow_factory,
            system_state_service=system_state_service,
        )
        logger.info("market_data_ingestion_enabled")
    if calendar_wanted and provider_clients is not None:
        calendar_ingestion_service = EconomicCalendarIngestionService(
            config=_build_calendar_ingestion_config(settings),
            provider=create_economic_calendar_provider(
                settings,
                client=provider_clients.economic_calendar,
            ),
            uow_factory=uow_factory,
            system_state_service=system_state_service,
        )
        logger.info("calendar_ingestion_enabled")

    forward_outcome_service: ForwardOutcomeService | None = None
    if settings.forward_outcome_recording_enabled:
        # No provider client: the ledger reads stored candles only, and never fetches. If ingestion
        # is off it simply finds nothing, which is the honest failure mode.
        forward_outcome_service = ForwardOutcomeService(
            config=_build_forward_outcome_config(settings),
            uow_factory=uow_factory,
            system_state_service=system_state_service,
        )
        logger.info("forward_outcome_recording_enabled")

    scheduler = AsyncIOScheduler(timezone=settings.app_timezone)
    register_jobs(
        scheduler,
        system_state_service=system_state_service,
        health_service=health_service,
        market_data_ingestion_service=ingestion_service,
        market_data_ingestion_interval_minutes=settings.market_data_ingestion_interval_minutes,
        calendar_ingestion_service=calendar_ingestion_service,
        calendar_ingestion_interval_minutes=settings.calendar_ingestion_interval_minutes,
        forward_outcome_service=forward_outcome_service,
        forward_outcome_record_interval_minutes=(settings.forward_outcome_record_interval_minutes),
        forward_outcome_resolve_interval_minutes=(
            settings.forward_outcome_resolve_interval_minutes
        ),
    )

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        logger.info("worker_starting")
        await update_worker_heartbeat_job(system_state_service)
        scheduler.start()
        logger.info("worker_started")
        await stop_event.wait()
    finally:
        logger.info("worker_stopping")
        scheduler.shutdown(wait=False)
        if provider_clients is not None:
            await provider_clients.aclose()
        await engine.dispose()
        logger.info("worker_stopped")


def _build_ingestion_config(settings: Settings) -> MarketDataIngestionConfig:
    pair = CurrencyPair(value=DEFAULT_INGESTION_PAIR)
    lookback = settings.market_data_ingestion_lookback_candles
    return MarketDataIngestionConfig(
        enabled=True,
        interval_minutes=settings.market_data_ingestion_interval_minutes,
        lookback_candles=lookback,
        items=(
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.M15,
                lookback_candle_count=lookback,
            ),
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.H1,
                lookback_candle_count=lookback,
            ),
        ),
    )


def _build_forward_outcome_config(settings: Settings) -> ForwardOutcomeConfig:
    """The same two series the worker already ingests.

    Deliberately not a wider list. The ledger can only record windows the database actually holds,
    and pointing it at a pair nobody ingests would fill it with incomplete windows that say more
    about ingestion than about the market.
    """
    pair = CurrencyPair(value=DEFAULT_INGESTION_PAIR)
    window_candles = settings.forward_outcome_window_candles
    return ForwardOutcomeConfig(
        enabled=True,
        record_interval_minutes=settings.forward_outcome_record_interval_minutes,
        resolve_interval_minutes=settings.forward_outcome_resolve_interval_minutes,
        window_candles=window_candles,
        horizon_candles=settings.forward_outcome_horizon_candles,
        resolve_batch_size=settings.forward_outcome_resolve_batch_size,
        items=(
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.M15,
                lookback_candle_count=window_candles,
            ),
            SnapshotScheduleItem(
                pair=pair,
                timeframe=Timeframe.H1,
                lookback_candle_count=window_candles,
            ),
        ),
    )


def _build_calendar_ingestion_config(settings: Settings) -> CalendarIngestionConfig:
    pair = CurrencyPair(value=DEFAULT_INGESTION_PAIR)
    return CalendarIngestionConfig(
        enabled=True,
        interval_minutes=settings.calendar_ingestion_interval_minutes,
        lookback_hours=settings.calendar_ingestion_lookback_hours,
        horizon_hours=settings.calendar_ingestion_horizon_hours,
        currencies=(pair.base_currency, pair.quote_currency),
    )


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
