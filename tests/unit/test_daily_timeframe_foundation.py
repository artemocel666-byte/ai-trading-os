from datetime import UTC, datetime, timedelta

import httpx
import pytest
from pydantic import ValidationError

from app.adapters.twelve_data import TIMEFRAME_TO_DELTA as ADAPTER_TIMEFRAME_TO_DELTA
from app.adapters.twelve_data import TIMEFRAME_TO_INTERVAL, TwelveDataMarketDataAdapter
from app.core import constants
from app.core.exceptions import ProviderInvalidPayloadError
from app.domain.currency_universe import (
    QUOTE_PRECEDENCE,
    UNIVERSE_CURRENCIES,
    universe_pairs,
)
from app.domain.entities import Candle, Timeframe
from app.domain.entities.backfill import BackfillChunkResult
from app.domain.entities.data_quality import (
    TIMEFRAME_TO_DELTA,
    TRADED_DAYS_ONLY_TIMEFRAMES,
    DataQualityIssueCode,
    build_feature_snapshot,
    expected_open_times,
    is_window_aligned,
)
from app.domain.value_objects import CurrencyPair
from scripts.backfill_market_data import coverage_shortfalls

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


def _adapter() -> TwelveDataMarketDataAdapter:
    """`_parse_candles` is pure — no request is made, so the client is never touched."""
    return TwelveDataMarketDataAdapter(
        client=httpx.AsyncClient(),
        api_key="unused",
        base_url="https://example.invalid",
        timeout=httpx.Timeout(1.0),
        retry_count=0,
        retry_backoff_seconds=0.0,
        max_request_range=timedelta(days=90),
    )


def _rows(count: int, *, impossible: int = 0) -> list[dict[str, str]]:
    """Daily rows, some with a close sitting outside the bar's own range — as seen in the wild."""
    rows: list[dict[str, str]] = []
    for index in range(count):
        day = (datetime(2020, 1, 1, tzinfo=UTC) + timedelta(days=index)).strftime("%Y-%m-%d")
        if index < impossible:
            rows.append(
                {"datetime": day, "open": "0.9", "high": "0.91", "low": "0.89", "close": "0.88"}
            )
        else:
            rows.append(
                {"datetime": day, "open": "0.9", "high": "0.91", "low": "0.88", "close": "0.89"}
            )
    return rows


def _parse(rows: list[dict[str, str]]) -> list[Candle]:
    return _adapter()._parse_candles(
        {"values": rows},
        PAIR,
        Timeframe.D1,
        datetime(2019, 12, 31, tzinfo=UTC),
        datetime(2020, 6, 1, tzinfo=UTC),
    )


def test_one_impossible_row_does_not_destroy_the_response() -> None:
    """The defect that cost Phase 9D-1 a day and left multi-year holes in most of the universe.

    The provider emits occasional daily bars whose low sits a few units of the eighth decimal above
    the close. `Candle` is right to refuse them — a close outside its own day's range is not a
    price. Refusing the *whole* payload for it threw away seven hundred good bars at a time.
    """
    candles = _parse(_rows(20, impossible=1))

    assert len(candles) == 19
    # Skipped, never repaired: widening the low to admit the close would edit an observation.
    assert all(candle.low <= candle.close for candle in candles)
    assert datetime(2020, 1, 1, tzinfo=UTC) not in {candle.open_time for candle in candles}


def test_the_worst_quality_pair_observed_is_still_accepted() -> None:
    """EURSEK loses 5.5% of its days this way against EURGBP's 1.3%, both measured live.

    A series that lossy is worth noting — and it is a series, not a broken feed. Refusing it would
    delete nineteen years of a currency from the universe over an eighteenth of its rows.
    """
    assert len(_parse(_rows(100, impossible=6))) == 94


def test_a_mostly_impossible_payload_is_still_refused() -> None:
    """Tolerating row by row without a ceiling would turn the guard into decoration."""
    with pytest.raises(ProviderInvalidPayloadError):
        _parse(_rows(20, impossible=6))


def test_a_clean_payload_keeps_every_row() -> None:
    assert len(_parse(_rows(20))) == 20


def test_a_failed_chunk_says_why_it_failed() -> None:
    """A whole day was spent guessing this from the shape of the holes.

    The service caught every exception and recorded `failed=True` and nothing else, so a fill that
    came back with five-year gaps could report *that* something broke and never *what*.
    """
    chunk = BackfillChunkResult(
        chunk_start=FRIDAY,
        chunk_end=TUESDAY,
        failed=True,
        failure_reason="ProviderRateLimitError",
    )

    assert chunk.failure_reason == "ProviderRateLimitError"


def test_a_chunk_that_worked_cannot_carry_a_failure_reason() -> None:
    with pytest.raises(ValidationError):
        BackfillChunkResult(
            chunk_start=FRIDAY, chunk_end=TUESDAY, fetched_count=5, failure_reason="whatever"
        )


def test_coverage_is_judged_against_the_sample_rather_than_an_absolute() -> None:
    """The check 9D-1 lacked, and the reason it is relative.

    The right number of bars depends on an instrument's real history, which the fill cannot know.
    What it can know is whether one member of the universe came back with far less than the rest —
    and a cross-section over instruments silently absent in some years is the bias that
    manufactures a finding.
    """
    median, short = coverage_shortfalls(
        [("EURUSD", 5000), ("GBPUSD", 4950), ("AUDCAD", 3700), ("USDJPY", 5010)]
    )

    # Four values, so the median is the lower of the two middles — the same nearest-rank habit the
    # rest of the project keeps, and a value the sample actually contained.
    assert median == 4950
    assert short == [("AUDCAD", 3700)]


def test_a_universe_that_agrees_with_itself_reports_no_shortfall() -> None:
    median, short = coverage_shortfalls([("EURUSD", 5000), ("GBPUSD", 4800), ("USDJPY", 4900)])

    assert median == 4900
    assert short == []


def test_one_missing_chunk_of_seven_is_caught() -> None:
    """Why the tolerance is a tenth: a single lost chunk costs about a seventh."""
    _, short = coverage_shortfalls([("A", 700), ("B", 700), ("C", 700), ("D", 600)])

    assert short == [("D", 600)]


def test_coverage_says_nothing_when_nothing_was_fetched() -> None:
    assert coverage_shortfalls([]) == (0, [])
    assert coverage_shortfalls([("EURUSD", 0), ("GBPUSD", 0)]) == (0, [])


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
