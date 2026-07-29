from collections.abc import Callable, Sequence
from datetime import datetime, timedelta

from app.core.exceptions import ApplicationError, ErrorCode, ProviderError
from app.core.time import normalize_to_utc
from app.domain.entities.calendar_ingestion import (
    CalendarIngestionConfig,
    CalendarIngestionDecision,
    CalendarIngestionDecisionReason,
    CalendarIngestionResult,
    CalendarIngestionTick,
)
from app.domain.entities.market_data import EconomicEvent
from app.domain.interfaces.providers import EconomicCalendarProvider
from app.domain.interfaces.unit_of_work import UnitOfWork
from app.services.system_state_service import SystemStateService

UnitOfWorkFactory = Callable[[], UnitOfWork]

CALENDAR_INGESTION_COMPONENT = "economic_calendar_ingestion"


class EconomicCalendarIngestionService:
    """Fetches scheduled economic events from the calendar provider and stores them.

    Unlike candle ingestion the window straddles the tick: it reaches back over recent events
    and forward over announced ones, because calendars are published ahead of time. Storing a
    future scheduled event is not lookahead bias; deciding what an analysis window may read is
    a separate concern owned by the snapshot layer.

    This never produces trading output: no directions, no price levels, no scoring, no AI calls,
    and no user-facing messages.
    """

    def __init__(
        self,
        *,
        config: CalendarIngestionConfig,
        provider: EconomicCalendarProvider,
        uow_factory: UnitOfWorkFactory,
        system_state_service: SystemStateService,
    ) -> None:
        self._config = config
        self._provider = provider
        self._uow_factory = uow_factory
        self._system_state_service = system_state_service

    async def run_tick(self, *, as_of: datetime) -> CalendarIngestionResult:
        tick = CalendarIngestionTick(as_of=as_of)
        decision = self._decide(tick)
        if not decision.should_fetch:
            return _skipped_result(tick=tick, decision=decision)

        window_start, window_end = calendar_ingestion_window(
            as_of=tick.as_of,
            lookback_hours=self._config.lookback_hours,
            horizon_hours=self._config.horizon_hours,
        )
        try:
            events = await self._provider.get_events(
                window_start,
                window_end,
                list(self._config.currencies),
            )
            inserted, updated = await self._store_events(events)
        except Exception as error:
            await self._record_failure(error)
            return CalendarIngestionResult(
                tick=tick,
                decision=decision,
                executed=True,
                skipped=False,
                succeeded=False,
                failed=True,
                window_start=window_start,
                window_end=window_end,
            )

        await self._system_state_service.record_integration_health("calendar")
        # An empty response is a normal outcome, not a failure: quiet calendar days exist, and a
        # fully up-to-date window legitimately returns nothing new.
        return CalendarIngestionResult(
            tick=tick,
            decision=decision,
            executed=True,
            skipped=False,
            succeeded=True,
            failed=False,
            window_start=window_start,
            window_end=window_end,
            fetched_count=len(events),
            inserted_count=inserted,
            updated_count=updated,
        )

    async def _store_events(self, events: Sequence[EconomicEvent]) -> tuple[int, int]:
        if not events:
            return (0, 0)
        async with self._uow_factory() as uow:
            result = await uow.economic_events.upsert_many(list(events))
            await uow.commit()
        return (result.inserted, result.updated)

    async def _record_failure(self, error: Exception) -> None:
        application_error = (
            error
            if isinstance(error, ApplicationError)
            else ProviderError(
                ErrorCode.PROVIDER_UNAVAILABLE,
                "Загрузка экономического календаря не удалась.",
                details={"currencies": ",".join(self._config.currencies)},
            )
        )
        await self._system_state_service.record_system_error(
            application_error,
            component=CALENDAR_INGESTION_COMPONENT,
            technical_details=f"{type(error).__name__}: {error}",
        )

    def _decide(self, tick: CalendarIngestionTick) -> CalendarIngestionDecision:
        if not self._config.enabled:
            return _decision(
                config=self._config,
                tick=tick,
                reason=CalendarIngestionDecisionReason.DISABLED,
                should_fetch=False,
            )
        if not self._config.currencies:
            return _decision(
                config=self._config,
                tick=tick,
                reason=CalendarIngestionDecisionReason.NO_CURRENCIES,
                should_fetch=False,
            )
        return _decision(
            config=self._config,
            tick=tick,
            reason=CalendarIngestionDecisionReason.COMPLETED,
            should_fetch=True,
        )


def calendar_ingestion_window(
    *,
    as_of: datetime,
    lookback_hours: int,
    horizon_hours: int,
) -> tuple[datetime, datetime]:
    """Return the window that straddles the tick: recent events plus announced ones."""
    if lookback_hours < 1 or horizon_hours < 1:
        raise ValueError("calendar ingestion lookback and horizon must be at least one hour")
    as_of_utc = normalize_to_utc(as_of)
    return (
        as_of_utc - timedelta(hours=lookback_hours),
        as_of_utc + timedelta(hours=horizon_hours),
    )


def _decision(
    *,
    config: CalendarIngestionConfig,
    tick: CalendarIngestionTick,
    reason: CalendarIngestionDecisionReason,
    should_fetch: bool,
) -> CalendarIngestionDecision:
    return CalendarIngestionDecision(
        enabled=config.enabled,
        should_fetch=should_fetch,
        reason=reason,
        currency_count=len(config.currencies),
        tick_as_of=tick.as_of,
    )


def _skipped_result(
    *,
    tick: CalendarIngestionTick,
    decision: CalendarIngestionDecision,
) -> CalendarIngestionResult:
    return CalendarIngestionResult(
        tick=tick,
        decision=decision,
        executed=False,
        skipped=True,
    )
