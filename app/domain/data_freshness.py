"""Which series are behind, which were never there, and by how much.

Pure domain: newest close times in, a report out. No session, no query — the caller that reads
storage is the one place any of that lives, as in `cross_section.py` and `carry.py`.

**The weekend rule is read, never rewritten.** `expected_open_times` has been the single definition
of which bars ought to exist since Phase 9D-1, and it already knows a daily series has no Saturday.
Deriving the expected newest close from it is what keeps this module from becoming a second opinion
about the calendar — the shape of every duplication this project has had to repair.

**The calendar's deliberate over-exclusion works in our favour here.** `market_calendar` treats the
whole weekend as closed even though a few genuine hours sit inside it, so the newest bar we *expect*
is never later than the newest bar that can exist. A conservative expectation cannot raise a false
alarm; at worst it stays quiet when it could have spoken, which is the safe direction for a check
whose whole value is being believed when it does speak.
"""

from collections.abc import Mapping
from datetime import datetime, timedelta

from app.core.time import normalize_to_utc
from app.domain.entities.data_freshness import (
    DEFAULT_TOLERANCE_BARS,
    FreshnessReading,
    FreshnessReport,
    FreshnessStatus,
)
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA, expected_open_times
from app.domain.entities.market_data import Timeframe
from app.domain.readiness_engine import latest_closed_boundary

#: How far back to look for the most recent bar the calendar expects. Long enough to clear a
#: weekend plus a run of holidays, short enough that the search stays trivial.
EXPECTATION_SEARCH_WINDOW = timedelta(days=10)


def expected_newest_close(
    *,
    timeframe: Timeframe,
    as_of: datetime,
    search_window: timedelta = EXPECTATION_SEARCH_WINDOW,
) -> datetime | None:
    """The close time of the most recent bar that ought to exist by `as_of`.

    `None` when the search window holds no expected bar at all, which is reported as
    `UNDETERMINED` rather than silently treated as fresh.
    """
    end = latest_closed_boundary(timeframe=timeframe, as_of=as_of)
    opens = expected_open_times(
        timeframe=timeframe, window_start=end - search_window, window_end=end
    )
    if not opens:
        return None
    return opens[-1] + TIMEFRAME_TO_DELTA[timeframe]


def read_freshness(
    *,
    instrument: str,
    timeframe: Timeframe,
    newest_close: datetime | None,
    as_of: datetime,
    tolerance_bars: int = DEFAULT_TOLERANCE_BARS,
) -> FreshnessReading:
    """One series judged against what the calendar says should be there."""
    if tolerance_bars < 0:
        raise ValueError("a tolerance cannot be negative")

    expected = expected_newest_close(timeframe=timeframe, as_of=as_of)
    if newest_close is None:
        # Never had a bar. An absence, not a delay — see the entity module for why the distinction
        # decides whether this report is worth reading at all.
        return FreshnessReading(
            instrument=instrument,
            timeframe=timeframe,
            newest_close=None,
            expected_close=expected,
            status=FreshnessStatus.ABSENT,
        )
    if expected is None:
        return FreshnessReading(
            instrument=instrument,
            timeframe=timeframe,
            newest_close=normalize_to_utc(newest_close),
            expected_close=None,
            status=FreshnessStatus.UNDETERMINED,
        )

    held = normalize_to_utc(newest_close)
    allowance = tolerance_bars * TIMEFRAME_TO_DELTA[timeframe]
    if held >= expected - allowance:
        return FreshnessReading(
            instrument=instrument,
            timeframe=timeframe,
            newest_close=held,
            expected_close=expected,
            status=FreshnessStatus.FRESH,
        )
    return FreshnessReading(
        instrument=instrument,
        timeframe=timeframe,
        newest_close=held,
        expected_close=expected,
        status=FreshnessStatus.STALE,
        behind=expected - held,
    )


def build_freshness_report(
    newest_by_instrument: Mapping[str, datetime | None],
    *,
    timeframe: Timeframe,
    as_of: datetime,
    tolerance_bars: int = DEFAULT_TOLERANCE_BARS,
) -> FreshnessReport:
    """Every instrument judged at one moment, ordered so two runs read the same way."""
    readings = tuple(
        read_freshness(
            instrument=instrument,
            timeframe=timeframe,
            newest_close=newest_by_instrument[instrument],
            as_of=as_of,
            tolerance_bars=tolerance_bars,
        )
        for instrument in sorted(newest_by_instrument)
    )
    return FreshnessReport(as_of=normalize_to_utc(as_of), readings=readings)
