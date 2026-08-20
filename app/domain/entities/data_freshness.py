"""Whether what we hold is as recent as it ought to be.

Phase 10-1. Every descriptive feature planned reads the daily universe, and the universe was a
hand-filled snapshot that went stale a day at a time with nothing in the system noticing. Phase 9D-1
already paid for the general version of this lesson: a fill reported success while the data was
holed, and it was only found by checking by hand.

**Absent is not stale, and the difference is the whole design.** One of the forty-five derived pairs
has never had data because the provider does not quote it. Counting that as staleness would make the
report cry every single day, and an alarm that always cries stops being read. It is named as an
absence instead — the project's standing habit of naming what is missing rather than substituting
for it.

**The threshold is named and arguable.** A provider publishes on its own schedule, so being one bar
behind at the moment we happen to look is ordinary; being two is not. That tolerance is a parameter
with a stated default rather than a constant buried in a comparison.
"""

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.entities.market_data import Timeframe

#: How many bars behind the expected newest one a series may be before it is called stale. One,
#: because the provider publishes on its own clock and the job looks on ours; two consecutive misses
#: are no longer a scheduling coincidence.
DEFAULT_TOLERANCE_BARS = 1


class FreshnessStatus(StrEnum):
    """Four answers, and three of them are not `STALE`.

    `ABSENT` and `UNDETERMINED` exist so that "we have nothing" and "we cannot tell" never get
    quietly folded into "we are behind", which would be three different facts wearing one label.
    """

    FRESH = "fresh"
    STALE = "stale"
    ABSENT = "absent"
    UNDETERMINED = "undetermined"


class FreshnessReading(BaseModel):
    """One instrument on one timeframe: what we hold, what we should, and the gap."""

    instrument: str = Field(min_length=1)
    timeframe: Timeframe
    #: The close time of the newest bar in storage, or `None` when there is no bar at all.
    newest_close: datetime | None
    #: The close time the calendar says should exist by now, or `None` when it cannot be derived.
    expected_close: datetime | None
    status: FreshnessStatus
    #: How far behind, present only when the status is `STALE`.
    behind: timedelta | None = None

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def a_gap_belongs_only_to_a_stale_reading(self) -> Self:
        if self.status is FreshnessStatus.STALE:
            if self.behind is None or self.behind <= timedelta(0):
                raise ValueError("a stale reading must say how far behind it is")
        elif self.behind is not None:
            raise ValueError("only a stale reading carries a gap")
        if self.status is FreshnessStatus.ABSENT and self.newest_close is not None:
            raise ValueError("an absent series cannot have a newest bar")
        return self


class FreshnessReport(BaseModel):
    """Every reading from one look, and the counts a caller acts on."""

    as_of: datetime
    readings: tuple[FreshnessReading, ...]

    model_config = ConfigDict(frozen=True)

    def _count(self, status: FreshnessStatus) -> int:
        return sum(1 for reading in self.readings if reading.status is status)

    @property
    def fresh_count(self) -> int:
        return self._count(FreshnessStatus.FRESH)

    @property
    def stale_count(self) -> int:
        return self._count(FreshnessStatus.STALE)

    @property
    def absent_count(self) -> int:
        return self._count(FreshnessStatus.ABSENT)

    @property
    def undetermined_count(self) -> int:
        return self._count(FreshnessStatus.UNDETERMINED)

    @property
    def stale(self) -> tuple[FreshnessReading, ...]:
        """The stale readings, furthest behind first — the order a reader wants them in."""
        return tuple(
            sorted(
                (r for r in self.readings if r.status is FreshnessStatus.STALE),
                key=lambda reading: reading.behind or timedelta(0),
                reverse=True,
            )
        )

    @property
    def worst_gap(self) -> timedelta | None:
        """The largest gap, or `None` when nothing is stale."""
        stale = self.stale
        return stale[0].behind if stale else None

    @property
    def is_healthy(self) -> bool:
        """Nothing stale and nothing we failed to judge. An absence is not ill health."""
        return self.stale_count == 0 and self.undetermined_count == 0
