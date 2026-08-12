"""Whether a rule's verdict says anything about what the window then did.

Eleven rules decide whether a window is worth looking at. Every calibration this project has run —
7D-2, 9A-6, 9A-8 — measured **how often each rule fires**, and none measured whether firing helps.
`scripts/measure_outcomes.py` knows what happened after a window and nothing about the verdict;
`scripts/replay_rules.py` knows the verdict and nothing about what happened.

The comparison is a rule's own two groups: the windows it passed against the windows it failed, on
the same instrument, the same timeframe, the same six months. Nothing else is held out, because
nothing else differs.

**Both directions are pooled, on purpose.** A window where LONG reached its target and a window
where SHORT did are both windows that *moved cleanly*, and that is the only property a rule with no
direction can plausibly select for. Pooling is what keeps a directional claim from being readable
out of this at all.

**The result is biased in favour of the rules and cannot be read as confirmation.** The thresholds
were fitted on this history, so a rule that separates outcomes here has demonstrated that its own
fit is self-consistent and no more. What the test *can* do is disconfirm: a rule that fails to
separate outcomes on the data it was tuned on has no case left.
"""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.domain.entities.outcome import OutcomeStatistics


class RuleValueComparison(BaseModel):
    """One rule, judged on the windows it passed against the windows it failed."""

    rule_id: str = Field(min_length=1)
    passed_window_count: int = Field(ge=0)
    failed_window_count: int = Field(ge=0)
    passed_statistics: OutcomeStatistics
    failed_statistics: OutcomeStatistics

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def statistics_must_match_the_window_counts(self) -> Self:
        # Two directions are measured for every window, so the pooled sample is twice the windows.
        # Asserting it here means a partitioning bug cannot reach a report and look like a finding.
        if self.passed_statistics.measured_count != 2 * self.passed_window_count:
            raise ValueError("passed statistics must pool both directions of every passed window")
        if self.failed_statistics.measured_count != 2 * self.failed_window_count:
            raise ValueError("failed statistics must pool both directions of every failed window")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def failure_share(self) -> Decimal | None:
        """How often the rule fired. Read before the edge, never after.

        Two of the three market rules fire on a few percent of windows, so their failing group is
        small and can post any number at all. A rule that fired eleven times has not been measured.
        """
        total = self.passed_window_count + self.failed_window_count
        if total == 0:
            return None
        return Decimal(self.failed_window_count) / Decimal(total)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def target_first_edge(self) -> Decimal | None:
        """Passed minus failed, on the share of resolved windows that reached a target first.

        Positive means windows the rule accepted resolved decisively more often than the ones it
        rejected — which is the only thing "this window is worth looking at" can mean without a
        direction. `None` when either group resolved nothing, because a share of zero would read as
        "never resolved" rather than "nothing to divide by".

        Computed rather than stored so it can never drift from the statistics it came from.
        """
        passed = self.passed_statistics.target_first_share
        failed = self.failed_statistics.target_first_share
        if passed is None or failed is None:
            return None
        return passed - failed

    @computed_field  # type: ignore[prop-decorator]
    @property
    def timeout_edge(self) -> Decimal | None:
        """Failed minus passed on the timeout share, so positive still means the rule helped.

        A window that resolved nothing inside the horizon wasted the attention it asked for.
        """
        passed = self.passed_statistics.timeout_share
        failed = self.failed_statistics.timeout_share
        if passed is None or failed is None:
            return None
        return failed - passed


class RuleValueReport(BaseModel):
    """Every market-facing rule, over one instrument and timeframe.

    `eligible_window_count` is the population after the plumbing rules were required to pass. The
    rules about our own data — completeness, candle age, market open, snapshot built — are excluded
    from comparison rather than measured: they fail exactly when the data is bad, and outcomes over
    bad data are strange for reasons that have nothing to do with the market.
    """

    pair: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    total_window_count: int = Field(ge=0)
    eligible_window_count: int = Field(ge=0)
    windows_without_a_plan: int = Field(default=0, ge=0)
    comparisons: tuple[RuleValueComparison, ...] = ()
    pooled_statistics: OutcomeStatistics

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def eligible_cannot_exceed_total(self) -> Self:
        if self.eligible_window_count > self.total_window_count:
            raise ValueError("more windows were eligible than were measured")
        if self.pooled_statistics.measured_count != 2 * self.eligible_window_count:
            raise ValueError(
                "pooled statistics must cover both directions of every eligible window"
            )
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def eligible_share(self) -> Decimal | None:
        if self.total_window_count == 0:
            return None
        return Decimal(self.eligible_window_count) / Decimal(self.total_window_count)
