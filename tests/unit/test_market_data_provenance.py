"""Provenance is the only thing separating an observation from an invention.

The `provider` column records who supplied a row. Seed and verification scripts write under their
own names, so the check needs no heuristic on the values — which matters, because the values
themselves looked entirely plausible: the seed candles found on 2026-08-07 were well-formed OHLC
with sane highs and lows. They were simply four hundred pips from where the market actually was.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.adapters import fmp_calendar, twelve_data
from app.core.constants import REAL_MARKET_DATA_PROVIDERS
from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.entities.market_data import EconomicImpact
from app.domain.value_objects import CurrencyPair
from scripts.replay_rules import synthetic_providers

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 8, 5, 8, 0, tzinfo=UTC)


def _candle(provider: str, index: int = 0) -> Candle:
    open_time = BASE_TIME + (index * timedelta(minutes=15))
    return Candle(
        provider=provider,
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=Decimal("1.10000"),
        high=Decimal("1.10030"),
        low=Decimal("1.09970"),
        close=Decimal("1.10010"),
        volume=Decimal("100"),
        is_closed=True,
    )


def _event(provider: str) -> EconomicEvent:
    return EconomicEvent(
        provider=provider,
        provider_event_id=f"{provider}-1",
        scheduled_at=BASE_TIME,
        currency="EUR",
        title="Test",
        impact=EconomicImpact.HIGH,
        fetched_at=BASE_TIME,
    )


def test_the_real_provider_set_matches_the_adapters_that_exist() -> None:
    """A new market-data adapter must be added here, or its rows read as fabricated.

    Failing that way round is the safe one: an unknown provider is refused rather than trusted.
    """
    assert twelve_data.PROVIDER_NAME in REAL_MARKET_DATA_PROVIDERS
    assert fmp_calendar.PROVIDER_NAME in REAL_MARKET_DATA_PROVIDERS
    assert {twelve_data.PROVIDER_NAME, fmp_calendar.PROVIDER_NAME} == REAL_MARKET_DATA_PROVIDERS


def test_real_rows_are_reported_as_clean() -> None:
    candles = [_candle(twelve_data.PROVIDER_NAME, index) for index in range(3)]

    assert synthetic_providers(candles, [_event(fmp_calendar.PROVIDER_NAME)]) == {}


def test_fabricated_rows_are_counted_by_provider() -> None:
    candles = [
        _candle(twelve_data.PROVIDER_NAME, 0),
        _candle("local-seed", 1),
        _candle("local-seed", 2),
        _candle("phase7a-proof", 3),
    ]

    assert synthetic_providers(candles, [_event("phase7b-proof")]) == {
        "local-seed": 2,
        "phase7a-proof": 1,
        "phase7b-proof": 1,
    }


def test_a_well_formed_invention_is_still_an_invention() -> None:
    """The seed candles were valid OHLC. Nothing about the values gave them away."""
    plausible = _candle("local-seed")

    assert plausible.high >= plausible.low
    assert synthetic_providers([plausible], []) == {"local-seed": 1}
