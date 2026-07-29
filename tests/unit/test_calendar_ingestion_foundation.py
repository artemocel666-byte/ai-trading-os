from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core import constants
from app.domain.entities import EconomicEvent, EconomicImpact
from app.domain.entities.calendar_ingestion import (
    CalendarIngestionConfig,
    CalendarIngestionDecisionReason,
)
from app.services.economic_calendar_ingestion_service import (
    EconomicCalendarIngestionService,
    calendar_ingestion_window,
)
from app.services.system_state_service import SystemStateService
from tests.fakes import FakeUnitOfWorkFactory

AS_OF = datetime(2026, 7, 28, 12, 0, tzinfo=UTC)


class FakeCalendarProvider:
    def __init__(
        self,
        *,
        events: list[EconomicEvent] | None = None,
        failing: bool = False,
    ) -> None:
        self._events = events or []
        self._failing = failing
        self.calls: list[tuple[datetime, datetime, Sequence[str] | None]] = []

    async def get_events(
        self,
        start_at: datetime,
        end_at: datetime,
        currencies: Sequence[str] | None = None,
    ) -> Sequence[EconomicEvent]:
        self.calls.append((start_at, end_at, currencies))
        if self._failing:
            raise RuntimeError("calendar provider unavailable")
        return self._events


def _event(offset_hours: int, *, currency: str = "EUR") -> EconomicEvent:
    scheduled_at = AS_OF + timedelta(hours=offset_hours)
    return EconomicEvent(
        provider="calendar-test",
        provider_event_id=f"{currency}-{scheduled_at.isoformat()}",
        title="Consumer Price Index",
        currency=currency,
        country=None,
        impact=EconomicImpact.HIGH,
        scheduled_at=scheduled_at,
        actual=Decimal("2.2"),
        forecast=Decimal("2.1"),
        previous=Decimal("2.0"),
        fetched_at=AS_OF,
    )


def _config(
    *,
    enabled: bool = True,
    currencies: tuple[str, ...] = ("EUR", "USD"),
) -> CalendarIngestionConfig:
    return CalendarIngestionConfig(
        enabled=enabled,
        interval_minutes=60,
        lookback_hours=24,
        horizon_hours=72,
        currencies=currencies,
    )


def _service(
    *,
    config: CalendarIngestionConfig,
    provider: FakeCalendarProvider,
    factory: FakeUnitOfWorkFactory,
) -> EconomicCalendarIngestionService:
    return EconomicCalendarIngestionService(
        config=config,
        provider=provider,
        uow_factory=factory,
        system_state_service=SystemStateService(factory),
    )


@pytest.mark.asyncio
async def test_disabled_calendar_ingestion_skips_without_calling_provider() -> None:
    provider = FakeCalendarProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(enabled=False), provider=provider, factory=factory)

    result = await service.run_tick(as_of=AS_OF)

    assert result.skipped is True
    assert result.decision.reason == CalendarIngestionDecisionReason.DISABLED
    assert provider.calls == []


@pytest.mark.asyncio
async def test_calendar_ingestion_without_currencies_skips() -> None:
    provider = FakeCalendarProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(currencies=()), provider=provider, factory=factory)

    result = await service.run_tick(as_of=AS_OF)

    assert result.skipped is True
    assert result.decision.reason == CalendarIngestionDecisionReason.NO_CURRENCIES
    assert provider.calls == []


@pytest.mark.asyncio
async def test_tick_fetches_and_stores_events() -> None:
    provider = FakeCalendarProvider(events=[_event(-2), _event(6), _event(30)])
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(), provider=provider, factory=factory)

    result = await service.run_tick(as_of=AS_OF)

    assert result.executed is True
    assert result.succeeded is True
    assert result.failed is False
    assert result.fetched_count == 3
    assert result.inserted_count == 3
    assert len(factory.events) == 3
    assert constants.SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH in factory.state


@pytest.mark.asyncio
async def test_window_straddles_the_tick() -> None:
    """Calendars are published ahead, so the stored window must reach into the future."""
    provider = FakeCalendarProvider()
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(), provider=provider, factory=factory)

    result = await service.run_tick(as_of=AS_OF)

    start_at, end_at, currencies = provider.calls[0]
    assert start_at < AS_OF < end_at
    assert AS_OF - start_at == timedelta(hours=24)
    assert end_at - AS_OF == timedelta(hours=72)
    assert list(currencies or []) == ["EUR", "USD"]
    assert result.window_start == start_at
    assert result.window_end == end_at


@pytest.mark.asyncio
async def test_empty_response_is_success_not_failure() -> None:
    # Quiet calendar days exist, exactly as weekends do for candles.
    provider = FakeCalendarProvider(events=[])
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(), provider=provider, factory=factory)

    result = await service.run_tick(as_of=AS_OF)

    assert result.succeeded is True
    assert result.failed is False
    assert result.fetched_count == 0
    assert factory.events == []
    assert constants.SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH in factory.state


@pytest.mark.asyncio
async def test_provider_failure_is_recorded_and_not_raised() -> None:
    provider = FakeCalendarProvider(failing=True)
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(), provider=provider, factory=factory)

    result = await service.run_tick(as_of=AS_OF)

    assert result.executed is True
    assert result.failed is True
    assert result.succeeded is False
    assert result.fetched_count == 0
    assert constants.SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH not in factory.state
    assert constants.SYSTEM_STATE_LAST_ERROR in factory.state


@pytest.mark.asyncio
async def test_tick_fetches_at_any_wall_clock_moment() -> None:
    """Regression guard carried over from the Phase 7A defect: no clock-alignment gate here."""
    provider = FakeCalendarProvider(events=[_event(1)])
    factory = FakeUnitOfWorkFactory()
    service = _service(config=_config(), provider=provider, factory=factory)

    ragged = AS_OF + timedelta(minutes=7, seconds=41, microseconds=3421)
    result = await service.run_tick(as_of=ragged)

    assert result.executed is True
    assert result.succeeded is True
    assert len(provider.calls) == 1


def test_calendar_ingestion_window_rejects_non_positive_bounds() -> None:
    with pytest.raises(ValueError, match="at least one hour"):
        calendar_ingestion_window(as_of=AS_OF, lookback_hours=0, horizon_hours=72)
    with pytest.raises(ValueError, match="at least one hour"):
        calendar_ingestion_window(as_of=AS_OF, lookback_hours=24, horizon_hours=0)


def test_no_wall_clock_gate_remains_in_the_service() -> None:
    import app.services.economic_calendar_ingestion_service as module

    assert not hasattr(module, "is_calendar_ingestion_due")
    assert "NOT_DUE" not in {reason.value for reason in CalendarIngestionDecisionReason}
