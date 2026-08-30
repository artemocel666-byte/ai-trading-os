"""Two questions asked of a price series, and neither of them is a ranking.

Phase 11-4 moved these out of `cross_section.py`. They were written there because 9D-2 needed them
first, but they are not the cross-section: one is a simple return between two closes, the other is
"what did this cost at that moment". The ranking — the part that is structurally a direction and
that the 9D-2 safety rule keeps out of every service, route, handler and job — stayed behind.

Keeping them there had a real cost. The market page needs a move over a window and a price at a
date; importing them would have dragged the word `cross_section` into a service and forced the
safety rule to be widened to admit a module the page never touches. Moving them keeps that rule at
full strength, which is the point: **a rule should be narrowed by naming the thing it never meant
to catch, never loosened to let one caller through.**

The same lesson as `daily_returns` in Phase 11-3. A derivation more than one question needs belongs
where it can be named, not inside the first module that happened to want it.
"""

from bisect import bisect_right
from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal

from app.domain.entities.market_data import Candle


def forward_return(closes: Sequence[Decimal]) -> Decimal | None:
    """Simple return from the first close to the last.

    `None` when there is nothing to measure or the starting price is not positive — never a
    substituted zero, which would read as "it did not move" rather than "there is no answer".
    """
    if len(closes) < 2 or closes[0] <= 0:
        return None
    return (closes[-1] - closes[0]) / closes[0]


#: How stale the price standing in for a rebalance date may be. A weekend plus a holiday is four
#: days; a week is generous without letting a months-old price masquerade as a month-end one.
MAXIMUM_ANCHOR_STALENESS = timedelta(days=7)


def latest_close_at(
    ordered_candles: Sequence[Candle],
    moment: datetime,
    *,
    maximum_staleness: timedelta = MAXIMUM_ANCHOR_STALENESS,
) -> Decimal | None:
    """The last close at or before `moment`, or `None` if the nearest one is too old.

    Every instrument is priced at the **same** calendar anchor, because a cross-section compares one
    instant. Trading calendars differ, so the anchor rarely falls on a bar for every pair at once —
    the nearest earlier close stands in, and the staleness bound is what stops that convenience from
    silently comparing today's price with last quarter's.
    """
    index = bisect_right([candle.close_time for candle in ordered_candles], moment)
    if index == 0:
        return None
    candle = ordered_candles[index - 1]
    if moment - candle.close_time > maximum_staleness:
        return None
    return candle.close
