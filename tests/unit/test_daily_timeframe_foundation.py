from datetime import UTC, datetime, timedelta

import pytest

from app.adapters.twelve_data import TIMEFRAME_TO_DELTA as ADAPTER_TIMEFRAME_TO_DELTA
from app.adapters.twelve_data import TIMEFRAME_TO_INTERVAL
from app.core import constants
from app.domain.currency_universe import (
    QUOTE_PRECEDENCE,
    UNIVERSE_CURRENCIES,
    universe_pairs,
)
from app.domain.entities import Candle, Timeframe
from app.domain.entities.data_quality import (
    TIMEFRAME_TO_DELTA,
    TRADED_DAYS_ONLY_TIMEFRAMES,
    DataQualityIssueCode,
    build_feature_snapshot,
    expected_open_times,
    is_window_aligned,
)
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")

#: Friday 2026-08-07 through Tuesday 2026-08-11: five calendar days holding three traded ones.
FRIDAY = datetime(2026, 8, 7, tzinfo=UTC)
SATURDAY = datetime(2026, 8, 8, tzinfo=UTC)
SUNDAY = datetime(2026, 8, 9, tzinfo=UTC)
MONDAY = datetime(2026, 8, 10, tzinfo=UTC)
TUESDAY = datetime(2026, 8, 11, tzinfo=UTC)


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9d1_daily_bars_and_universe"


def _daily_candle(open_time: datetime) -> Candle:
    return Candle(
        provider="daily-test",
        pair=PAIR,
        timeframe=Timeframe.D1,
        open_time=open_time,
        close_time=open_time + timedelta(days=1),
        open="1.10000",
        high="1.10500",
        low="1.09500",
        close="1.10200",
        volume="1000",
        is_closed=True,
    )


def test_a_daily_window_expects_traded_days_only() -> None:
    """The defect this phase exists to prevent.

    Provider daily bars arrive on weekdays and only erratically at weekends — measured against the
    live provider, EURUSD had 58 Saturdays and USDJPY 84 over the same 142 weeks. Expecting a
    weekend bar would report a gap most weeks, and a different gap per instrument.
    """
    expected = expected_open_times(
        timeframe=Timeframe.D1, window_start=FRIDAY, window_end=TUESDAY + timedelta(days=1)
    )

    assert expected == (FRIDAY, MONDAY, TUESDAY)


def test_an_intraday_window_still_expects_every_slot() -> None:
    """M15 and H1 must not move. The provider returns a continuous 24/7 series there, filler and
    all, and the weekend is excluded later at analysis time rather than never expected."""
    expected = expected_open_times(
        timeframe=Timeframe.H1, window_start=SATURDAY, window_end=SATURDAY + timedelta(hours=3)
    )

    assert len(expected) == 3
    assert Timeframe.H1 not in TRADED_DAYS_ONLY_TIMEFRAMES
    assert Timeframe.M15 not in TRADED_DAYS_ONLY_TIMEFRAMES


def test_a_daily_window_spanning_a_weekend_is_complete_not_gapped() -> None:
    """The end-to-end version of the same thing, through the real snapshot builder."""
    snapshot = build_feature_snapshot(
        pair=PAIR,
        timeframe=Timeframe.D1,
        window_start=FRIDAY,
        window_end=TUESDAY + timedelta(days=1),
        candles=[_daily_candle(FRIDAY), _daily_candle(MONDAY), _daily_candle(TUESDAY)],
    )

    codes = {issue.code for issue in snapshot.quality_issues}
    assert DataQualityIssueCode.MISSING_CANDLE not in codes
    assert DataQualityIssueCode.WINDOW_NOT_ALIGNED not in codes
    assert snapshot.candle_availability.missing_count == 0


def test_a_weekend_daily_bar_the_provider_sent_is_not_treated_as_missing() -> None:
    """Extra weekend bars are stored because the provider sent them, and cost nothing here.

    They are surplus rather than absent, so they raise no missing-candle issue; the analysis path
    excludes them through `is_market_open`, the same way it excludes intraday weekend filler.
    """
    snapshot = build_feature_snapshot(
        pair=PAIR,
        timeframe=Timeframe.D1,
        window_start=FRIDAY,
        window_end=TUESDAY + timedelta(days=1),
        candles=[
            _daily_candle(FRIDAY),
            _daily_candle(SATURDAY),
            _daily_candle(SUNDAY),
            _daily_candle(MONDAY),
            _daily_candle(TUESDAY),
        ],
    )

    codes = {issue.code for issue in snapshot.quality_issues}
    assert DataQualityIssueCode.MISSING_CANDLE not in codes
    assert snapshot.candle_availability.missing_count == 0


def test_alignment_asks_about_the_window_not_about_the_candles_inside_it() -> None:
    """Why alignment had to stop being inferred from the expected-times count.

    That identity — start plus count times delta equals end — holds only while every slot produces
    a bar. A daily window skipping a weekend breaks it, and would have been reported ragged.
    """
    assert is_window_aligned(
        timeframe=Timeframe.D1, window_start=FRIDAY, window_end=TUESDAY + timedelta(days=1)
    )
    assert not is_window_aligned(
        timeframe=Timeframe.D1,
        window_start=FRIDAY,
        window_end=TUESDAY + timedelta(days=1, hours=7),
    )


def test_a_timeframe_cannot_be_half_added() -> None:
    """The defect that actually happened while building this phase, now asserted.

    `D1` went into the enum and the domain delta map, and the adapter kept a third private copy of
    both. Every daily request was refused *before* the network call, so a live backfill reported
    forty-five pairs as "not quoted by the provider" — a wrong answer that looked like a real one.
    """
    for timeframe in Timeframe:
        assert timeframe in TIMEFRAME_TO_DELTA, timeframe
        assert timeframe in TIMEFRAME_TO_INTERVAL, timeframe
    assert TIMEFRAME_TO_DELTA is ADAPTER_TIMEFRAME_TO_DELTA


def test_pairs_are_written_the_way_the_market_quotes_them() -> None:
    written = {pair.value for pair in universe_pairs()}

    for expected in ("EURUSD", "USDJPY", "GBPUSD", "USDCHF", "NOKSEK", "CHFJPY", "USDCAD"):
        assert expected in written
    for inverted in ("USDEUR", "JPYUSD", "SEKNOK", "CADUSD"):
        assert inverted not in written


def test_the_universe_is_derived_from_currencies_rather_than_listed() -> None:
    """A listed pair could be added or dropped later to suit a result; a derived one cannot."""
    count = len(UNIVERSE_CURRENCIES)

    assert len(universe_pairs()) == count * (count - 1) // 2
    assert universe_pairs() == universe_pairs()


def test_a_smaller_universe_still_quotes_in_precedence_order() -> None:
    pairs = universe_pairs(frozenset({"USD", "JPY", "EUR"}))

    assert [pair.value for pair in pairs] == ["EURUSD", "EURJPY", "USDJPY"]


def test_a_currency_with_no_quoting_convention_is_refused() -> None:
    with pytest.raises(ValueError, match="precedence"):
        universe_pairs(frozenset({"USD", "XYZ"}))


def test_every_universe_currency_has_a_precedence() -> None:
    assert frozenset(QUOTE_PRECEDENCE) == UNIVERSE_CURRENCIES
    assert len(QUOTE_PRECEDENCE) == len(set(QUOTE_PRECEDENCE))
