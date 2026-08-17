"""What holding a currency pair earns beyond its price move.

Phase 9D-4, the first measurement in this project that reads something other than past prices. Being
long `EURUSD` is holding euros funded in dollars: the position earns the euro rate, pays the dollar
rate, and separately gains or loses whatever the exchange rate does. The first part is the
**carry**, the second is the **spot** move, and their sum is what the position actually returned.

**The decomposition is carried in the record, not recovered from it.** A positive total driven
entirely by accrual is a different claim from one where the spot move cooperates, and a single
number cannot show which. Keeping all three in one frozen row is what makes it impossible to report
the total without being able to show its parts.

**Uncovered interest parity is the null.** Theory says the high-rate currency depreciates by exactly
the differential, so the total should be **zero** and the two components should cancel. The
documented anomaly is that historically they have not. That is what makes this a test rather than an
accounting identity: if the parts always cancelled, the total would be zero by construction and
there would be nothing to measure.
"""

from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class CarryReading(BaseModel):
    """One pair at one rebalance date: what it was ranked on, and what it then returned.

    `differential` is known **at** the date, under the lag rule in `app.domain.carry`. The two
    return components describe the holding window that follows it, and are the only fields here that
    look past the date.
    """

    as_of: datetime
    instrument: str = Field(min_length=1)
    base_currency: str = Field(min_length=3, max_length=3)
    quote_currency: str = Field(min_length=3, max_length=3)
    #: Annualised: `rate(base) - rate(quote)`, as a fraction. Positive means the base currency pays
    #: more, so a long position accrues.
    differential: Decimal
    #: The exchange rate's own move over the holding window, as a fraction.
    spot_return: Decimal
    #: The part of `differential` actually earned over the holding window — not the annual figure.
    accrued_carry: Decimal

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def a_pair_needs_two_different_currencies(self) -> Self:
        if self.base_currency == self.quote_currency:
            raise ValueError("a carry differential needs two different currencies")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_return(self) -> Decimal:
        """What the position returned: the price move plus what it accrued holding it."""
        return self.spot_return + self.accrued_carry
