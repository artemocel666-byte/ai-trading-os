"""How many bets a set of positions actually is.

Phase 10-3. Someone holding `EURUSD`, `GBPUSD` and `AUDUSD` believes they hold three positions. If
those three are 0.85 correlated they hold roughly **one position at triple size**, and the loss that
arrives will arrive on all three at once. Saying so needs no forecast — it is arithmetic on stored
prices, and it is the reading that most clearly justifies this product.

**A single correlation is a lonely central tendency in a different costume.** Reporting `0.6` for a
window whose halves were `0.85` and `0.30` is the exact failure Phase 10-2 closed for medians, so a
reading here cannot exist without both halves beside it.

**A missing correlation is never a zero.** Zero reads as "independent", and telling somebody their
positions are independent when nothing at all is known is the worst thing this feature could do.
Absences are named, as everywhere else in this project.
"""

from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

#: Overlapping observations required before two instruments may be correlated at all. Forty splits
#: into two halves of twenty, which is thin for either half — deliberately, because a correlation
#: that swings between its halves is exactly what this reading exists to expose.
MINIMUM_OVERLAP = 40


class ConcentrationStatus(StrEnum):
    """Three answers, and only one of them is a number.

    `FULLY_HEDGED` exists because the measure genuinely has no value there rather than a large one:
    a set whose correlations cancel to zero has no variance left to divide by, and reporting an
    enormous "effective bets" would dress a division by zero as a finding.
    """

    MEASURED = "measured"
    FULLY_HEDGED = "fully_hedged"
    NOT_ENOUGH_OVERLAP = "not_enough_overlap"


class CorrelationReading(BaseModel):
    """Two instruments over one window, with the halves that show whether it held."""

    left: str = Field(min_length=1)
    right: str = Field(min_length=1)
    #: Days both instruments were priced. Pairs have different histories; this is never assumed.
    overlap_count: int = Field(ge=MINIMUM_OVERLAP)
    coefficient: Decimal = Field(ge=Decimal("-1"), le=Decimal("1"))
    first_half: Decimal = Field(ge=Decimal("-1"), le=Decimal("1"))
    second_half: Decimal = Field(ge=Decimal("-1"), le=Decimal("1"))

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def two_instruments_must_differ(self) -> Self:
        if self.left == self.right:
            raise ValueError("an instrument is trivially correlated with itself")
        return self

    @property
    def half_gap(self) -> Decimal:
        """How far the two halves disagree — whether the middle figure is worth much."""
        return abs(self.first_half - self.second_half)


class ConcentrationReading(BaseModel):
    """One set of instruments, and how many independent bets it comes to.

    For `N` instruments held in equal size the portfolio variance is proportional to the sum of
    every entry of the correlation matrix, so the effective count is `N² / ΣΣρ`. Perfectly
    correlated instruments give exactly 1; uncorrelated ones give exactly `N`. Both extremes are
    hand-checkable, which is why this measure was chosen over one needing eigenvalues.
    """

    instruments: tuple[str, ...]
    status: ConcentrationStatus
    effective_bets: Decimal | None = None
    correlations: tuple[CorrelationReading, ...] = ()
    #: Named when the status is `NOT_ENOUGH_OVERLAP`, so a reader learns which pair was missing
    #: rather than only that something was.
    missing_pairs: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def a_number_belongs_only_to_a_measured_reading(self) -> Self:
        if len(self.instruments) < 2:
            raise ValueError("concentration is a question about two instruments or more")
        if len(set(self.instruments)) != len(self.instruments):
            raise ValueError("an instrument cannot be held against itself")
        if self.status is ConcentrationStatus.MEASURED:
            if self.effective_bets is None:
                raise ValueError("a measured reading must carry its effective count")
            if not Decimal("1") <= self.effective_bets:
                raise ValueError("a set can never be fewer than one bet")
        elif self.effective_bets is not None:
            raise ValueError("only a measured reading carries an effective count")
        if self.status is not ConcentrationStatus.NOT_ENOUGH_OVERLAP and self.missing_pairs:
            raise ValueError("only an unmeasurable reading names missing pairs")
        return self

    @property
    def instrument_count(self) -> int:
        return len(self.instruments)

    @property
    def widest_half_gap(self) -> Decimal | None:
        """The least stable correlation in the set, or `None` when none were measured."""
        if not self.correlations:
            return None
        return max(reading.half_gap for reading in self.correlations)
