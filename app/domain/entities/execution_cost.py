"""What an assumed execution cost does to a measured outcome.

Every outcome figure this project has published is gross. That has been a caveat in prose since
Phase 9A-2 and a standing open item in `PLANS.md`; here it becomes an axis. The cost is *assumed*,
not observed — the project stores OHLC and no spread — so nothing in this module may be confused
with data. It is a parameter of a report, and the safety tests keep it out of storage.

**Nothing here chooses a cost.** A sweep that picked the flattering point would be the same mistake
Phase 9A-3 made with a threshold. The whole curve is the artefact; the two readings below are read
off it, and both are fixed before any run.

**A missing reading is named rather than substituted.** "Already below break-even before any cost"
and "the grid did not reach far enough" are different statements, and a single `None` would merge
them into a shrug. `CostReading` carries the distinction, for the same reason `target_first_share`
returns `None` instead of zero when nothing resolved.
"""

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.domain.entities.outcome import OutcomeStatistics

#: The effect size Phase 9C-2 and 9C-3 required before calling a field informative: five percentage
#: points of target-first share, holding across four series. Expressing that bar as a cost is the
#: point of this phase — it says what the project's own standard of evidence is worth in the one
#: unit that actually gets paid.
FINDING_EQUIVALENT_POINTS = Decimal("0.05")


class CostReadingStatus(StrEnum):
    """Why a reading off the curve does or does not have a number."""

    FOUND = "FOUND"
    #: The share was already at or below the level being sought before any cost was applied. There
    #: is no positive cost that causes it, and reporting an interpolated one would invent a cause.
    ALREADY_BELOW_AT_ZERO = "ALREADY_BELOW_AT_ZERO"
    #: The curve never fell that far within the swept grid. A wider grid would answer it; this one
    #: cannot, and saying so is different from saying the cost is large.
    BEYOND_THE_GRID = "BEYOND_THE_GRID"
    #: Some point on the curve resolved nothing, so there is no share to compare.
    UNAVAILABLE = "UNAVAILABLE"


class CostReading(BaseModel):
    """A cost read off the curve, or a named reason there is none."""

    status: CostReadingStatus
    cost: Decimal | None = None

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def a_cost_is_present_exactly_when_one_was_found(self) -> Self:
        if self.status == CostReadingStatus.FOUND and self.cost is None:
            raise ValueError("a found reading must carry the cost it found")
        if self.status != CostReadingStatus.FOUND and self.cost is not None:
            raise ValueError("a reading that found nothing must not carry a cost")
        return self


class CostPoint(BaseModel):
    """One assumed round-trip cost, and the outcomes of the whole sample measured under it."""

    cost: Decimal = Field(ge=Decimal("0"))
    statistics: OutcomeStatistics

    model_config = ConfigDict(frozen=True)


class CostSensitivityProfile(BaseModel):
    """One series measured across a grid of assumed costs.

    `break_even_share` is carried on the profile rather than assumed by a reader, because it depends
    on the plan geometry the run used: a plan risking 1.5 and seeking 2.0 breaks even at 3/7, and a
    different pair of multipliers would move it.
    """

    pair: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    break_even_share: Decimal = Field(gt=Decimal("0"), lt=Decimal("1"))
    points: tuple[CostPoint, ...]

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def the_curve_must_start_at_zero_and_climb(self) -> Self:
        if len(self.points) < 2:
            raise ValueError("a sensitivity profile needs at least a zero-cost point and one more")
        if self.points[0].cost != 0:
            # Without a free point there is nothing to measure the others against, and every
            # difference below would be relative to an already-handicapped sample.
            raise ValueError("the first point must be the zero-cost measurement")
        costs = [point.cost for point in self.points]
        if costs != sorted(costs) or len(set(costs)) != len(costs):
            raise ValueError("cost points must be strictly ascending")
        measured = {point.statistics.measured_count for point in self.points}
        if len(measured) != 1:
            # Every point must be the same windows under a different assumption. Different
            # populations would make the curve a comparison of samples rather than of costs.
            raise ValueError("every cost point must cover the same number of windows")
        return self

    @property
    def zero_cost_share(self) -> Decimal | None:
        """The gross figure, which must reproduce what previous phases published."""
        return self.points[0].statistics.target_first_share

    @computed_field  # type: ignore[prop-decorator]
    @property
    def break_even_cost(self) -> CostReading:
        """The cost at which the plan stops paying for itself.

        `ALREADY_BELOW_AT_ZERO` is the answer that matters: it says no cost is small enough, because
        the plan was already losing before anyone charged for it.
        """
        return self._cost_where_share_falls_to(self.break_even_share)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def finding_equivalent_cost(self) -> CostReading:
        """The cost worth as much target-first share as the project's own bar for a finding."""
        return self.cost_for_loss_of(FINDING_EQUIVALENT_POINTS)

    def cost_for_loss_of(self, share_points: Decimal) -> CostReading:
        """The cost that costs `share_points` of target share, against the zero-cost figure."""
        if share_points <= 0:
            raise ValueError("a loss of share must be positive to be located on the curve")
        gross = self.zero_cost_share
        if gross is None:
            return CostReading(status=CostReadingStatus.UNAVAILABLE)
        return self._cost_where_share_falls_to(gross - share_points)

    def _cost_where_share_falls_to(self, level: Decimal) -> CostReading:
        """First crossing, linearly interpolated between the two points that bracket it.

        The *first* crossing rather than the last: real curves wobble, and the smallest cost that
        does the damage is the honest answer to "how much can this bear".
        """
        measured = [point.statistics.target_first_share for point in self.points]
        shares = [share for share in measured if share is not None]
        if len(shares) != len(measured):
            return CostReading(status=CostReadingStatus.UNAVAILABLE)

        if shares[0] <= level:
            return CostReading(status=CostReadingStatus.ALREADY_BELOW_AT_ZERO)

        for index in range(1, len(shares)):
            previous, current = shares[index - 1], shares[index]
            if current > level:
                continue
            low_cost, high_cost = self.points[index - 1].cost, self.points[index].cost
            crossed = (previous - level) / (previous - current)
            return CostReading(
                status=CostReadingStatus.FOUND,
                cost=low_cost + (high_cost - low_cost) * crossed,
            )

        return CostReading(status=CostReadingStatus.BEYOND_THE_GRID)
