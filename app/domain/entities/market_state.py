"""Where things stand right now, against what they have historically been.

Phase 10-2, and the first content in this project written for a person rather than for a
measurement. Seven pre-registered measurements returned nothing and 9D-4 explained why: what can be
computed from public data is already in the price. So the product describes **where things stand**
and never what they will do.

**A current observation is not a collapsed distribution.** Today's carry differential is one number
because it *is* one number, and requiring a spread around it would be applying the honesty rule
where it does not belong. The rule bites where a *sample* is summarised — and there the summary and
its dispersion travel together or not at all.

**`CurrencyStrengthReading` is the case that proves the rule earns its keep.** "The euro rose 0.5%
on average" is a different statement depending on whether it rose 0.5% against all nine counterparts
or rose 4% against one and fell 3% against another. One number cannot tell those apart, so the
reading carries the range it was averaged over and cannot be built without it.
"""

from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.entities.calibration import FieldDistribution


class HistoricalReading(BaseModel):
    """One instrument's current value, and the history that gives it a scale.

    `волатильность 1.23` tells a reader nothing — a raw number with no scale is decoration rather
    than description. The percentile and the distribution are what turn it into a fact, and keeping
    all three in one frozen record is what makes it impossible to show the number alone.
    """

    instrument: str = Field(min_length=1)
    field_ref: str = Field(min_length=1)
    current: Decimal
    #: Share of history at or below `current`, floored — a value at the very top reads 100.
    percentile: int = Field(ge=0, le=100)
    distribution: FieldDistribution

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def a_reading_needs_a_history_to_be_read_against(self) -> Self:
        if self.distribution.observed_count == 0:
            raise ValueError("a percentile without observations describes nothing")
        return self

    @property
    def observation_count(self) -> int:
        return self.distribution.observed_count


class CurrencyStrengthReading(BaseModel):
    """One currency's move against every other universe currency it is quoted with.

    The question a single chart cannot answer: a person watching `EURUSD` sees one line and cannot
    tell a rising euro from a falling dollar. Across the whole universe the two separate.
    """

    currency: str = Field(min_length=3, max_length=3)
    #: How many counterpart currencies contributed. Nine when the universe is whole.
    observation_count: int = Field(gt=0)
    mean_move: Decimal
    lowest_move: Decimal
    highest_move: Decimal

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def the_mean_must_sit_inside_the_range_it_came_from(self) -> Self:
        if self.lowest_move > self.highest_move:
            raise ValueError("a range cannot end below where it started")
        if not self.lowest_move <= self.mean_move <= self.highest_move:
            raise ValueError("a mean must lie within the moves it averages")
        return self

    @property
    def is_broad(self) -> bool:
        """Whether the currency moved the same way against every counterpart.

        A statement of fact about the sample, not a prediction. A broad move and a move driven by
        one counterpart are different situations, and the reader is the one who decides what to make
        of that.
        """
        return self.lowest_move > 0 or self.highest_move < 0


class CarryReadingToday(BaseModel):
    """One pair's current interest rate differential.

    Deliberately without a dispersion: this is an observed value, not a summary of a sample. See the
    module docstring — applying the rule here would be cargo-culting it.
    """

    instrument: str = Field(min_length=1)
    differential: Decimal
    #: The month the rate describes, so a reader can see how old the input is.
    rate_month: datetime

    model_config = ConfigDict(frozen=True)


class MarketStateReport(BaseModel):
    """One look at the whole universe: what moved, how unusual it is, and what it pays."""

    as_of: datetime
    window_days: int = Field(gt=0)
    strengths: tuple[CurrencyStrengthReading, ...]
    readings: tuple[HistoricalReading, ...]
    carry: tuple[CarryReadingToday, ...]

    model_config = ConfigDict(frozen=True)

    @property
    def strongest_first(self) -> tuple[CurrencyStrengthReading, ...]:
        return tuple(sorted(self.strengths, key=lambda item: item.mean_move, reverse=True))

    @property
    def highest_carry_first(self) -> tuple[CarryReadingToday, ...]:
        return tuple(sorted(self.carry, key=lambda item: item.differential, reverse=True))
