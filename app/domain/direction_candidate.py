"""The one module in this project that produces a direction.

Every safety test since Phase 4 has asserted that nothing here decides "up" or "down". Phase 9A
made that mechanical — no function anywhere may return a `SignalDirection` — and said in writing
that the day the test fails, somebody is adding a strategy and must say so out loud. This is that
day, and this is the saying so.

**This candidate has been measured and it failed.** Verdict retracted on 2026-08-07, hours after it
was recorded — see the addendum in `docs/phase9a3-verification-report.md`. The apparent edge came
from the data provider's synthetic weekend rows, which make up about 28% of stored history: the
market is shut, the provider carries prices forward, and the jump back into real trading looks
exactly like the one-sided move this candidate keys on. Exclude weekends and the in-sample result
reverses sign on both timeframes.

The module stays here, unwired and disproved, because that was the plan for a negative verdict: the
next idea should be tested by this apparatus rather than start from an empty file. **Nothing here
should be wired to anything.** The hypothesis below is retained only so the next candidate can see
the shape it has to fill.

**What it proposes**, for the record: a window that moved in a conspicuously straight line gives
some of it back. The sign was chosen by an in-sample sweep — the module was first written the
intuitive way, proposing that a straight move continues, and the sweep contradicted it at every
threshold. That sweep is now known to have been reading filler.

**Abstention is a first-class answer.** The return type is optional and the safety test requires it
to stay optional. A rule that always has an opinion is worse than one that knows when to be quiet,
and most windows do not deserve an opinion: they are chop, and this returns `None` for them.

**No future data, no persistence, no wiring.** The candidate reads a snapshot, which is bounded at
its own `as_of` by construction, and it may not import the outcome measurement that judges it — the
thing being tested must not see the test.
"""

from decimal import Decimal

from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.pipeline_decision import (
    REVIEWABLE_PIPELINE_STATUSES,
    PipelineDecisionReport,
)
from app.domain.entities.signal_contract import SignalDirection

# Chosen in-sample over the first 60% of six months of EURUSD, by "highest edge with coverage of at
# least 10%" — on data since found to be about 28% synthetic weekend filler. The value is retained
# so the retracted result can be reproduced exactly, and it carries no recommendation. On
# weekend-free data this threshold is the worst of the grid on both timeframes.
DEFAULT_MINIMUM_EFFICIENCY = Decimal("0.60")


def propose_direction(
    snapshot: AnalysisSnapshot,
    *,
    decision: PipelineDecisionReport | None = None,
    minimum_efficiency: Decimal = DEFAULT_MINIMUM_EFFICIENCY,
) -> SignalDirection | None:
    """Propose a direction for this window, or `None` when the window does not warrant one.

    Two gates, and both must open:

    - the pipeline must consider the window worth reviewing at all, when a decision is supplied.
      A direction read off a window the eleven rules distrust would be a number with no standing;
    - the movement must be one-sided enough to be worth calling overextended at all. Below the
      threshold the window is chop, and there is nothing to revert from.

    Passing no `decision` measures the hypothesis in isolation, which is what the evaluation harness
    does when it reports the ungated variant. Production would always pass one.

    The proposal is **against** the window's own movement. The mechanism once written here — a
    straight push being exhaustion rather than initiation — was a story fitted to a result, and the
    result has since been retracted. It is left out rather than left standing: an explanation for
    something that did not happen is worse than no explanation, because it survives in the reader's
    memory after the number that prompted it is gone.
    """
    if decision is not None and decision.status not in REVIEWABLE_PIPELINE_STATUSES:
        return None

    displacement = _net_displacement(snapshot)
    efficiency = _move_efficiency(snapshot)
    if displacement is None or efficiency is None:
        return None
    if efficiency < minimum_efficiency:
        # Chop. The window travelled, but it got nowhere in particular, and a direction read off it
        # would be noise dressed as a view.
        return None
    if displacement == 0:
        # Straight-line movement that nets to exactly zero is not possible, but a rounding artefact
        # could produce it; there is no direction in a zero.
        return None

    # Deliberately inverted: a window that climbed is proposed SHORT, and vice versa.
    return SignalDirection.SHORT if displacement > 0 else SignalDirection.LONG


def _net_displacement(snapshot: AnalysisSnapshot) -> Decimal | None:
    """Where the window ended relative to where it began, in summed per-candle returns.

    Deliberately the same series the efficiency ratio divides, so the two cannot disagree: a
    numerator taken from `simple_return` could exceed its own denominator across a gap and produce a
    ratio above one.
    """
    if snapshot.feature_snapshot is None:
        return None
    returns = snapshot.feature_snapshot.candle_summary.per_candle_returns
    if not returns:
        return None
    return sum(returns, Decimal("0"))


def _move_efficiency(snapshot: AnalysisSnapshot) -> Decimal | None:
    """Net displacement over distance travelled, bounded to `[0, 1]`.

    The magnitude half of this calculation is also exposed as `market_context.move_efficiency` in
    the field resolver registry, where any rule may read it. Only the sign is confined to this
    module, because only the sign is a direction.
    """
    if snapshot.feature_snapshot is None:
        return None
    returns = snapshot.feature_snapshot.candle_summary.per_candle_returns
    if not returns:
        return None
    distance_travelled = sum((abs(value) for value in returns), Decimal("0"))
    if distance_travelled == 0:
        return None
    return abs(sum(returns, Decimal("0"))) / distance_travelled
