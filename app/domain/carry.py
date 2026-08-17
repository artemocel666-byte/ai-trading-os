"""The interest rate differential, lagged so it could actually have been known.

Pure domain: rates and returns in, observations out. No candles loaded, no session, no query — the
caller that walks history is the one place any of that lives, as in `cross_section.py`.

**The lag is a measurement choice and lives here, not in storage.** Phase 9D-3 stored each rate
against the month it describes, exactly as published. This module decides how stale a rate must be
before a measurement may rank on it — which is a question that stays open and arguable precisely
because it was kept out of the table.

**An anchor missing one currency is dropped whole.** Not the pairs involving it — the entire date.
Forty-five pairs drawn from ten currencies mean one absent rate silently removes nine pairs and
reshapes every bucket boundary on that date. Ranking the survivors would be a different measurement
wearing the same name, so `lagged_rates_for_anchor` returns nothing at all rather than a partial
map. Phase 9D-3 counted how often this happens before this module existed: once, in June 2020.

**Nothing here chooses anything.** The lag, the components and the accrual are fixed by the Phase
9D-3 plan, written before any rate was looked at.
"""

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from app.domain.entities.carry import CarryReading
from app.domain.entities.cross_section import CrossSectionObservation
from app.domain.market_calendar import MONTHS_PER_YEAR, shift_months

#: Fixed in the Phase 9D-3 plan: at the anchor beginning month M, the value dated M-2 is used.
#:
#: A monthly average for M-1 is only complete once M-1 has ended, and is published later still. One
#: month would mean ranking on a number that did not yet exist — the quiet way a measurement reads
#: the future and reports it as skill. Two months errs toward *not knowing*, and costs almost
#: nothing in a series that moves a few times a year.
RATE_LAG_MONTHS = 2


class CarryComponent(StrEnum):
    """Which part of the return a profile measures. The ranking never changes between them."""

    TOTAL = "total"
    SPOT = "spot"
    CARRY = "carry"


def carry_differential(*, base_rate: Decimal, quote_rate: Decimal) -> Decimal:
    """Annualised `rate(base) - rate(quote)`.

    Long `EURUSD` holds euros funded in dollars, so it earns the euro rate and pays the dollar one.
    The sign convention follows the quote convention: positive means a long position accrues.
    """
    return base_rate - quote_rate


def accrued_carry(differential: Decimal, *, months: int) -> Decimal:
    """The part of an annual differential earned over a holding window of whole months.

    Simple division rather than compounding. Over one month on a differential of a few percent the
    difference is far below the measurement's resolution, and a compounding convention would be one
    more choice to defend for no gain.
    """
    if months < 1:
        raise ValueError("a holding window is at least one month")
    return differential * Decimal(months) / Decimal(MONTHS_PER_YEAR)


def rate_month_for_anchor(anchor: datetime, *, lag_months: int = RATE_LAG_MONTHS) -> datetime:
    """The month whose published rate a measurement at `anchor` is allowed to use."""
    if lag_months < 0:
        raise ValueError("a lag cannot reach forward")
    return shift_months(anchor, -lag_months)


def lagged_rates_for_anchor(
    anchor: datetime,
    rates_by_currency: Mapping[str, Mapping[datetime, Decimal]],
    currencies: frozenset[str],
    *,
    lag_months: int = RATE_LAG_MONTHS,
) -> dict[str, Decimal] | None:
    """Every currency's usable rate at this anchor, or `None` if even one is missing.

    All-or-nothing on purpose: see the module docstring. The caller counts the refusals and reports
    them, because a run that lost dates is not the same measurement as one that did not.
    """
    needed = rate_month_for_anchor(anchor, lag_months=lag_months)
    resolved: dict[str, Decimal] = {}
    for currency in currencies:
        month = rates_by_currency.get(currency, {}).get(needed)
        if month is None:
            return None
        resolved[currency] = month
    return resolved


def build_carry_reading(
    *,
    anchor: datetime,
    instrument: str,
    base_currency: str,
    quote_currency: str,
    rates: Mapping[str, Decimal],
    spot_return: Decimal,
    holding_months: int,
) -> CarryReading:
    """One pair's ranking value and both return components, from a complete rate map."""
    differential = carry_differential(
        base_rate=rates[base_currency], quote_rate=rates[quote_currency]
    )
    return CarryReading(
        as_of=anchor,
        instrument=instrument,
        base_currency=base_currency,
        quote_currency=quote_currency,
        differential=differential,
        spot_return=spot_return,
        accrued_carry=accrued_carry(differential, months=holding_months),
    )


def observations(
    readings: Sequence[CarryReading], component: CarryComponent
) -> list[CrossSectionObservation]:
    """The same ranking, measured three different ways.

    `field_value` is the differential for every component, so the buckets are identical by
    construction and the three results are a decomposition of one measurement rather than three
    measurements that happen to be adjacent. A test asserts the bucket membership matches.
    """
    measured: Callable[[CarryReading], Decimal] = {
        CarryComponent.TOTAL: lambda reading: reading.total_return,
        CarryComponent.SPOT: lambda reading: reading.spot_return,
        CarryComponent.CARRY: lambda reading: reading.accrued_carry,
    }[component]
    return [
        CrossSectionObservation(
            as_of=reading.as_of,
            instrument=reading.instrument,
            field_value=reading.differential,
            forward_return=measured(reading),
        )
        for reading in readings
    ]
