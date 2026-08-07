"""Score a directional candidate against a coin toss on the windows it chose.

Pure aggregation: outcomes in, an evaluation out. It computes nothing about markets and knows
nothing about the candidate's reasoning — it is handed, per window, what the candidate said and what
happened afterwards in both directions.

The benchmark pools both directions over the candidate's own subset. That is what makes the number
honest: a candidate is credited only for choosing better than a coin on the windows it selected,
never for selecting windows that were easy in a period that drifted one way.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from app.domain.entities.direction_evaluation import DirectionEvaluation
from app.domain.entities.outcome import OutcomeKind, WindowOutcome
from app.domain.entities.signal_contract import SignalDirection

# Ambiguity counts against the plan, exactly as it does in Phase 9A-2: an outcome the data cannot
# adjudicate is not allowed to become a win.
_WIN = OutcomeKind.TARGET_FIRST


@dataclass(frozen=True)
class WindowProposal:
    """One window: what the candidate proposed, and what each direction actually did.

    Both outcomes are always carried, even when the candidate stayed quiet, because the benchmark
    needs the direction the candidate did *not* choose.
    """

    proposed: SignalDirection | None
    long_outcome: WindowOutcome
    short_outcome: WindowOutcome


def evaluate_direction(proposals: Iterable[WindowProposal], *, label: str) -> DirectionEvaluation:
    """Tally a candidate over a slice of history."""
    window_count = 0
    proposed_count = 0
    resolved_count = 0
    rule_wins = 0
    inverted_wins = 0
    benchmark_resolved = 0
    benchmark_wins = 0
    ambiguous_count = 0

    for proposal in proposals:
        window_count += 1
        if proposal.proposed is None:
            continue
        proposed_count += 1

        chosen, opposite = _split(proposal)
        if _is_resolved(chosen) and _is_resolved(opposite):
            # Both readings must exist for this window, otherwise the rule and its benchmark would
            # be measured over different samples and the difference would mean nothing.
            resolved_count += 1
            rule_wins += int(chosen.kind == _WIN)
            inverted_wins += int(opposite.kind == _WIN)
            ambiguous_count += int(chosen.kind == OutcomeKind.AMBIGUOUS)
            # A coin toss on this window would have taken each side half the time, so pooling both
            # sides is the same thing counted without the variance.
            benchmark_resolved += 2
            benchmark_wins += int(chosen.kind == _WIN) + int(opposite.kind == _WIN)

    return DirectionEvaluation(
        label=label,
        window_count=window_count,
        proposed_count=proposed_count,
        resolved_count=resolved_count,
        rule_target_first_count=rule_wins,
        inverted_target_first_count=inverted_wins,
        benchmark_resolved_count=benchmark_resolved,
        benchmark_target_first_count=benchmark_wins,
        ambiguous_count=ambiguous_count,
    )


def _split(proposal: WindowProposal) -> tuple[WindowOutcome, WindowOutcome]:
    if proposal.proposed == SignalDirection.LONG:
        return (proposal.long_outcome, proposal.short_outcome)
    return (proposal.short_outcome, proposal.long_outcome)


def _is_resolved(outcome: WindowOutcome) -> bool:
    """Timeouts and missing data are excluded from both sides, never scored as losses."""
    return outcome.kind in (OutcomeKind.TARGET_FIRST, OutcomeKind.STOP_FIRST, OutcomeKind.AMBIGUOUS)
