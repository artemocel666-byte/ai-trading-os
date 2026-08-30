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

from collections.abc import Iterable, Sequence
from decimal import Decimal

from app.domain.entities.cross_section import (
    BUCKET_COUNT,
    CrossSectionBucket,
    CrossSectionObservation,
    CrossSectionPeriod,
    CrossSectionProfile,
)


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
