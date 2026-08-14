from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Candle, Timeframe
from app.domain.entities.execution_cost import (
    FINDING_EQUIVALENT_POINTS,
    CostPoint,
    CostReading,
    CostReadingStatus,
    CostSensitivityProfile,
)
from app.domain.entities.outcome import OutcomeKind, OutcomeStatistics, WindowOutcome
from app.domain.entities.signal_contract import SignalDirection, SignalPricePlan
from app.domain.execution_cost import break_even_share, build_cost_sensitivity_profile
from app.domain.outcome_measurement import measure_outcome
from app.domain.value_objects import CurrencyPair
from scripts.profile_execution_cost import _atr_spread

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)
STEP = timedelta(minutes=15)

#: One pip on a five-decimal quote, the cost the pre-registered grid centres on.
ONE_PIP = Decimal("0.00010")

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


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9c5_window_width_measurement"


def _candle(index: int, *, low: str, high: str) -> Candle:
    open_time = BASE_TIME + (index * STEP)
    return Candle(
        provider="execution-cost-test",
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


def _outcome(kind: OutcomeKind, direction: SignalDirection) -> WindowOutcome:
    resolved = kind not in (OutcomeKind.TIMEOUT, OutcomeKind.NO_DATA)
    return WindowOutcome(
        direction=direction,
        entry_price=Decimal("1.10000"),
        stop_loss=Decimal("1.09800"),
        take_profit=Decimal("1.10300"),
        kind=kind,
        bars_to_resolution=2 if resolved else None,
    )


def _statistics(*, target: int, stop: int, timeout: int = 0) -> OutcomeStatistics:
    return OutcomeStatistics(
        measured_count=target + stop + timeout,
        target_first_count=target,
        stop_first_count=stop,
        timeout_count=timeout,
    )


def _profile(*points: tuple[str, int], break_even: str = "0.5") -> CostSensitivityProfile:
    """`points` are (cost, target-first count) over a thousand resolved windows apiece."""
    return CostSensitivityProfile(
        pair="EURUSD",
        timeframe="M15",
        break_even_share=Decimal(break_even),
        points=tuple(
            CostPoint(
                cost=Decimal(cost),
                statistics=_statistics(target=target, stop=1000 - target),
            )
            for cost, target in points
        ),
    )


def test_a_cost_of_zero_measures_exactly_what_the_gross_run_measured() -> None:
    """Every published figure must survive the parameter being added under it."""
    forward = [_candle(0, low="1.10050", high="1.10350")]

    gross = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward)
    explicit = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward, cost=Decimal("0"))

    assert gross == explicit
    assert gross.kind == OutcomeKind.TARGET_FIRST


def test_a_cost_moves_a_long_target_out_of_reach() -> None:
    forward = [_candle(0, low="1.10050", high="1.10300")]

    assert (
        measure_outcome(SignalDirection.LONG, LONG_PLAN, forward).kind == OutcomeKind.TARGET_FIRST
    )
    under_cost = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward, cost=ONE_PIP)

    assert under_cost.kind == OutcomeKind.TIMEOUT


def test_a_cost_brings_a_long_protective_level_within_reach() -> None:
    """The half of the effect that is easy to forget: the stop moves too, and it moves closer."""
    forward = [_candle(0, low="1.09805", high="1.09950")]

    assert measure_outcome(SignalDirection.LONG, LONG_PLAN, forward).kind == OutcomeKind.TIMEOUT
    under_cost = measure_outcome(SignalDirection.LONG, LONG_PLAN, forward, cost=ONE_PIP)

    assert under_cost.kind == OutcomeKind.STOP_FIRST


def test_the_shift_is_mirrored_for_a_short() -> None:
    """A cost handicaps both directions, so pooling them cannot hide it in one of the two."""
    forward = [_candle(0, low="1.10050", high="1.10195")]

    assert measure_outcome(SignalDirection.SHORT, SHORT_PLAN, forward).kind == OutcomeKind.TIMEOUT
    under_cost = measure_outcome(SignalDirection.SHORT, SHORT_PLAN, forward, cost=ONE_PIP)

    assert under_cost.kind == OutcomeKind.STOP_FIRST


def test_cost_leaves_the_distance_between_the_levels_alone() -> None:
    """The property the whole formulation rests on.

    Cost moves the pair against the position rather than squeezing it, so a win still pays what it
    paid and a loss still costs what it cost. Only the odds of reaching either one change — which
    is why a cost-adjusted share stays comparable to every gross share the project has published,
    break-even included.
    """
    forward = [_candle(0, low="1.09950", high="1.10050")]

    for direction, plan in ((SignalDirection.LONG, LONG_PLAN), (SignalDirection.SHORT, SHORT_PLAN)):
        gross = measure_outcome(direction, plan, forward)
        charged = measure_outcome(direction, plan, forward, cost=ONE_PIP)

        assert charged.take_profit - charged.stop_loss == gross.take_profit - gross.stop_loss
        assert charged.entry_price == gross.entry_price


def test_a_negative_cost_is_refused() -> None:
    """A rebate is not modelled, and allowing one would let a caller improve a result by fiat."""
    with pytest.raises(ValueError, match="negative"):
        measure_outcome(
            SignalDirection.LONG,
            LONG_PLAN,
            [_candle(0, low="1.09950", high="1.10050")],
            cost=Decimal("-0.00010"),
        )


def test_a_cost_that_would_drive_a_level_to_zero_is_refused() -> None:
    with pytest.raises(ValueError, match="zero"):
        measure_outcome(
            SignalDirection.SHORT,
            SHORT_PLAN,
            [_candle(0, low="1.09950", high="1.10050")],
            cost=Decimal("2.0"),
        )


def test_break_even_share_is_risk_over_the_whole_span() -> None:
    """3/7 for the Phase 9A multipliers, which is where 42.86% in every report comes from."""
    assert break_even_share(Decimal("1.5"), Decimal("2.0")) == Decimal(3) / Decimal(7)
    assert break_even_share(Decimal("1"), Decimal("1")) == Decimal("0.5")


def test_break_even_share_refuses_a_distance_that_is_not_positive() -> None:
    with pytest.raises(ValueError, match="positive"):
        break_even_share(Decimal("0"), Decimal("2.0"))


def test_the_curve_interpolates_the_cost_at_which_a_share_crosses() -> None:
    profile = _profile(("0", 500), ("0.00010", 400), break_even="0.45")

    reading = profile.break_even_cost

    assert reading.status == CostReadingStatus.FOUND
    assert reading.cost == Decimal("0.00005")


def test_a_plan_already_below_break_even_names_that_rather_than_extrapolating() -> None:
    """The expected reading for this project, and the one a bare `None` would have blurred.

    Pooled gross is 41.42% against a break-even of 42.86%. There is no positive cost that causes
    that, and an interpolated negative number would invent a cause.
    """
    profile = _profile(("0", 480), ("0.00010", 400))

    reading = profile.break_even_cost

    assert reading.status == CostReadingStatus.ALREADY_BELOW_AT_ZERO
    assert reading.cost is None


def test_a_curve_that_never_falls_far_enough_says_so_rather_than_guessing() -> None:
    profile = _profile(("0", 500), ("0.00010", 480), break_even="0.30")

    assert profile.break_even_cost.status == CostReadingStatus.BEYOND_THE_GRID


def test_a_point_that_resolved_nothing_makes_the_reading_unavailable() -> None:
    profile = CostSensitivityProfile(
        pair="EURUSD",
        timeframe="M15",
        break_even_share=Decimal("0.45"),
        points=(
            CostPoint(cost=Decimal("0"), statistics=_statistics(target=500, stop=500)),
            CostPoint(cost=ONE_PIP, statistics=_statistics(target=0, stop=0, timeout=1000)),
        ),
    )

    assert profile.break_even_cost.status == CostReadingStatus.UNAVAILABLE


def test_the_finding_equivalent_cost_is_read_against_the_project_bar() -> None:
    """Five points is what 9C-2 and 9C-3 required of a field. This says what that is worth."""
    assert Decimal("0.05") == FINDING_EQUIVALENT_POINTS
    profile = _profile(("0", 500), ("0.00020", 400))

    reading = profile.finding_equivalent_cost

    assert reading.status == CostReadingStatus.FOUND
    assert reading.cost == Decimal("0.00010")


def test_a_loss_of_share_must_be_positive_to_be_located() -> None:
    with pytest.raises(ValueError, match="positive"):
        _profile(("0", 500), ("0.00010", 400)).cost_for_loss_of(Decimal("0"))


def test_a_reading_cannot_claim_a_cost_it_did_not_find() -> None:
    with pytest.raises(ValidationError):
        CostReading(status=CostReadingStatus.BEYOND_THE_GRID, cost=Decimal("0.00010"))
    with pytest.raises(ValidationError):
        CostReading(status=CostReadingStatus.FOUND)


def test_a_curve_must_start_from_a_free_measurement() -> None:
    """Without a zero-cost point every difference would be relative to a handicapped sample."""
    with pytest.raises(ValidationError):
        _profile(("0.00002", 500), ("0.00010", 400))


def test_cost_points_must_be_strictly_ascending() -> None:
    with pytest.raises(ValidationError):
        _profile(("0", 500), ("0.00010", 400), ("0.00005", 380))
    with pytest.raises(ValidationError):
        _profile(("0", 500), ("0.00010", 400), ("0.00010", 380))


def test_a_curve_needs_something_to_compare_the_free_point_against() -> None:
    with pytest.raises(ValidationError):
        _profile(("0", 500))


def test_every_point_must_cover_the_same_windows() -> None:
    """Points measured over different populations compare samples, not costs."""
    with pytest.raises(ValidationError):
        CostSensitivityProfile(
            pair="EURUSD",
            timeframe="M15",
            break_even_share=Decimal("0.45"),
            points=(
                CostPoint(cost=Decimal("0"), statistics=_statistics(target=500, stop=500)),
                CostPoint(cost=ONE_PIP, statistics=_statistics(target=400, stop=500)),
            ),
        )


def test_the_atr_spread_reports_values_the_sample_actually_held() -> None:
    """Nearest-rank, shared with `rule_calibration`: an interpolated quartile was never observed."""
    spread = _atr_spread([Decimal(value) for value in (4, 1, 3, 2)])

    assert spread is not None
    assert (spread.lower, spread.median, spread.upper) == (Decimal(1), Decimal(2), Decimal(3))


def test_the_relative_spread_is_what_makes_two_window_widths_comparable() -> None:
    """The Phase 9C-5 plumbing check: a wider window must visibly steady the ATR estimate."""
    jumpy = _atr_spread([Decimal(value) for value in (1, 2, 4, 8)])
    steady = _atr_spread([Decimal(value) for value in (3, 4, 4, 5)])

    assert jumpy is not None
    assert steady is not None
    assert jumpy.relative_spread > steady.relative_spread
    assert _atr_spread([]) is None


def test_the_builder_orders_the_curve_and_takes_break_even_from_the_geometry() -> None:
    charged = [_outcome(OutcomeKind.STOP_FIRST, direction) for direction in SignalDirection]
    free = [_outcome(OutcomeKind.TARGET_FIRST, direction) for direction in SignalDirection]

    profile = build_cost_sensitivity_profile(
        [(ONE_PIP, charged), (Decimal("0"), free)],
        pair="EURUSD",
        timeframe="M15",
        stop=Decimal("1.5"),
        target=Decimal("2.0"),
    )

    assert [point.cost for point in profile.points] == [Decimal("0"), ONE_PIP]
    assert profile.break_even_share == Decimal(3) / Decimal(7)
    assert profile.zero_cost_share == Decimal("1")
