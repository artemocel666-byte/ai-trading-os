"""Assemble a cost curve from the same windows measured under different assumed costs.

Pure domain: costs and outcomes in, a profile out. No candles, no session, no query — the caller
that walks history is the one place any of that lives, as in `field_outcome_profile.py` and
`rule_value.py`.

**Nothing here chooses a cost.** The grid is supplied whole and reported whole, so there is no
parameter that could be tuned to the data and then presented as a finding. That is the same defence
`field_outcome_profile.py` makes for its deciles, and for the same reason: Phase 9A-3 swept a
parameter, cleared its criteria, and was retracted the same day.

**Break-even follows from the plan's geometry, and nothing else.** A plan risking `stop` to seek
`target` needs `stop / (stop + target)` of its resolved windows to reach the target — 3/7 for the
Phase 9A multipliers. That is arithmetic, not a claim about markets, and it is what makes a
cost-adjusted share readable against every gross share the project has already published.
"""

from collections.abc import Iterable, Sequence
from decimal import Decimal

from app.domain.entities.execution_cost import CostPoint, CostSensitivityProfile
from app.domain.entities.outcome import WindowOutcome
from app.domain.outcome_measurement import aggregate_outcomes


def break_even_share(stop: Decimal, target: Decimal) -> Decimal:
    """The share of resolved windows a plan must win to come out level, gross of costs."""
    if stop <= 0 or target <= 0:
        raise ValueError("both distances must be positive to have a break-even share")
    return stop / (stop + target)


def build_cost_sensitivity_profile(
    outcomes_by_cost: Iterable[tuple[Decimal, Sequence[WindowOutcome]]],
    *,
    pair: str,
    timeframe: str,
    stop: Decimal,
    target: Decimal,
) -> CostSensitivityProfile:
    """One curve: the same sample, aggregated once per assumed cost.

    The caller is responsible for measuring the *same windows* at every cost — the entity refuses a
    profile whose points cover different numbers of windows, because a curve built from shifting
    populations compares samples rather than costs.
    """
    points = tuple(
        CostPoint(cost=cost, statistics=aggregate_outcomes(outcomes))
        for cost, outcomes in sorted(outcomes_by_cost, key=lambda item: item[0])
    )
    return CostSensitivityProfile(
        pair=pair,
        timeframe=timeframe,
        break_even_share=break_even_share(stop, target),
        points=points,
    )
