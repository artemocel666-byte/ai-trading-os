from collections.abc import Sequence
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.domain.context_engine import MarketContextEngine
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.context import ContextIssueCode, MarketContextSnapshot
from app.domain.value_objects import CurrencyPair
from app.services.context_service import ContextService

PAIR = CurrencyPair(value="EURUSD")
OTHER_PAIR = CurrencyPair(value="GBPUSD")
START = datetime(2026, 7, 8, 8, 0, tzinfo=UTC)


def _candle(
    index: int,
    *,
    provider: str = "unit",
    pair: CurrencyPair = PAIR,
    timeframe: Timeframe = Timeframe.M15,
    open_value: str = "100",
    high: str = "110",
    low: str = "95",
    close: str = "105",
    volume: str | None = "10",
) -> Candle:
    open_time = START + timedelta(minutes=15 * index)
    return Candle(
        provider=provider,
        pair=pair,
        timeframe=timeframe,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=Decimal(open_value),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=Decimal(volume) if volume is not None else None,
        is_closed=True,
    )


def _event(
    minutes: int,
    *,
    currency: str = "EUR",
    impact: EconomicImpact = EconomicImpact.HIGH,
    provider_event_id: str = "event",
) -> EconomicEvent:
    return EconomicEvent(
        provider="unit",
        provider_event_id=provider_event_id,
        title="Consumer Price Index",
        currency=currency,
        country="Eurozone",
        impact=impact,
        scheduled_at=START + timedelta(minutes=minutes),
        actual=Decimal("2.2"),
        forecast=Decimal("2.1"),
        previous=Decimal("2.0"),
        fetched_at=START,
    )


def _engine() -> MarketContextEngine:
    return MarketContextEngine()


def _issue_codes(snapshot: MarketContextSnapshot) -> set[ContextIssueCode]:
    return {issue.code for issue in snapshot.context_issues}


def test_context_engine_calculates_exact_decimal_context() -> None:
    candles = [
        _candle(2, open_value="90", high="100", low="89", close="99"),
        _candle(0, open_value="100", high="112", low="99", close="110"),
        _candle(1, open_value="80", high="90", low="79", close="88"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=candles,
        moving_average_windows=(2, 3),
    )

    assert snapshot.quality_ok is True
    assert snapshot.return_distribution.close_values == (
        Decimal("110"),
        Decimal("88"),
        Decimal("99"),
    )
    assert snapshot.return_distribution.close_change_values == (
        Decimal("-22"),
        Decimal("11"),
    )
    assert snapshot.return_distribution.per_candle_returns == (
        Decimal("0.1"),
        Decimal("0.1"),
        Decimal("0.1"),
    )
    assert snapshot.return_distribution.cumulative_return == Decimal("-0.1")
    assert snapshot.return_distribution.mean_return == Decimal("0.1")
    assert snapshot.return_distribution.median_return == Decimal("0.1")
    assert snapshot.return_distribution.min_return == Decimal("0.1")
    assert snapshot.return_distribution.max_return == Decimal("0.1")
    assert snapshot.return_distribution.return_standard_deviation == Decimal("0")
    assert snapshot.return_distribution.realized_volatility == Decimal("0")
    assert snapshot.return_distribution.max_close_to_close_drawdown == Decimal("0.2")


def test_context_models_normalize_times_to_utc() -> None:
    stockholm = timezone(timedelta(hours=2))
    candle = _candle(0).model_copy(
        update={
            "open_time": datetime(2026, 7, 8, 10, 0, tzinfo=stockholm),
            "close_time": datetime(2026, 7, 8, 10, 15, tzinfo=stockholm),
        }
    )

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 10, 0, tzinfo=stockholm),
        window_end=datetime(2026, 7, 8, 10, 15, tzinfo=stockholm),
        as_of=datetime(2026, 7, 8, 10, 15, tzinfo=stockholm),
        candles=[candle],
        moving_average_windows=(1,),
    )

    assert snapshot.window.window_start == START
    assert snapshot.window.window_end == START + timedelta(minutes=15)
    assert snapshot.window.as_of == START + timedelta(minutes=15)


def test_context_engine_excludes_items_after_as_of() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1), _candle(2)],
        economic_events=[
            _event(20, provider_event_id="included"),
            _event(40, provider_event_id="later"),
        ],
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert snapshot.event_context.used_event_count == 1
    assert ContextIssueCode.CANDLE_AFTER_AS_OF in _issue_codes(snapshot)
    assert ContextIssueCode.EVENT_AFTER_AS_OF in _issue_codes(snapshot)


def test_context_engine_reports_duplicate_candles() -> None:
    duplicate = _candle(0, provider="duplicate")

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), duplicate, _candle(1)],
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert ContextIssueCode.DUPLICATE_CANDLE in _issue_codes(snapshot)
    assert snapshot.quality_ok is False


def test_context_engine_reports_missing_candle_gaps() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=[_candle(0), _candle(2)],
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert ContextIssueCode.MISSING_CANDLE in _issue_codes(snapshot)
    assert snapshot.quality_ok is False


def test_context_engine_reports_mismatched_pair_and_timeframe() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[
            _candle(0, pair=OTHER_PAIR),
            _candle(0, timeframe=Timeframe.H1),
        ],
        moving_average_windows=(1,),
    )

    assert snapshot.time_context.candle_count == 0
    assert ContextIssueCode.CANDLE_PAIR_MISMATCH in _issue_codes(snapshot)
    assert ContextIssueCode.CANDLE_TIMEFRAME_MISMATCH in _issue_codes(snapshot)
    assert ContextIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_context_engine_requires_closed_candles_only() -> None:
    open_candle = _candle(0).model_copy(update={"is_closed": False})

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[open_candle],
        moving_average_windows=(1,),
    )

    assert snapshot.time_context.candle_count == 0
    assert ContextIssueCode.CANDLE_NOT_CLOSED in _issue_codes(snapshot)
    assert ContextIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_context_engine_handles_empty_and_small_input_without_fake_values() -> None:
    empty = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[],
        moving_average_windows=(3,),
    )

    assert empty.return_distribution.close_values == ()
    assert empty.return_distribution.cumulative_return is None
    assert empty.return_distribution.return_standard_deviation is None
    assert empty.range_context.average_true_range is None
    assert empty.candle_shape.average_body_size is None
    assert ContextIssueCode.NO_CANDLES in _issue_codes(empty)

    small = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1)],
        moving_average_windows=(3,),
    )
    assert small.moving_average_summary.close_mean_series[0].values == ()
    assert ContextIssueCode.INSUFFICIENT_CANDLES in _issue_codes(small)


def test_context_engine_calculates_moving_averages() -> None:
    candles = [
        _candle(0, open_value="100", high="101", low="99", close="100"),
        _candle(1, open_value="100", high="111", low="99", close="110"),
        _candle(2, open_value="100", high="121", low="99", close="120"),
        _candle(3, open_value="100", high="131", low="99", close="130"),
        _candle(4, open_value="100", high="141", low="99", close="140"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=75),
        as_of=START + timedelta(minutes=75),
        candles=candles,
        moving_average_windows=(3, 5),
    )

    assert snapshot.moving_average_summary.close_mean_series[0].values == (
        Decimal("110"),
        Decimal("120"),
        Decimal("130"),
    )
    assert snapshot.moving_average_summary.close_mean_series[1].values == (Decimal("120"),)
    assert snapshot.moving_average_summary.return_mean_series[0].values == (
        Decimal("0.1"),
        Decimal("0.2"),
        Decimal("0.3"),
    )


def test_context_engine_calculates_range_and_shape_values() -> None:
    candles = [
        _candle(0, open_value="100", high="110", low="95", close="105"),
        _candle(1, open_value="105", high="112", low="104", close="110"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=candles,
        moving_average_windows=(2,),
    )

    assert snapshot.range_context.true_range_values == (Decimal("15"), Decimal("8"))
    assert snapshot.range_context.average_true_range == Decimal("11.5")
    assert snapshot.range_context.candle_range_values == (Decimal("15"), Decimal("8"))
    assert snapshot.range_context.range_change_ratios == (None, Decimal("-7") / Decimal("15"))
    assert snapshot.candle_shape.body_sizes == (Decimal("5"), Decimal("5"))
    assert snapshot.candle_shape.upper_wick_sizes == (Decimal("5"), Decimal("2"))
    assert snapshot.candle_shape.lower_wick_sizes == (Decimal("5"), Decimal("1"))
    assert snapshot.candle_shape.average_upper_wick_size == Decimal("3.5")
    assert snapshot.candle_shape.average_lower_wick_size == Decimal("3")
    assert snapshot.candle_shape.body_to_range_ratios == (
        Decimal("1") / Decimal("3"),
        Decimal("5") / Decimal("8"),
    )
    assert snapshot.candle_shape.close_location_in_range_values == (
        Decimal("2") / Decimal("3"),
        Decimal("3") / Decimal("4"),
    )


def test_context_engine_calculates_event_context() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1), _candle(2)],
        economic_events=[
            _event(5, currency="EUR", impact=EconomicImpact.HIGH, provider_event_id="1"),
            _event(20, currency="USD", impact=EconomicImpact.LOW, provider_event_id="2"),
            _event(40, currency="EUR", impact=EconomicImpact.MEDIUM, provider_event_id="3"),
        ],
        moving_average_windows=(2,),
    )

    assert snapshot.event_context.input_event_count == 3
    assert snapshot.event_context.used_event_count == 2
    assert [(item.impact, item.count) for item in snapshot.event_context.counts_by_impact] == [
        (EconomicImpact.HIGH, 1),
        (EconomicImpact.LOW, 1),
    ]
    assert [(item.currency, item.count) for item in snapshot.event_context.counts_by_currency] == [
        ("EUR", 1),
        ("USD", 1),
    ]
    assert snapshot.event_context.latest_event_time == START + timedelta(minutes=20)
    assert snapshot.event_context.minutes_since_latest_event == Decimal("10")
    assert ContextIssueCode.EVENT_AFTER_AS_OF in _issue_codes(snapshot)


def test_context_models_are_immutable() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[_candle(0)],
        moving_average_windows=(1,),
    )

    with pytest.raises(ValidationError):
        snapshot.return_distribution.close_values = (Decimal("999"),)


class _ContextCandleRepository:
    def __init__(self, candles: Sequence[Candle]) -> None:
        self.candles = list(candles)
        self.calls: list[dict[str, object]] = []

    async def list_range(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
        provider: str | None = None,
    ) -> list[Candle]:
        self.calls.append(
            {
                "pair": pair,
                "timeframe": timeframe,
                "start_at": start_at,
                "end_at": end_at,
                "provider": provider,
            }
        )
        return list(self.candles)


class _ContextEventRepository:
    def __init__(self, events: Sequence[EconomicEvent]) -> None:
        self.events = list(events)
        self.calls: list[dict[str, object]] = []

    async def list_window(
        self,
        *,
        start_at: datetime,
        end_at: datetime,
        currencies: list[str] | None = None,
        provider: str | None = None,
    ) -> list[EconomicEvent]:
        self.calls.append(
            {
                "start_at": start_at,
                "end_at": end_at,
                "currencies": currencies,
                "provider": provider,
            }
        )
        return list(self.events)


class _ContextRepositories:
    def __init__(
        self,
        candle_repository: _ContextCandleRepository,
        event_repository: _ContextEventRepository,
    ) -> None:
        self.candles = candle_repository
        self.economic_events = event_repository


@asynccontextmanager
async def _context_repositories(
    candle_repository: _ContextCandleRepository,
    event_repository: _ContextEventRepository,
):
    yield _ContextRepositories(candle_repository, event_repository)


class _ContextUnitOfWorkFactory:
    def __init__(
        self,
        candle_repository: _ContextCandleRepository,
        event_repository: _ContextEventRepository,
    ) -> None:
        self._candle_repository = candle_repository
        self._event_repository = event_repository

    def __call__(self):
        return _context_repositories(self._candle_repository, self._event_repository)


@pytest.mark.asyncio
async def test_context_service_reads_repositories_and_builds_snapshot() -> None:
    candle_repository = _ContextCandleRepository([_candle(0), _candle(1)])
    event_repository = _ContextEventRepository([_event(5, provider_event_id="service")])
    service = ContextService(_ContextUnitOfWorkFactory(candle_repository, event_repository))

    snapshot = await service.build_market_context(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        provider="unit",
        moving_average_windows=(2,),
    )

    assert snapshot.time_context.candle_count == 2
    assert snapshot.event_context.used_event_count == 1
    assert candle_repository.calls[0]["pair"] == PAIR
    assert candle_repository.calls[0]["provider"] == "unit"
    assert event_repository.calls[0]["currencies"] == ["EUR", "USD"]
    assert event_repository.calls[0]["provider"] == "unit"
