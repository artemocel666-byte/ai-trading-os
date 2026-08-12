"""What happened after windows grouped by where a field's value fell.

Phase 9C-2 showed that the three market-facing rules do not separate outcomes, and that two of them
could barely have: calibrated to fire on 1-10% of windows, they reject 2-5% and cannot partition a
population. That leaves the field itself untested. A band at 0.30/2.5 might be throwing away
information `volatility_ratio` actually carries.

**No threshold is chosen anywhere in this module.** Sweeping cuts and keeping the best is fitting,
and this project has paid for that once already — the 9A-3 candidate cleared criteria on a swept
parameter and was retracted the same day. Windows are bucketed by decile instead: the boundaries
come from the sample, so there is no parameter to overfit and the whole profile is the artefact
rather than a winning point.

**Two readings, because the rule under examination is a band.** A monotone comparison would be blind
to a U-shape — both tails bad, middle good — which is exactly what `volatility_ratio` encodes. So a
profile is read for a gradient (top decile against bottom) and for a band (the two extreme deciles
against the middle eight), and both are fixed before any run.
"""

from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.domain.entities.outcome import OutcomeStatistics

#: Ten buckets. Fine enough to show a shape, coarse enough that each holds hundreds of windows on a
#: six-month sample, so a single decile is not itself a small-sample artefact.
DECILE_COUNT = 10


class FieldDecile(BaseModel):
    """One tenth of the sample, ordered by field value, and what happened after those windows."""

    index: int = Field(ge=1, le=DECILE_COUNT)
    lower_bound: Decimal
    upper_bound: Decimal
    window_count: int = Field(ge=0)
    statistics: OutcomeStatistics

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def statistics_must_pool_both_directions(self) -> Self:
        if self.statistics.measured_count != 2 * self.window_count:
            raise ValueError("decile statistics must pool both directions of every window")
        if self.upper_bound < self.lower_bound:
            raise ValueError("a decile cannot end below where it started")
        return self


class FieldOutcomeProfile(BaseModel):
    """One field, over one instrument and timeframe, as ten ordered buckets.

    `unavailable_count` is kept apart from the deciles. A field that did not resolve says nothing
    about its window, and bucketing it as zero would put an absence at the bottom of the range —
    which is how an unavailable reading becomes an observation.
    """

    pair: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    field_ref: str = Field(min_length=1)
    total_window_count: int = Field(ge=0)
    unavailable_count: int = Field(default=0, ge=0)
    deciles: tuple[FieldDecile, ...] = ()
    pooled_statistics: OutcomeStatistics

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def deciles_must_account_for_every_observed_window(self) -> Self:
        observed = sum(decile.window_count for decile in self.deciles)
        if observed + self.unavailable_count != self.total_window_count:
            raise ValueError("every window must be either bucketed or counted as unavailable")
        if self.pooled_statistics.measured_count != 2 * observed:
            raise ValueError(
                "pooled statistics must cover both directions of every bucketed window"
            )
        if self.deciles and tuple(decile.index for decile in self.deciles) != tuple(
            range(1, len(self.deciles) + 1)
        ):
            raise ValueError("deciles must be present in order from one upward")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def gradient_edge(self) -> Decimal | None:
        """Top decile minus bottom, on target-first share. Catches a monotone relationship.

        `None` when either extreme resolved nothing: a share of zero would read as "never resolved"
        rather than "nothing to divide by".
        """
        if len(self.deciles) < 2:
            return None
        top = self.deciles[-1].statistics.target_first_share
        bottom = self.deciles[0].statistics.target_first_share
        if top is None or bottom is None:
            return None
        return top - bottom

    @computed_field  # type: ignore[prop-decorator]
    @property
    def band_edge(self) -> Decimal | None:
        """Middle eight deciles minus the two extremes. Catches the U-shape a band rule assumes.

        Positive means the middle of the range resolved more decisively than either tail, which is
        the hypothesis `market_context.volatility_ratio` was built on and has never been tested
        against outcomes.
        """
        if len(self.deciles) < 3:
            return None
        middle = _combined_target_first_share(self.deciles[1:-1])
        extremes = _combined_target_first_share((self.deciles[0], self.deciles[-1]))
        if middle is None or extremes is None:
            return None
        return middle - extremes


def _combined_target_first_share(deciles: tuple[FieldDecile, ...]) -> Decimal | None:
    """Pooled over several deciles, by summing counts rather than averaging shares.

    Averaging the shares would weight a decile that resolved twice as often the same as one that
    barely resolved at all.
    """
    target = sum(decile.statistics.target_first_count for decile in deciles)
    resolved = sum(decile.statistics.resolved_count for decile in deciles)
    if resolved == 0:
        return None
    return Decimal(target) / Decimal(resolved)
