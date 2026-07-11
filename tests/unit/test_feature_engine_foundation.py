from collections.abc import Sequence
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from types import TracebackType
from typing import Self

import pytest
from pydantic import ValidationError

from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.features import FeatureIssueCode, MarketFeatureSnapshot
from app.domain.feature_engine import MarketFeatureEngine
from app.domain.value_objects import CurrencyPair
from app.services.feature_service import FeatureService

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


def _engine() -> MarketFeatureEngine:
    return MarketFeatureEngine()


def _issue_codes(snapshot: MarketFeatureSnapshot) -> set[FeatureIssueCode]:
    return {issue.code for issue in snapshot.quality_issues}


def test_feature_engine_calculates_exact_deterministic_decimal_features() -> None:
    candles = [
        _candle(2, open_value="110", high="115", low="108", close="112", volume=None),
        _candle(0, open_value="100", high="110", low="95", close="105", volume="10"),
        _candle(1, open_value="105", high="112", low="104", close="110", volume="20"),
    ]

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=candles,
        rolling_window_size=2,
    )

    summary = snapshot.candle_summary
    assert snapshot.quality_ok is True
    assert summary.expected_candle_count == 3
    assert summary.input_candle_count == 3
    assert summary.used_candle_count == 3
    assert summary.latest_close == Decimal("112")
    assert summary.latest_candle_close_time == START + timedelta(minutes=45)
    assert summary.simple_return == Decimal("0.12")
    assert summary.per_candle_returns == (
        Decimal("0.05"),
        Decimal("5") / Decimal("105"),
        Decimal("2") / Decimal("110"),
    )
    assert summary.rolling_close_mean_window == 2
    assert summary.rolling_close_means == (Decimal("107.5"), Decimal("111"))
    assert summary.rolling_high_low_ranges == (Decimal("17"), Decimal("11"))
    assert summary.average_candle_range == Decimal("10")
    assert summary.average_body_size == Decimal("4")
    assert summary.volume_observed_count == 2
    assert summary.volume_sum == Decimal("30")
    assert summary.volume_average == Decimal("15")
    assert summary.true_ranges == (Decimal("15"), Decimal("8"), Decimal("7"))
    assert summary.average_true_range == Decimal("10")
    assert summary.market_data_complete is True


def test_feature_models_normalize_datetimes_to_utc() -> None:
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
        rolling_window_size=1,
    )

    assert snapshot.window.window_start == START
    assert snapshot.window.window_end == START + timedelta(minutes=15)
    assert snapshot.window.as_of == START + timedelta(minutes=15)


def test_feature_engine_excludes_future_candles_and_events_after_as_of() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1), _candle(2)],
        economic_events=[
            _event(20, provider_event_id="included"),
            _event(40, provider_event_id="future"),
        ],
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert snapshot.economic_event_summary.used_event_count == 1
    assert FeatureIssueCode.CANDLE_AFTER_AS_OF in _issue_codes(snapshot)
    assert FeatureIssueCode.EVENT_AFTER_AS_OF in _issue_codes(snapshot)


def test_feature_engine_reports_duplicate_candles_without_weakening_upsert_semantics() -> None:
    duplicate = _candle(0, provider="duplicate")

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), duplicate, _candle(1)],
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert FeatureIssueCode.DUPLICATE_CANDLE in _issue_codes(snapshot)
    assert snapshot.candle_summary.market_data_complete is False


def test_feature_engine_reports_missing_candle_gaps() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=45),
        as_of=START + timedelta(minutes=45),
        candles=[_candle(0), _candle(2)],
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert FeatureIssueCode.MISSING_CANDLE in _issue_codes(snapshot)
    assert snapshot.candle_summary.market_data_complete is False


def test_feature_engine_reports_mismatched_pair_and_timeframe() -> None:
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
        rolling_window_size=1,
    )

    assert snapshot.candle_summary.used_candle_count == 0
    assert FeatureIssueCode.CANDLE_PAIR_MISMATCH in _issue_codes(snapshot)
    assert FeatureIssueCode.CANDLE_TIMEFRAME_MISMATCH in _issue_codes(snapshot)
    assert FeatureIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_feature_engine_requires_closed_candles_only() -> None:
    open_candle = _candle(0).model_copy(update={"is_closed": False})

    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[open_candle],
        rolling_window_size=1,
    )

    assert snapshot.candle_summary.used_candle_count == 0
    assert FeatureIssueCode.CANDLE_NOT_CLOSED in _issue_codes(snapshot)
    assert FeatureIssueCode.NO_CANDLES in _issue_codes(snapshot)


def test_feature_engine_counts_economic_events_by_impact_and_currency() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1)],
        economic_events=[
            _event(5, currency="EUR", impact=EconomicImpact.HIGH, provider_event_id="1"),
            _event(10, currency="USD", impact=EconomicImpact.LOW, provider_event_id="2"),
            _event(20, currency="EUR", impact=EconomicImpact.HIGH, provider_event_id="3"),
            _event(35, currency="EUR", impact=EconomicImpact.MEDIUM, provider_event_id="4"),
        ],
        rolling_window_size=2,
    )

    assert [
        (item.impact, item.count) for item in snapshot.economic_event_summary.counts_by_impact
    ] == [
        (EconomicImpact.HIGH, 2),
        (EconomicImpact.LOW, 1),
    ]
    assert [
        (item.currency, item.count) for item in snapshot.economic_event_summary.counts_by_currency
    ] == [("EUR", 2), ("USD", 1)]
    assert snapshot.economic_event_summary.input_event_count == 4
    assert snapshot.economic_event_summary.used_event_count == 3
    assert FeatureIssueCode.EVENT_OUT_OF_RANGE in _issue_codes(snapshot)


def test_feature_engine_handles_empty_and_insufficient_data_without_fake_values() -> None:
    empty = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[],
        rolling_window_size=3,
    )
    assert empty.candle_summary.latest_close is None
    assert empty.candle_summary.simple_return is None
    assert empty.candle_summary.per_candle_returns == ()
    assert empty.candle_summary.rolling_close_means == ()
    assert FeatureIssueCode.NO_CANDLES in _issue_codes(empty)

    insufficient = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        candles=[_candle(0), _candle(1)],
        rolling_window_size=3,
    )
    assert insufficient.candle_summary.rolling_close_means == ()
    assert FeatureIssueCode.INSUFFICIENT_CANDLES in _issue_codes(insufficient)


def test_feature_snapshot_models_are_immutable() -> None:
    snapshot = _engine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=15),
        as_of=START + timedelta(minutes=15),
        candles=[_candle(0)],
        rolling_window_size=1,
    )

    with pytest.raises(ValidationError):
        snapshot.candle_summary.latest_close = Decimal("999")


class _FakeCandleRepository:
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


class _FakeEconomicEventRepository:
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


class _FakeFeatureUnitOfWork:
    def __init__(
        self,
        candle_repository: _FakeCandleRepository,
        event_repository: _FakeEconomicEventRepository,
    ) -> None:
        self.candles = candle_repository
        self.economic_events = event_repository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class _FakeFeatureUnitOfWorkFactory:
    def __init__(
        self,
        candle_repository: _FakeCandleRepository,
        event_repository: _FakeEconomicEventRepository,
    ) -> None:
        self._candle_repository = candle_repository
        self._event_repository = event_repository

    def __call__(self) -> _FakeFeatureUnitOfWork:
        return _FakeFeatureUnitOfWork(self._candle_repository, self._event_repository)


@pytest.mark.asyncio
async def test_feature_service_reads_repositories_and_builds_snapshot() -> None:
    candles = [_candle(0), _candle(1)]
    events = [_event(5, currency="EUR", provider_event_id="service")]
    candle_repository = _FakeCandleRepository(candles)
    event_repository = _FakeEconomicEventRepository(events)
    service = FeatureService(_FakeFeatureUnitOfWorkFactory(candle_repository, event_repository))

    snapshot = await service.build_market_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=START,
        window_end=START + timedelta(minutes=30),
        as_of=START + timedelta(minutes=30),
        provider="unit",
        rolling_window_size=2,
    )

    assert snapshot.candle_summary.used_candle_count == 2
    assert snapshot.economic_event_summary.used_event_count == 1
    assert candle_repository.calls[0]["pair"] == PAIR
    assert candle_repository.calls[0]["provider"] == "unit"
    assert event_repository.calls[0]["currencies"] == ["EUR", "USD"]
    assert event_repository.calls[0]["provider"] == "unit"
