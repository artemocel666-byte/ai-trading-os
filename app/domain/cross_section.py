"""Rank instruments against each other on one date, then pool the dates.

Pure domain: observations in, a profile out. No candles loaded, no session, no query — the caller
that walks history is the one place any of that lives, as in `field_outcome_profile.py` and
`execution_cost.py`.

**Ranking happens inside a date, and that is the whole point.** The Phase 9C-3 profiler sorts every
observation together and cuts buckets globally, which on this data would rank a 2008 return against
a 2015 one — a comparison through time wearing cross-sectional clothes. Reusing it here was the
obvious move and it would have been wrong.

**Nothing here chooses anything.** Buckets are cut at ranks the date's own sample supplies, and the
formation and holding periods were fixed in the Phase 9D-1 plan before any daily data existed. There
is no parameter that could be tuned to the data and then reported as a finding.
"""

from bisect import bisect_right
from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta
from decimal import Decimal

from app.domain.entities.cross_section import (
    BUCKET_COUNT,
    CrossSectionBucket,
    CrossSectionObservation,
    CrossSectionPeriod,
    CrossSectionProfile,
)
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


def rank_into_buckets(
    observations: Sequence[CrossSectionObservation],
    *,
    bucket_count: int = BUCKET_COUNT,
) -> CrossSectionPeriod | None:
    """One date's instruments, ordered by field value and cut into equal-sized buckets.

    `None` when the date cannot support the ordering — fewer instruments than buckets means at least
    one would be empty, and an empty extreme would put a zero-instrument mean into the spread.
    """
    if bucket_count < 2:
        raise ValueError("a cross-section needs at least a top and a bottom bucket")
    if len(observations) < bucket_count:
        return None

    moments = {observation.as_of for observation in observations}
    if len(moments) != 1:
        # The guard that makes this a cross-section rather than a pool. Mixing dates here is the
        # exact confusion this module exists to prevent, and it would be invisible in the output.
        raise ValueError("a cross-section ranks one moment; these observations span several")

    ordered = sorted(observations, key=lambda observation: observation.field_value)
    buckets: list[CrossSectionBucket] = []
    for index in range(bucket_count):
        start = (index * len(ordered)) // bucket_count
        end = ((index + 1) * len(ordered)) // bucket_count
        slice_ = ordered[start:end]
        if not slice_:  # pragma: no cover - excluded by the length check above
            return None
        buckets.append(
            CrossSectionBucket(
                index=len(buckets) + 1,
                instrument_count=len(slice_),
                lower_bound=slice_[0].field_value,
                upper_bound=slice_[-1].field_value,
                mean_forward_return=sum((item.forward_return for item in slice_), Decimal("0"))
                / Decimal(len(slice_)),
            )
        )

    return CrossSectionPeriod(
        as_of=next(iter(moments)),
        instrument_count=sum(bucket.instrument_count for bucket in buckets),
        buckets=tuple(buckets),
    )


def build_cross_section_profile(
    observations_by_date: Iterable[Sequence[CrossSectionObservation]],
    *,
    field_ref: str,
    bucket_count: int = BUCKET_COUNT,
    cost_per_leg: Decimal = Decimal("0"),
) -> CrossSectionProfile | None:
    """The series of per-date spreads, oldest first.

    Dates that cannot support the ordering are dropped rather than filled; the caller reports how
    many, because a run whose cross-section collapsed on half its dates is not the same measurement
    as one whose did not.
    """
    periods = [
        period
        for group in observations_by_date
        if (period := rank_into_buckets(group, bucket_count=bucket_count)) is not None
    ]
    if not periods:
        return None
    periods.sort(key=lambda period: period.as_of)
    return CrossSectionProfile(
        field_ref=field_ref,
        bucket_count=bucket_count,
        cost_per_leg=cost_per_leg,
        periods=tuple(periods),
    )
