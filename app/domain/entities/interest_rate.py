"""A currency's short-term interest rate for one month.

Phase 9D-3, and the first data in this project that is **not a price**. Six pre-registered
measurements returned nothing, and every one of them read past prices of the instrument itself;
9D-2 drew the boundary explicitly. An interest rate is outside it.

**Storage is faithful; the lag is a measurement choice.** `as_of` is the month the value describes,
exactly as the source states it. How stale a rate must be before a measurement may rank on it is a
question for that measurement's pre-registration — baking a lag in here would make it impossible to
question later.

**There is no sign constraint, and that is deliberate.** JPY, CHF and EUR all spent years below
zero; a positivity validator would reject real observations. The absence of that validator is
asserted by a test, so nobody adds one later thinking it was an oversight.
"""

from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc

#: The provider name recorded on every row. Rates are a different kind of observation from candles,
#: so they carry their own provenance and `REAL_MARKET_DATA_PROVIDERS` is untouched by them.
FRED_PROVIDER_NAME = "fred"


class InterestRate(BaseModel):
    """One currency, one month, one rate — as a fraction of a year, not a percent.

    The source quotes `3.84` meaning 3.84% per annum. The conversion happens once, in the adapter,
    where the source's convention is known; by the time a rate reaches here it is `0.0384`.
    """

    provider: str = Field(min_length=1)
    #: The provider's own identifier for the series this value came from, so a stored number can be
    #: traced back to exactly one published series rather than to "FRED, somewhere".
    source_series: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    as_of: datetime
    annual_rate: Decimal

    model_config = ConfigDict(frozen=True)

    @field_validator("currency")
    @classmethod
    def currency_must_be_upper_case(cls, value: str) -> str:
        stripped = value.strip().upper()
        if not stripped.isalpha():
            raise ValueError("currency must be three letters")
        return stripped

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("annual_rate", mode="before")
    @classmethod
    def reject_float_rate(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("annual_rate must use Decimal-compatible inputs, not float")
        return value

    @model_validator(mode="after")
    def as_of_must_be_the_start_of_a_month(self) -> Self:
        """The source publishes one value per month, dated to its first day.

        Storing a mid-month timestamp would make two rows for one month possible, and the whole
        point of the unique key is that a month has exactly one rate.
        """
        moment = self.as_of
        if (moment.day, moment.hour, moment.minute, moment.second, moment.microsecond) != (
            1,
            0,
            0,
            0,
            0,
        ):
            raise ValueError("as_of must be the first instant of a month in UTC")
        if not self.annual_rate.is_finite():
            raise ValueError("annual_rate must be finite")
        return self
