from datetime import UTC, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair


def _valid_candle(**overrides: object) -> Candle:
    values: dict[str, object] = {
        "provider": "fixture",
        "pair": CurrencyPair(value="EURUSD"),
        "timeframe": Timeframe.M15,
        "open_time": datetime(2026, 7, 3, 10, 0, tzinfo=UTC),
        "close_time": datetime(2026, 7, 3, 10, 15, tzinfo=UTC),
        "open": Decimal("1.1000"),
        "high": Decimal("1.1050"),
        "low": Decimal("1.0950"),
        "close": Decimal("1.1020"),
        "volume": Decimal("100"),
        "is_closed": True,
    }
    values.update(overrides)
    return Candle(**values)


def test_candle_normalizes_provider_timestamp_to_utc() -> None:
    candle = _valid_candle(
        open_time=datetime(2026, 7, 3, 12, 0, tzinfo=ZoneInfo("Europe/Stockholm")),
        close_time=datetime(2026, 7, 3, 12, 15, tzinfo=ZoneInfo("Europe/Stockholm")),
    )

    assert candle.open_time == datetime(2026, 7, 3, 10, 0, tzinfo=UTC)
    assert candle.close_time == datetime(2026, 7, 3, 10, 15, tzinfo=UTC)


@pytest.mark.parametrize(
    "overrides",
    [
        {"open": 1.1},
        {"open_time": datetime(2026, 7, 3, 10, 0)},
        {"close_time": datetime(2026, 7, 3, 9, 59, tzinfo=UTC)},
        {"is_closed": False},
        {"high": Decimal("1.0900")},
        {"low": Decimal("1.1100")},
        {"provider": " "},
        {"volume": Decimal("-1")},
    ],
)
def test_invalid_candle_inputs_are_rejected(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        _valid_candle(**overrides)


def test_economic_event_normalizes_timestamps_and_non_numeric_values() -> None:
    event = EconomicEvent(
        provider="fixture",
        provider_event_id="event-1",
        title="Consumer Price Index",
        currency="EUR",
        country="Sweden",
        impact=EconomicImpact.HIGH,
        scheduled_at=datetime(2026, 7, 3, 12, 0, tzinfo=ZoneInfo("Europe/Stockholm")),
        actual="N/A",
        forecast="2.1",
        previous=Decimal("2.0"),
        fetched_at=datetime(2026, 7, 3, 11, 0, tzinfo=UTC),
    )

    assert event.scheduled_at == datetime(2026, 7, 3, 10, 0, tzinfo=UTC)
    assert event.actual is None
    assert event.actual_raw == "N/A"
    assert event.forecast == Decimal("2.1")
    assert event.forecast_raw is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"currency": "eur"},
        {"scheduled_at": datetime(2026, 7, 3, 10, 0)},
        {"provider": ""},
        {"provider_event_id": " "},
        {"title": " "},
        {"actual": 1.5},
        {"actual": "x" * 201},
        {"actual": Decimal("1000000000000001")},
    ],
)
def test_invalid_economic_event_inputs_are_rejected(overrides: dict[str, object]) -> None:
    values: dict[str, object] = {
        "provider": "fixture",
        "provider_event_id": "event-1",
        "title": "Consumer Price Index",
        "currency": "EUR",
        "country": None,
        "impact": EconomicImpact.MEDIUM,
        "scheduled_at": datetime(2026, 7, 3, 10, 0, tzinfo=UTC),
        "fetched_at": datetime(2026, 7, 3, 9, 0, tzinfo=UTC),
    }
    values.update(overrides)

    with pytest.raises(ValidationError):
        EconomicEvent(**values)
