"""When the currency market is open, and why that is a question about data rather than taste.

The provider returns a continuous 24/7 series. The market is not continuous: it closes on Friday
evening and reopens on Sunday evening. Across the whole stored history, **28.5% of candles fall on a
Saturday or Sunday**, and they are not traded prices — long runs carry byte-identical highs and
lows while the last price is carried forward, then one violently wide candle appears when trading
actually resumes.

That makes closed-market data a **data-quality** concern and not a preference about when to trade.
A window built from carried-forward prices has an understated average true range, a fabricated
transition at the reopen, and no informational content; every threshold calibrated over it is
partly measuring the filler. The Phase 9A-3 verdict was retracted for exactly this reason.

**Deliberately the whole of Saturday and Sunday**, rather than the true session boundary. The real
one drifts with daylight saving and differs by venue, and this project has no venue specification
to read it from. Over-excluding is the safe direction: the cost is the genuine Sunday-evening
reopen, a few hours a week, against a rule that cannot be wrong about the other hundred and sixty.

If an instrument specification with real trading hours ever arrives, it should replace this.
"""

from datetime import UTC, datetime
from enum import IntEnum

from app.core.time import normalize_to_utc

#: Months in a year. Named because an annual rate divided by twelve appears in the carry
#: measurement, and a bare `12` there could be read as a window length.
MONTHS_PER_YEAR = 12


def month_start(moment: datetime) -> datetime:
    """The first instant of the calendar month containing `moment`, in UTC."""
    normalized = normalize_to_utc(moment)
    return datetime(normalized.year, normalized.month, 1, tzinfo=UTC)


def shift_months(moment: datetime, months: int) -> datetime:
    """The first instant of the month `months` away from the one containing `moment`.

    Lands on a month start in both directions, which is what every monthly rebalance in this
    project anchors on. Defined here once: it was privately copied into two scripts, and a third
    needed it — the shape of every duplication this project has had to repair.
    """
    normalized = normalize_to_utc(moment)
    total = (normalized.year * MONTHS_PER_YEAR + normalized.month - 1) + months
    return datetime(total // MONTHS_PER_YEAR, total % MONTHS_PER_YEAR + 1, 1, tzinfo=UTC)


class _IsoWeekday(IntEnum):
    SATURDAY = 6
    SUNDAY = 7


CLOSED_MARKET_ISO_WEEKDAYS = frozenset({_IsoWeekday.SATURDAY, _IsoWeekday.SUNDAY})


def is_market_open(moment: datetime) -> bool:
    """Whether the currency market was trading at this moment.

    Conservative by construction: a weekday returns `True` even during thin hours, and the entire
    weekend returns `False` even where a couple of genuine trading hours sit inside it.
    """
    return normalize_to_utc(moment).isoweekday() not in CLOSED_MARKET_ISO_WEEKDAYS
