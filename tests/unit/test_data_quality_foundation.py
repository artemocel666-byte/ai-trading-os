from datetime import UTC, datetime
from decimal import Decimal

from app.domain.entities import (
    Candle,
    DataQualityIssueCode,
    EconomicEvent,
    EconomicImpact,
    Timeframe,
    build_feature_snapshot,
)
from app.domain.replay import HistoricalReplay
from app.domain.value_objects import CurrencyPair


def _candle(open_hour: int, open_minute: int = 0) -> Candle:
    open_time = datetime(2026, 7, 8, open_hour, open_minute, tzinfo=UTC)
    close_time = open_time.replace(minute=open_time.minute + 15)
    return Candle(
        provider="fixture",
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=close_time,
        open=Decimal("1.1000"),
        high=Decimal("1.1050"),
        low=Decimal("1.0950"),
        close=Decimal("1.1020"),
        volume=Decimal("100"),
        is_closed=True,
    )


def _event(scheduled_at: datetime, currency: str = "EUR") -> EconomicEvent:
    return EconomicEvent(
        provider="fixture",
        provider_event_id=f"{currency}-{scheduled_at.isoformat()}",
        title="Consumer Price Index",
        currency=currency,
        country="Eurozone",
        impact=EconomicImpact.HIGH,
        scheduled_at=scheduled_at,
        actual=Decimal("2.2"),
        forecast=Decimal("2.1"),
        previous=Decimal("2.0"),
        fetched_at=datetime(2026, 7, 8, 7, 0, tzinfo=UTC),
    )


def test_feature_snapshot_reports_complete_market_data_window() -> None:
    snapshot = build_feature_snapshot(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        window_end=datetime(2026, 7, 8, 8, 30, tzinfo=UTC),
        candles=[_candle(8, 0), _candle(8, 15)],
        economic_events=[_event(datetime(2026, 7, 8, 8, 10, tzinfo=UTC))],
    )

    assert snapshot.market_data_complete is True
    assert snapshot.candle_availability.expected_count == 2
    assert snapshot.candle_availability.observed_count == 2
    assert snapshot.economic_event_availability.event_count == 1
    assert snapshot.economic_event_availability.currencies == ("EUR",)
    assert snapshot.quality_issues == ()


def test_feature_snapshot_reports_missing_duplicate_and_out_of_range_data() -> None:
    outside = _candle(9, 0)
    duplicate = _candle(8, 0)

    snapshot = build_feature_snapshot(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        window_end=datetime(2026, 7, 8, 8, 45, tzinfo=UTC),
        candles=[_candle(8, 0), duplicate, outside],
        economic_events=[_event(datetime(2026, 7, 8, 9, 0, tzinfo=UTC))],
    )

    issue_codes = [issue.code for issue in snapshot.quality_issues]
    assert snapshot.market_data_complete is False
    assert DataQualityIssueCode.DUPLICATE_CANDLE in issue_codes
    assert DataQualityIssueCode.MISSING_CANDLE in issue_codes
    assert DataQualityIssueCode.CANDLE_OUT_OF_RANGE in issue_codes
    assert DataQualityIssueCode.EVENT_OUT_OF_RANGE in issue_codes


def test_historical_replay_frame_is_deterministic_and_cutoff_based() -> None:
    replay = HistoricalReplay(
        candles=[_candle(8, 0), _candle(8, 15)],
        economic_events=[
            _event(datetime(2026, 7, 8, 8, 5, tzinfo=UTC)),
            _event(datetime(2026, 7, 8, 8, 25, tzinfo=UTC), currency="USD"),
        ],
    )

    frame = replay.frame(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        window_end=datetime(2026, 7, 8, 8, 30, tzinfo=UTC),
        as_of=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
        currencies=["EUR"],
    )

    assert len(frame.candles) == 1
    assert frame.candles[0].open_time == datetime(2026, 7, 8, 8, 0, tzinfo=UTC)
    assert len(frame.economic_events) == 1
    assert frame.economic_events[0].currency == "EUR"
    assert frame.feature_snapshot.market_data_complete is False
