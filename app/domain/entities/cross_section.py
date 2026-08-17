"""Many instruments compared at one moment, and what followed.

Phase 9D-2. Every measurement before it asked what follows a window on **one** series through time,
and five of them answered nothing. This asks a different question: of the instruments available on
one date, do those at the top of some ordering behave differently over the next month than those at
the bottom?

**The statistic is a time series, not a pool.** Each rebalance date yields exactly one number — the
top bucket's mean return minus the bottom's — and the series of those numbers is the result. Pooling
every instrument-month into one bag would count forty-four correlated pairs in a single month as
forty-four independent facts, which is how a cross-sectional study inflates its own confidence.

**This module holds a direction, and that is a deliberate change.** Until now nothing in the project
could produce one, because there was no measured basis for one and inventing one was the failure to
avoid. A ranking is structurally a direction: the headline number is what the top did *minus* what
the bottom did. So the line moved from *"no direction exists"* to *"no direction is delivered"* — a
safety test keeps this module out of every service, Telegram, API and scheduler file, and
`REAL_TRADING_ENABLED` stays permanently `False`.
"""

from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

#: Three buckets, pre-registered in the Phase 9D-1 plan. Forty-four pairs drawn from ten currencies
#: carry roughly nine independent dimensions, so deciles would report four-pair buckets of things
#: that mostly move together.
BUCKET_COUNT = 3

#: The t-statistic a spread must reach. Two standard errors over ~230 monthly periods is an
#: annualised Sharpe near 0.45 — this design can see a strong effect and cannot confirm a faint one.
MINIMUM_T_STATISTIC = Decimal("2.0")


class CrossSectionObservation(BaseModel):
    """One instrument on one rebalance date: where it ranked, and what it then did.

    `field_value` is what the instrument is *ordered by* — known on the date. `forward_return` is
    what happened afterwards, and is the only thing here that looks past the date. Keeping them in
    one frozen record is what makes it impossible to rank on something the future supplied.
    """

    as_of: datetime
    instrument: str = Field(min_length=1)
    field_value: Decimal
    forward_return: Decimal

    model_config = ConfigDict(frozen=True)


class CrossSectionBucket(BaseModel):
    """One slice of one date's ordering."""

    index: int = Field(ge=1)
    instrument_count: int = Field(gt=0)
    lower_bound: Decimal
    upper_bound: Decimal
    mean_forward_return: Decimal

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def bounds_must_not_run_backwards(self) -> Self:
        if self.upper_bound < self.lower_bound:
            raise ValueError("a bucket cannot end below where it started")
        return self


class CrossSectionPeriod(BaseModel):
    """One rebalance date: the ordering, the buckets, and the single number they produce."""

    as_of: datetime
    instrument_count: int = Field(gt=0)
    buckets: tuple[CrossSectionBucket, ...]

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def buckets_must_be_present_and_ordered(self) -> Self:
        if len(self.buckets) < 2:
            raise ValueError("a period needs at least a top and a bottom bucket to have a spread")
        if tuple(bucket.index for bucket in self.buckets) != tuple(range(1, len(self.buckets) + 1)):
            raise ValueError("buckets must be present in order from one upward")
        if sum(bucket.instrument_count for bucket in self.buckets) != self.instrument_count:
            raise ValueError("every ranked instrument must land in exactly one bucket")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def spread(self) -> Decimal:
        """Top bucket minus bottom. The one number this date contributes to the result."""
        return self.buckets[-1].mean_forward_return - self.buckets[0].mean_forward_return


class SpreadRun(BaseModel):
    """A stretch of consecutive rebalance periods and what the spread did across it."""

    started_at: datetime
    ended_at: datetime
    period_count: int = Field(ge=1)
    cumulative_spread: Decimal

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def a_run_cannot_end_before_it_starts(self) -> Self:
        if self.ended_at < self.started_at:
            raise ValueError("a run cannot end before it starts")
        return self


class CrossSectionProfile(BaseModel):
    """The series of per-date spreads, and what it adds up to.

    `cost_per_leg` is subtracted from every period's spread before anything is computed: a long and
    a short leg are both rebalanced each period, so the round trip is paid twice. Zero by default,
    and swept by the caller rather than assumed — the Phase 9C-4 doctrine.
    """

    field_ref: str = Field(min_length=1)
    bucket_count: int = Field(ge=2)
    cost_per_leg: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    periods: tuple[CrossSectionPeriod, ...]

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def periods_must_be_ordered_in_time(self) -> Self:
        if not self.periods:
            raise ValueError("a profile needs at least one rebalance period")
        moments = [period.as_of for period in self.periods]
        if moments != sorted(moments) or len(set(moments)) != len(moments):
            raise ValueError("rebalance periods must be strictly ordered in time")
        return self

    @property
    def net_spreads(self) -> tuple[Decimal, ...]:
        """Each period's spread after the round trip on both legs."""
        charge = 2 * self.cost_per_leg
        return tuple(period.spread - charge for period in self.periods)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mean_spread(self) -> Decimal:
        spreads = self.net_spreads
        return sum(spreads, Decimal("0")) / Decimal(len(spreads))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def standard_error(self) -> Decimal | None:
        """`None` with fewer than two periods: one number has no spread about itself."""
        spreads = self.net_spreads
        if len(spreads) < 2:
            return None
        mean = self.mean_spread
        variance = sum(((value - mean) ** 2 for value in spreads), Decimal("0")) / Decimal(
            len(spreads) - 1
        )
        if variance <= 0:
            return Decimal("0")
        return variance.sqrt() / Decimal(len(spreads)).sqrt()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def t_statistic(self) -> Decimal | None:
        """`None` when there is no error to divide by, rather than a substituted infinity."""
        error = self.standard_error
        if error is None or error == 0:
            return None
        return self.mean_spread / error

    def worst_run(self, *, length: int) -> SpreadRun | None:
        """The worst stretch of `length` consecutive periods, or `None` if the series is shorter.

        Added in Phase 9D-4 and applicable to any spread series. A mean and a t-statistic describe
        the middle of a distribution and say nothing about its edge, and carry's signature failure
        is exactly *positive mean, catastrophic tail* — it broke violently in 2008 and on the franc
        in 2015. A spread whose mean passes while its worst year is ruinous has to be reported as
        that, not as a finding, and a number nobody computed cannot be reported at all.

        `length=1` gives the single worst period, which is the same question at the shortest window.

        **Summed, not compounded.** These are differences between two returns, and a difference does
        not compound like a return; summing is the arithmetic that matches what the number is.
        """
        if length < 1:
            raise ValueError("a run covers at least one period")
        spreads = self.net_spreads
        if len(spreads) < length:
            return None
        starts = range(len(spreads) - length + 1)
        worst = min(starts, key=lambda index: sum(spreads[index : index + length], Decimal("0")))
        return SpreadRun(
            started_at=self.periods[worst].as_of,
            ended_at=self.periods[worst + length - 1].as_of,
            period_count=length,
            cumulative_spread=sum(spreads[worst : worst + length], Decimal("0")),
        )

    def half(self, *, first: bool) -> "CrossSectionProfile":
        """The same profile over one half of its periods, for the stability criterion.

        Not a holdout — nothing was selected, so there is nothing to hold out from. It is this
        design's analogue of the four-series sign check every previous phase used.
        """
        midpoint = len(self.periods) // 2
        chosen = self.periods[:midpoint] if first else self.periods[midpoint:]
        return CrossSectionProfile(
            field_ref=self.field_ref,
            bucket_count=self.bucket_count,
            cost_per_leg=self.cost_per_leg,
            periods=chosen,
        )

    @property
    def clears_the_bar(self) -> bool:
        """Every pre-registered criterion at once, so no partial pass can be read as a pass."""
        statistic = self.t_statistic
        if statistic is None or self.mean_spread <= 0 or statistic < MINIMUM_T_STATISTIC:
            return False
        if len(self.periods) < 4:
            return False
        return self.half(first=True).mean_spread > 0 and self.half(first=False).mean_spread > 0
