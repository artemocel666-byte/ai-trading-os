"""What participants hold, as opposed to what the price did.

Phase 10-4. Every other reading in this project describes a price. This one describes positions —
the last obtainable source on the shortlist drawn up after 9D-4, and a different kind of fact.

**Its value here is descriptive.** As a predictor it would almost certainly be the eighth null: the
documented effects are the same order as carry, and the resolution arithmetic from 9D-4 applies
unchanged. Nothing in this module or anything rendering it may suggest otherwise.

**A reading is anchored to the Tuesday it describes, not to the day it was fetched.** The CFTC
publishes on Friday afternoon for the preceding Tuesday, so the data is three days old on arrival
and up to ten before the next one. A line saying "участники держат" implies the present tense and
would be wrong by default; the age is carried here so the renderer can state it.

**The dollar entry is an index against a basket, not a bilateral rate.** "Speculators are net long
the euro against the dollar" and "speculators are net long a dollar basket" are different
observations, so the distinction travels with the row rather than living in a reader's memory.
"""

from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc

#: The provider recorded on every row. Positioning is a different kind of observation from a candle,
#: so it carries its own provenance and `REAL_MARKET_DATA_PROVIDERS` is untouched by it.
CFTC_PROVIDER_NAME = "cftc"


class PositioningReading(BaseModel):
    """One currency's speculative positioning for one weekly report."""

    provider: str = Field(min_length=1)
    #: The CFTC contract code, and the reason this project maps by code rather than by name.
    #: Both `NZ DOLLAR` and `USD INDEX` were renamed in early 2022 — their previous names stop on
    #: 2022-02-01 — while the codes `112741` and `098662` run unchanged since 1999 and 1992. A
    #: name-keyed mapping would have produced two series starting in 2022 beside six running for
    #: decades, and the report would have looked healthy while being holed.
    contract_code: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    #: The Tuesday the positions describe.
    report_date: datetime
    noncommercial_long: int = Field(ge=0)
    noncommercial_short: int = Field(ge=0)
    #: Always positive: a row without open interest yields no reading at all, because the share
    #: below would be a division by zero dressed as a position of zero.
    open_interest: int = Field(gt=0)
    #: True for the dollar index, which is measured against a basket rather than one counterpart.
    is_basket: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("currency")
    @classmethod
    def currency_must_be_upper_case(cls, value: str) -> str:
        stripped = value.strip().upper()
        if not stripped.isalpha():
            raise ValueError("currency must be three letters")
        return stripped

    @field_validator("report_date")
    @classmethod
    def report_date_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def a_report_date_is_a_whole_day(self) -> Self:
        moment = self.report_date
        if (moment.hour, moment.minute, moment.second, moment.microsecond) != (0, 0, 0, 0):
            raise ValueError("a report date is a whole day in UTC")
        return self

    @property
    def net_share(self) -> Decimal:
        """Net speculative position as a share of open interest.

        Normalised because raw contract counts compare neither between currencies nor across
        decades: the euro contract dwarfs the New Zealand one, and every contract has grown.
        """
        net = Decimal(self.noncommercial_long - self.noncommercial_short)
        return net / Decimal(self.open_interest)

    def age_in_days(self, as_of: datetime) -> int:
        """How stale this reading is at the moment somebody reads it."""
        return (normalize_to_utc(as_of) - self.report_date).days
