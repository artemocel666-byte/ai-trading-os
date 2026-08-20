"""Say which stored series are behind, which were never there, and by how much.

Phase 10-1. The same answer the daily job computes, readable by hand — for the moment after a fill
when you want to see the state yourself rather than wait for a log line.

Read-only: it evaluates and prints, and writes nothing. Unlike the scheduled path it records no
system error, because a person running a script is already looking.
"""

import argparse
import asyncio
import sys
from datetime import datetime

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.currency_universe import universe_pairs
from app.domain.data_freshness import build_freshness_report
from app.domain.entities.data_freshness import DEFAULT_TOLERANCE_BARS, FreshnessStatus
from app.domain.entities.market_data import Timeframe
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report how far each stored series is behind what the calendar expects. Read-only."
        )
    )
    parser.add_argument(
        "--timeframe", default=Timeframe.D1.value, choices=[t.value for t in Timeframe]
    )
    parser.add_argument("--tolerance-bars", type=int, default=DEFAULT_TOLERANCE_BARS)
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _age(newest: datetime | None, as_of: datetime) -> str:
    if newest is None:
        return "-"
    hours = (normalize_to_utc(as_of) - newest).total_seconds() / 3600
    return f"{hours:.0f}h"


async def _main() -> int:
    args = _parse_args()
    timeframe = Timeframe(args.timeframe)
    settings = Settings(_env_file=None)
    engine = create_engine(args.database_url or settings.database_dsn())
    as_of = utc_now()
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        async with uow_factory() as uow:
            newest = await uow.candles.newest_close_times(timeframe=timeframe)
    finally:
        await engine.dispose()

    instruments = tuple(pair.value for pair in universe_pairs())
    report = build_freshness_report(
        {instrument: newest.get(instrument) for instrument in instruments},
        timeframe=timeframe,
        as_of=as_of,
        tolerance_bars=args.tolerance_bars,
    )

    print(
        f"Timeframe {timeframe.value} at {as_of.isoformat(timespec='seconds')}   "
        f"tolerance {args.tolerance_bars} bar(s)"
    )
    print(
        f"  fresh={report.fresh_count}  stale={report.stale_count}  "
        f"absent={report.absent_count}  undetermined={report.undetermined_count}"
    )
    expected = next((r.expected_close for r in report.readings if r.expected_close), None)
    if expected is not None:
        print(f"  newest bar the calendar expects: {expected.isoformat(timespec='seconds')}")

    # Absences first and separately: a pair the provider does not quote is a standing fact, not a
    # problem that appeared today, and mixing it into the stale list is how a report stops
    # being read at all.
    absent = [r.instrument for r in report.readings if r.status is FreshnessStatus.ABSENT]
    if absent:
        print(f"\nNever stored ({len(absent)}): {', '.join(absent)}")

    if report.stale:
        print(f"\nBehind ({report.stale_count}):")
        print(f"  {'instrument':<10} {'newest held':<26} {'age':>6} {'behind':>10}")
        for reading in report.stale:
            behind = reading.behind
            newest_held = reading.newest_close
            print(
                f"  {reading.instrument:<10} "
                f"{'-' if newest_held is None else newest_held.isoformat(timespec='seconds'):<26} "
                f"{_age(newest_held, as_of):>6} "
                f"{'-' if behind is None else f'{behind.days}d':>10}"
            )

    print(f"\n  {'HEALTHY' if report.is_healthy else 'BEHIND'}")
    return 0 if report.is_healthy else 1


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
