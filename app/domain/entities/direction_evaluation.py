"""What a directional candidate was worth, measured against choosing at random.

The comparison that matters is **not** against the Phase 9A-2 baseline. That baseline carries the
sample's own drift — over six months of EURUSD, SHORT led LONG by 4.6 percentage points on M15 and
10.9 on H1 with no strategy at all — so a candidate that happens to lean short would inherit the
drift and look skilful for reasons that have nothing to do with it.

Instead the benchmark is computed **on the candidate's own windows**: what a coin toss would have
produced on exactly the subset the candidate chose to speak about. Window selection is held
constant, so the edge isolates the single thing under test — whether choosing this direction over
its opposite carries information.

`inverted_share` is the same subset with every proposal flipped. It costs nothing to compute and
tests the opposite hypothesis, but it is a second hypothesis and must be read as one.
"""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class DirectionEvaluation(BaseModel):
    """One configuration, on one slice of history, judged on its own subset of windows."""

    label: str = Field(min_length=1)
    window_count: int = Field(ge=0)
    proposed_count: int = Field(ge=0)
    resolved_count: int = Field(ge=0)
    rule_target_first_count: int = Field(ge=0)
    inverted_target_first_count: int = Field(ge=0)
    benchmark_resolved_count: int = Field(ge=0)
    benchmark_target_first_count: int = Field(ge=0)
    ambiguous_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def counts_must_be_consistent(self) -> Self:
        if self.proposed_count > self.window_count:
            raise ValueError("a candidate cannot speak about more windows than were measured")
        if self.resolved_count > self.proposed_count:
            raise ValueError("more windows resolved than were proposed")
        if self.rule_target_first_count > self.resolved_count:
            raise ValueError("more wins than resolved windows")
        if self.inverted_target_first_count > self.resolved_count:
            raise ValueError("more inverted wins than resolved windows")
        if self.benchmark_target_first_count > self.benchmark_resolved_count:
            raise ValueError("more benchmark wins than resolved benchmark windows")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def coverage(self) -> Decimal | None:
        """Share of windows the candidate had an opinion about.

        A candidate that speaks about a handful of windows can post any number at all, so this is
        read before the edge, never after.
        """
        if self.window_count == 0:
            return None
        return Decimal(self.proposed_count) / Decimal(self.window_count)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def rule_share(self) -> Decimal | None:
        if self.resolved_count == 0:
            return None
        return Decimal(self.rule_target_first_count) / Decimal(self.resolved_count)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def inverted_share(self) -> Decimal | None:
        if self.resolved_count == 0:
            return None
        return Decimal(self.inverted_target_first_count) / Decimal(self.resolved_count)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def benchmark_share(self) -> Decimal | None:
        """What a coin toss would have produced on these same windows."""
        if self.benchmark_resolved_count == 0:
            return None
        return Decimal(self.benchmark_target_first_count) / Decimal(self.benchmark_resolved_count)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def edge(self) -> Decimal | None:
        """The whole result in one number, or `None` when there is nothing to compare.

        Computed rather than stored so it can never drift from the counts it came from.
        """
        rule_share = self.rule_share
        benchmark_share = self.benchmark_share
        if rule_share is None or benchmark_share is None:
            return None
        return rule_share - benchmark_share
