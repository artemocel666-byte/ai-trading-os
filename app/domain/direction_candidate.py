"""The one module in this project that produces a direction.

Every safety test since Phase 4 has asserted that nothing here decides "up" or "down". Phase 9A
made that mechanical — no function anywhere may return a `SignalDirection` — and said in writing
that the day the test fails, somebody is adding a strategy and must say so out loud. This is that
day, and this is the saying so.

**A candidate, not a conclusion.** What lives here is one hypothesis, written so it can be measured
and discarded: a window that moved in a conspicuously straight line is proposed to give some of it
back. `docs/phase9a3-verification-report.md` records whether it cleared the acceptance criteria that
were fixed before it was ever run. If it did not, this module stays exactly where it is — unwired,
disproved, and useful as the shape the next candidate fills.

**The direction of the hypothesis was chosen by measurement, not by taste.** The module was first
written the other way round, proposing that a straight move continues, because that is the intuitive
reading. The in-sample sweep said the opposite at every threshold on both timeframes — continuation
lost by 5 to 8 percentage points, reversion won by the same — so the module was turned around before
the held-out data was touched. Choosing the sign in-sample is what in-sample data is for; the
out-of-sample run in the report is what makes the choice worth anything.

**Abstention is a first-class answer.** The return type is optional and the safety test requires it
to stay optional. A rule that always has an opinion is worse than one that knows when to be quiet,
and most windows do not deserve an opinion: they are chop, and this returns `None` for them.

**No future data, no persistence, no wiring.** The candidate reads a snapshot, which is bounded at
its own `as_of` by construction, and it may not import the outcome measurement that judges it — the
thing being tested must not see the test.
"""

from decimal import Decimal

from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.pipeline_decision import PipelineDecisionReport, PipelineDecisionStatus
from app.domain.entities.signal_contract import SignalDirection

# Chosen in-sample over the first 60% of six months of EURUSD, from the grid 0.20/0.30/0.40/0.50/
# 0.60, by the rule "highest edge with coverage of at least 10%", and never adjusted after the
# out-of-sample run. The grid was checked against the observed distribution of
# `market_context.move_efficiency` first: median 0.28, p75 0.47, p95 0.76 on both M15 and H1, so
# every value in it separates a real part of the sample. 0.60 sits near p88 — the candidate speaks
# only about the most one-sided eighth of windows, and says nothing about the rest.
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

    The proposal is **against** the window's own movement. A plausible reading of why: over twelve
    candles a conspicuously straight push is more often exhaustion than the start of something, and
    with a protective level and a target placed symmetrically in average true ranges, the retrace
    reaches the near side first. That is a story fitted to a result, though, and stories are cheap —
    the number in the report is the only part of this paragraph that was earned.
    """
    if decision is not None and decision.status != PipelineDecisionStatus.READY_FOR_REVIEW:
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
