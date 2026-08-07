from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.analysis_engine import AnalysisEngine
from app.domain.direction_candidate import DEFAULT_MINIMUM_EFFICIENCY, propose_direction
from app.domain.direction_evaluation import WindowProposal, evaluate_direction
from app.domain.entities import Candle, Timeframe
from app.domain.entities.direction_evaluation import DirectionEvaluation
from app.domain.entities.outcome import OutcomeKind, WindowOutcome
from app.domain.entities.pipeline_decision import PipelineDecisionStatus
from app.domain.entities.signal_contract import SignalDirection
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.strategy_field_resolver import resolve_field
from app.domain.value_objects import CurrencyPair

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 20, 8, 0, tzinfo=UTC)
STEP = timedelta(minutes=15)


def _snapshot(closes: list[Decimal]):
    """Build a window from an explicit close path, so each test states its own shape."""
    candles = []
    previous = closes[0]
    for index, close in enumerate(closes):
        open_price = previous
        candles.append(
            Candle(
                provider="direction-test",
                pair=PAIR,
                timeframe=Timeframe.M15,
                open_time=BASE_TIME + (index * STEP),
                close_time=BASE_TIME + ((index + 1) * STEP),
                open=open_price,
                high=max(open_price, close) + Decimal("0.00020"),
                low=min(open_price, close) - Decimal("0.00020"),
                close=close,
                volume=Decimal("100"),
                is_closed=True,
            )
        )
        previous = close
    as_of = BASE_TIME + (len(closes) * STEP)
    return AnalysisEngine().build_snapshot(
        pair=PAIR,
        timeframe=Timeframe.M15,
        window_start=BASE_TIME,
        window_end=as_of,
        as_of=as_of,
        candles=candles,
        economic_events=[],
        moving_average_windows=(3,),
    )


def _straight(tick: Decimal, count: int = 12) -> list[Decimal]:
    return [Decimal("1.10000") + (tick * (index + 1)) for index in range(count)]


def _sawtooth(tick: Decimal, count: int = 12) -> list[Decimal]:
    """Same distance travelled as a straight line, ending exactly where it began."""
    return [
        Decimal("1.10000") + (tick if index % 2 == 0 else Decimal("0")) for index in range(count)
    ]


def test_project_phase_is_current() -> None:
    assert constants.PROJECT_PHASE == "phase_9a6_clean_calibration_foundation"


def test_a_straight_climb_proposes_short() -> None:
    """Against the move, not with it — the direction the in-sample sweep selected."""
    assert propose_direction(_snapshot(_straight(Decimal("0.00020")))) == SignalDirection.SHORT


def test_the_mirror_proposes_long() -> None:
    assert propose_direction(_snapshot(_straight(Decimal("-0.00020")))) == SignalDirection.LONG


def test_a_sawtooth_abstains_despite_travelling_just_as_far() -> None:
    """The whole point of the candidate: distance is not direction.

    This window moves exactly as much as the straight climb above and ends where it started. A rule
    keyed on volatility could not tell them apart; this one must.
    """
    snapshot = _snapshot(_sawtooth(Decimal("0.00020")))

    assert propose_direction(snapshot) is None


def test_a_window_below_the_threshold_abstains() -> None:
    # Two steps up for every one down: real drift, but well short of a straight line.
    closes = []
    price = Decimal("1.10000")
    for index in range(12):
        price += Decimal("0.00020") if index % 3 else Decimal("-0.00030")
        closes.append(price)
    snapshot = _snapshot(closes)
    efficiency = resolve_field("market_context.move_efficiency", snapshot)

    assert isinstance(efficiency, Decimal)
    assert efficiency < DEFAULT_MINIMUM_EFFICIENCY
    assert propose_direction(snapshot) is None


def test_lowering_the_threshold_lets_the_same_window_speak() -> None:
    """The threshold is the only thing separating these two answers, which is what a sweep tunes.

    The sawtooth's net displacement is not exactly zero — each per-candle return divides by its own
    open, so a round trip in price does not perfectly cancel in returns — and the residue is the
    right size to be ignored by any real threshold and picked up by a threshold of zero. That is the
    honest reading: at zero the candidate has no filter left and will name a direction on noise.
    """
    snapshot = _snapshot(_sawtooth(Decimal("0.00020")))

    assert propose_direction(snapshot, minimum_efficiency=Decimal("0.90")) is None
    assert propose_direction(snapshot, minimum_efficiency=Decimal("0")) is not None


def test_a_flat_window_abstains_rather_than_dividing_by_zero() -> None:
    snapshot = _snapshot([Decimal("1.10000")] * 12)

    assert propose_direction(snapshot) is None
    assert resolve_field("market_context.move_efficiency", snapshot) is None


def test_efficiency_is_unchanged_when_the_whole_series_is_scaled() -> None:
    """Normalised by construction — the same lesson as `volatility_ratio`, for free."""
    small = resolve_field(
        "market_context.move_efficiency", _snapshot(_straight(Decimal("0.00010")))
    )
    large = resolve_field(
        "market_context.move_efficiency", _snapshot(_straight(Decimal("0.00100")))
    )

    assert isinstance(small, Decimal)
    assert small == large


def test_efficiency_of_a_straight_line_is_one() -> None:
    efficiency = resolve_field(
        "market_context.move_efficiency", _snapshot(_straight(Decimal("0.00020")))
    )

    assert efficiency == Decimal("1")


def test_a_distrusted_window_gets_no_direction() -> None:
    """A perfectly straight climb, on a window the real composer refuses to trust.

    The decision comes from `StrategyDecisionComposer` rather than a hand-built report, so the gate
    is tested against the verdict production would actually produce.
    """
    incomplete = _snapshot(_straight(Decimal("0.00020"), count=3))
    decision = StrategyDecisionComposer().compose(incomplete, incomplete.window.as_of)

    assert decision.status != PipelineDecisionStatus.READY_FOR_REVIEW
    assert propose_direction(incomplete, decision=decision) is None
    # Ungated, the same window still has a direction in it — the gate is what removes it.
    assert propose_direction(incomplete) == SignalDirection.SHORT


def _outcome(direction: SignalDirection, kind: OutcomeKind) -> WindowOutcome:
    resolved = kind not in (OutcomeKind.TIMEOUT, OutcomeKind.NO_DATA)
    return WindowOutcome(
        direction=direction,
        entry_price=Decimal("1.10000"),
        stop_loss=Decimal("1.09800") if direction == SignalDirection.LONG else Decimal("1.10200"),
        take_profit=Decimal("1.10300") if direction == SignalDirection.LONG else Decimal("1.09700"),
        kind=kind,
        bars_to_resolution=2 if resolved else None,
    )


def _proposal(
    proposed: SignalDirection | None,
    *,
    long_kind: OutcomeKind = OutcomeKind.TARGET_FIRST,
    short_kind: OutcomeKind = OutcomeKind.STOP_FIRST,
) -> WindowProposal:
    return WindowProposal(
        proposed=proposed,
        long_outcome=_outcome(SignalDirection.LONG, long_kind),
        short_outcome=_outcome(SignalDirection.SHORT, short_kind),
    )


def test_a_perfect_candidate_scores_half_the_gap_over_a_coin_toss() -> None:
    """A candidate that always picks the winning side beats a coin by exactly 50 points.

    Not 100: the benchmark pools both sides of each window, so a coin toss already wins half of
    them. This is the arithmetic ceiling and it is worth stating, because a reported edge anywhere
    near it would mean something is wrong rather than that something is brilliant.
    """
    evaluation = evaluate_direction(
        [_proposal(SignalDirection.LONG) for _ in range(10)], label="perfect"
    )

    assert evaluation.rule_share == Decimal("1")
    assert evaluation.benchmark_share == Decimal("0.5")
    assert evaluation.edge == Decimal("0.5")
    assert evaluation.inverted_share == Decimal("0")


def test_the_inverted_edge_is_exactly_the_negative_of_the_rule_edge() -> None:
    """Continuation and reversion are one signed result, not two chances to find something."""
    proposals = [
        _proposal(SignalDirection.LONG),
        _proposal(SignalDirection.SHORT),
        _proposal(SignalDirection.LONG, long_kind=OutcomeKind.STOP_FIRST),
    ]
    inverted = [
        WindowProposal(
            proposed=(
                SignalDirection.SHORT
                if item.proposed == SignalDirection.LONG
                else SignalDirection.LONG
            ),
            long_outcome=item.long_outcome,
            short_outcome=item.short_outcome,
        )
        for item in proposals
    ]

    forward = evaluate_direction(proposals, label="trend")
    backward = evaluate_direction(inverted, label="reversion")

    assert forward.edge is not None
    assert backward.edge is not None
    assert forward.edge == -backward.edge


def test_abstentions_lower_coverage_without_touching_the_edge() -> None:
    spoke = [_proposal(SignalDirection.LONG) for _ in range(5)]
    quiet = [_proposal(None) for _ in range(15)]

    evaluation = evaluate_direction(spoke + quiet, label="selective")

    assert evaluation.window_count == 20
    assert evaluation.coverage == Decimal("5") / Decimal("20")
    assert evaluation.edge == Decimal("0.5")


def test_an_ambiguous_window_is_not_allowed_to_become_a_win() -> None:
    evaluation = evaluate_direction(
        [_proposal(SignalDirection.LONG, long_kind=OutcomeKind.AMBIGUOUS)], label="ambiguous"
    )

    assert evaluation.resolved_count == 1
    assert evaluation.ambiguous_count == 1
    assert evaluation.rule_share == Decimal("0")


def test_a_window_that_resolved_on_only_one_side_is_dropped_from_both() -> None:
    """Otherwise the rule and its benchmark would be measured over different samples."""
    evaluation = evaluate_direction(
        [_proposal(SignalDirection.LONG, short_kind=OutcomeKind.TIMEOUT)], label="half-resolved"
    )

    assert evaluation.proposed_count == 1
    assert evaluation.resolved_count == 0
    assert evaluation.edge is None


def test_an_empty_evaluation_reports_nothing_rather_than_zero() -> None:
    evaluation = evaluate_direction([], label="empty")

    assert evaluation.coverage is None
    assert evaluation.rule_share is None
    assert evaluation.edge is None


def test_an_evaluation_cannot_claim_more_wins_than_windows() -> None:
    with pytest.raises(ValidationError):
        DirectionEvaluation(
            label="impossible",
            window_count=10,
            proposed_count=5,
            resolved_count=5,
            rule_target_first_count=6,
            inverted_target_first_count=0,
            benchmark_resolved_count=10,
            benchmark_target_first_count=6,
        )


def test_an_evaluation_cannot_speak_about_more_windows_than_it_saw() -> None:
    with pytest.raises(ValidationError):
        DirectionEvaluation(
            label="impossible",
            window_count=3,
            proposed_count=4,
            resolved_count=3,
            rule_target_first_count=1,
            inverted_target_first_count=1,
            benchmark_resolved_count=6,
            benchmark_target_first_count=2,
        )
