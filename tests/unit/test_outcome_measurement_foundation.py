from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Candle, Timeframe
from app.domain.entities.outcome import OutcomeKind, OutcomeStatistics, WindowOutcome
from app.domain.entities.signal_contract import SignalDirection, SignalPricePlan
from app.domain.outcome_measurement import aggregate_outcomes, measure_outcome
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)
STEP = timedelta(minutes=15)

ENTRY = Decimal("1.10000")
LONG_PLAN = SignalPricePlan(
    entry_min=Decimal("1.09990"),
    entry_max=Decimal("1.10010"),
    stop_loss=Decimal("1.09800"),
    take_profit_1=Decimal("1.10300"),
)
SHORT_PLAN = SignalPricePlan(
    entry_min=Decimal("1.09990"),
    entry_max=Decimal("1.10010"),
    stop_loss=Decimal("1.10200"),
    take_profit_1=Decimal("1.09700"),
)


def _candle(index: int, *, low: str, high: str) -> Candle:
    open_time = BASE_TIME + (index * STEP)
    return Candle(
        provider="outcome-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + STEP,
        open=Decimal(low),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(high),
        volume=Decimal("100"),
        is_closed=True,
    )


def _quiet(index: int) -> Candle:
    """A candle that touches neither level."""
    return _candle(index, low="1.09950", high="1.10050")


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9a8_second_instrument_foundation"


def test_target_reached_cleanly_is_target_first() -> None:
    forward = [_quiet(0), _quiet(1), _candle(2, low="1.10050", high="1.10350")]

    outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward)

    assert outcome.kind == OutcomeKind.TARGET_FIRST
    assert outcome.bars_to_resolution == 3
    assert outcome.entry_price == ENTRY


def test_protective_level_reached_cleanly_is_stop_first() -> None:
    forward = [_quiet(0), _candle(1, low="1.09750", high="1.09960")]

    outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward)

    assert outcome.kind == OutcomeKind.STOP_FIRST
    assert outcome.bars_to_resolution == 2


def test_a_candle_spanning_both_levels_is_ambiguous_and_counted_against_the_plan() -> None:
    """OHLC records four prices, not their order — so this case is admitted, not guessed."""
    forward = [_candle(0, low="1.09700", high="1.10400")]

    outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward)

    assert outcome.kind == OutcomeKind.AMBIGUOUS
    assert outcome.bars_to_resolution == 1
    assert outcome.conservative_kind == OutcomeKind.STOP_FIRST


def test_neither_level_within_the_horizon_is_timeout() -> None:
    forward = [_quiet(index) for index in range(10)]

    outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward, horizon_candles=5)

    assert outcome.kind == OutcomeKind.TIMEOUT
    assert outcome.bars_to_resolution is None


def test_the_horizon_hides_a_later_resolution() -> None:
    """A hit past the horizon is not a hit: the plan was already out of time."""
    forward = [_quiet(0), _quiet(1), _candle(2, low="1.10050", high="1.10350")]

    outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward, horizon_candles=2)

    assert outcome.kind == OutcomeKind.TIMEOUT


def test_no_forward_candles_is_no_data_not_a_loss() -> None:
    outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, [])

    assert outcome.kind == OutcomeKind.NO_DATA
    assert outcome.bars_to_resolution is None


def test_short_mirrors_long_on_a_mirrored_series() -> None:
    long_forward = [_quiet(0), _candle(1, low="1.10050", high="1.10350")]
    short_forward = [_quiet(0), _candle(1, low="1.09650", high="1.09950")]

    long_outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, long_forward)
    short_outcome = measure_outcome(SignalDirection.SHORT, SHORT_PLAN, short_forward)

    assert long_outcome.kind == short_outcome.kind == OutcomeKind.TARGET_FIRST
    assert long_outcome.bars_to_resolution == short_outcome.bars_to_resolution == 2


def test_short_protective_level_is_above_the_entry() -> None:
    forward = [_candle(0, low="1.10150", high="1.10250")]

    outcome = measure_outcome(SignalDirection.SHORT, SHORT_PLAN, forward)

    assert outcome.kind == OutcomeKind.STOP_FIRST


def test_the_walk_stops_at_the_first_resolution() -> None:
    """A later target does not overwrite an earlier protective hit."""
    forward = [
        _candle(0, low="1.09750", high="1.09960"),
        _candle(1, low="1.10050", high="1.10350"),
    ]

    outcome = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward)

    assert outcome.kind == OutcomeKind.STOP_FIRST
    assert outcome.bars_to_resolution == 1


def test_horizon_must_be_at_least_one_candle() -> None:
    with pytest.raises(ValueError, match="horizon_candles"):
        measure_outcome(SignalDirection.LONG, LONG_PLAN, [_quiet(0)], horizon_candles=0)


def _outcome(kind: OutcomeKind) -> WindowOutcome:
    resolved = kind not in (OutcomeKind.TIMEOUT, OutcomeKind.NO_DATA)
    return WindowOutcome(
        direction=SignalDirection.LONG,
        entry_price=ENTRY,
        stop_loss=LONG_PLAN.stop_loss,
        take_profit=LONG_PLAN.take_profit_1,
        kind=kind,
        bars_to_resolution=2 if resolved else None,
    )


def test_aggregation_counts_every_kind_and_leaves_ambiguity_visible() -> None:
    statistics = aggregate_outcomes(
        [
            _outcome(OutcomeKind.TARGET_FIRST),
            _outcome(OutcomeKind.TARGET_FIRST),
            _outcome(OutcomeKind.STOP_FIRST),
            _outcome(OutcomeKind.AMBIGUOUS),
            _outcome(OutcomeKind.TIMEOUT),
            _outcome(OutcomeKind.NO_DATA),
        ]
    )

    assert statistics.measured_count == 6
    assert statistics.resolved_count == 4
    assert statistics.ambiguous_count == 1
    # Ambiguity sits in the denominator, so it counts against the plan without becoming a loss.
    assert statistics.target_first_share == Decimal("2") / Decimal("4")
    assert statistics.ambiguous_share == Decimal("1") / Decimal("4")
    assert statistics.conservative_stop_first_count == 2
    assert statistics.timeout_share == Decimal("1") / Decimal("6")
    assert statistics.average_bars_to_resolution == Decimal("2")


def test_shares_are_unavailable_rather_than_zero_when_nothing_resolved() -> None:
    """Zero would read as "never reached the target"; there is simply nothing to divide by."""
    statistics = aggregate_outcomes([_outcome(OutcomeKind.TIMEOUT)])

    assert statistics.target_first_share is None
    assert statistics.ambiguous_share is None
    assert statistics.average_bars_to_resolution is None
    assert statistics.timeout_share == Decimal("1")


def test_empty_aggregation_reports_nothing_measured() -> None:
    statistics = aggregate_outcomes([])

    assert statistics.measured_count == 0
    assert statistics.timeout_share is None
    assert statistics.target_first_share is None


def test_an_unresolved_outcome_cannot_claim_a_resolution_bar() -> None:
    with pytest.raises(ValidationError):
        WindowOutcome(
            direction=SignalDirection.LONG,
            entry_price=ENTRY,
            stop_loss=LONG_PLAN.stop_loss,
            take_profit=LONG_PLAN.take_profit_1,
            kind=OutcomeKind.TIMEOUT,
            bars_to_resolution=3,
        )


def test_a_resolved_outcome_must_report_the_bar_that_resolved_it() -> None:
    with pytest.raises(ValidationError):
        WindowOutcome(
            direction=SignalDirection.LONG,
            entry_price=ENTRY,
            stop_loss=LONG_PLAN.stop_loss,
            take_profit=LONG_PLAN.take_profit_1,
            kind=OutcomeKind.TARGET_FIRST,
            bars_to_resolution=None,
        )


def test_statistics_counts_must_add_up() -> None:
    with pytest.raises(ValidationError):
        OutcomeStatistics(measured_count=5, target_first_count=1)
