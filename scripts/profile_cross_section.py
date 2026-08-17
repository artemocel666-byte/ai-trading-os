"""Rank the currency universe against itself each month and report what followed.

Phase 9D-2, and the first question this project has asked that is not about one series through time.
Five phases asked what follows a window on EURUSD and answered nothing; this asks whether the
currencies that rose most over the last three months behave differently over the next month than
those that rose least.

**Formation three months, holding one month** were fixed in the Phase 9D-1 plan, before any daily
data existed, and are not revisited here. Buckets are cut at ranks the date's own sample supplies.
Nothing in this script chooses anything.

**Costs are swept, not assumed** — the Phase 9C-4 doctrine. The grid is reported whole rather than
one flattering point.

Read-only: it evaluates and prints, and writes nothing.
"""

import argparse
import asyncio
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal

from app.core.config import Settings
from app.core.constants import REAL_MARKET_DATA_PROVIDERS
from app.core.time import normalize_to_utc, utc_now
from app.domain.cross_section import (
    build_cross_section_profile,
    forward_return,
    latest_close_at,
)
from app.domain.currency_universe import universe_pairs
from app.domain.entities import Timeframe
from app.domain.entities.cross_section import (
    BUCKET_COUNT,
    MINIMUM_T_STATISTIC,
    CrossSectionObservation,
    CrossSectionProfile,
)
from app.domain.entities.market_data import Candle
from app.domain.market_calendar import shift_months
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory

#: Round-trip cost per leg, in basis points, fixed before the run. Both legs rebalance every month,
#: so the profile charges twice this. The grid spans from free to implausibly expensive so the whole
#: curve is visible and a reader can find their own broker on it.
DEFAULT_COST_GRID_BPS: tuple[int, ...] = (0, 1, 2, 5, 10)

#: The cost the pre-registered criterion reads. Two basis points a leg is about two pips on a
#: five-decimal major — generous for a monthly rebalance in the most liquid market there is.
CRITERION_COST_BPS = 2


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rank the currency universe by trailing return each month, hold one month, and report "
            "the top-minus-bottom spread as a time series. Read-only."
        )
    )
    parser.add_argument("--formation-months", type=int, default=3)
    parser.add_argument("--holding-months", type=int, default=1)
    parser.add_argument("--bucket-count", type=int, default=BUCKET_COUNT)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _anchors(
    earliest: datetime, latest: datetime, *, formation: int, holding: int
) -> list[datetime]:
    """Month boundaries that have a full formation window behind and a full holding window ahead."""
    anchors: list[datetime] = []
    cursor = shift_months(earliest, 1)
    while True:
        if shift_months(cursor, -formation) < earliest:
            cursor = shift_months(cursor, 1)
            continue
        if shift_months(cursor, holding) > latest:
            break
        anchors.append(cursor)
        cursor = shift_months(cursor, 1)
    return anchors


def _share(value: Decimal) -> str:
    return f"{value * 100:+.3f}%"


def _profile_line(label: str, profile: CrossSectionProfile | None) -> str:
    if profile is None:
        return f"  {label:<22} no periods"
    statistic = profile.t_statistic
    error = profile.standard_error
    return (
        f"  {label:<22} periods={len(profile.periods):>4} "
        f"mean={_share(profile.mean_spread):>10} "
        f"se={'-' if error is None else f'{error * 100:.3f}%':>9} "
        f"t={'-' if statistic is None else f'{statistic:+.2f}':>7}"
    )


async def _main() -> int:
    args = _parse_args()
    if args.formation_months < 1 or args.holding_months < 1:
        raise ValueError("formation and holding must each be at least one month")
    settings = Settings(_env_file=None)
    engine = create_engine(args.database_url or settings.database_dsn())
    pairs = universe_pairs()

    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        by_pair: dict[str, list[Candle]] = {}
        async with uow_factory() as uow:
            for pair in pairs:
                candles = await uow.candles.list_range(
                    pair=pair,
                    timeframe=Timeframe.D1,
                    start_at=datetime(2000, 1, 1, tzinfo=UTC),
                    end_at=normalize_to_utc(utc_now()),
                )
                real = [
                    candle for candle in candles if candle.provider in REAL_MARKET_DATA_PROVIDERS
                ]
                real.sort(key=lambda candle: candle.close_time)
                if real:
                    by_pair[pair.value] = real
    finally:
        await engine.dispose()

    if not by_pair:
        print("No daily candles are stored. Run the Phase 9D-1 universe backfill first.")
        return 1

    earliest = min(candles[0].close_time for candles in by_pair.values())
    latest = max(candles[-1].close_time for candles in by_pair.values())
    anchors = _anchors(
        earliest, latest, formation=args.formation_months, holding=args.holding_months
    )

    observations: dict[datetime, list[CrossSectionObservation]] = defaultdict(list)
    absent = 0
    for anchor in anchors:
        formed_at = shift_months(anchor, -args.formation_months)
        settled_at = shift_months(anchor, args.holding_months)
        for symbol, candles in by_pair.items():
            start = latest_close_at(candles, formed_at)
            here = latest_close_at(candles, anchor)
            after = latest_close_at(candles, settled_at)
            if start is None or here is None or after is None:
                absent += 1
                continue
            trailing = forward_return([start, here])
            ahead = forward_return([here, after])
            if trailing is None or ahead is None:
                absent += 1
                continue
            observations[anchor].append(
                CrossSectionObservation(
                    as_of=anchor,
                    instrument=symbol,
                    field_value=trailing,
                    forward_return=ahead,
                )
            )

    grouped = [observations[anchor] for anchor in anchors if observations[anchor]]
    widths = sorted(len(group) for group in grouped)

    # Plumbing first, before any result: a cross-section that is not actually wide on most dates
    # invalidates everything after it, and reading the verdict first would make that easy to miss.
    plumbing: dict[str, object] = {
        "pairs_derived": len(pairs),
        "pairs_with_daily_history": len(by_pair),
        "history_from": str(earliest.date()),
        "history_to": str(latest.date()),
        "rebalance_dates": len(grouped),
        "instruments_per_date_min": widths[0] if widths else 0,
        "instruments_per_date_max": widths[-1] if widths else 0,
        "instrument_dates_dropped_for_missing_prices": absent,
    }
    if args.format == "text":
        print(f"Universe: {len(pairs)} pairs derived, {len(by_pair)} with stored daily history")
        print(
            f"History: {earliest.date()} .. {latest.date()}   "
            f"formation {args.formation_months}m, holding {args.holding_months}m, "
            f"{args.bucket_count} buckets"
        )
        if widths:
            print(
                f"Rebalance dates: {len(grouped)}   instruments per date: "
                f"min {widths[0]}, median {widths[len(widths) // 2]}, max {widths[-1]}   "
                f"instrument-dates dropped for missing prices: {absent}"
            )

    profiles = {
        bps: build_cross_section_profile(
            grouped,
            field_ref=f"trailing_return_{args.formation_months}m",
            bucket_count=args.bucket_count,
            cost_per_leg=Decimal(bps) / Decimal(10000),
        )
        for bps in DEFAULT_COST_GRID_BPS
    }
    gross = profiles[0]
    if gross is None:
        print("\nNo rebalance date could support the ordering; there is nothing to measure.")
        return 1

    if args.format == "json":
        print(json.dumps(_payload(profiles, args, plumbing), indent=2))
        return 0

    print("\nTop-minus-bottom spread, per month, both legs charged:")
    print(f"  {'cost/leg':<22} {'periods':>10} {'mean':>14} {'se':>12} {'t':>9}")
    for bps, profile in profiles.items():
        print(_profile_line(f"{bps} bp", profile))

    # ASCII only: a Windows console defaults to cp1252 and mangles anything outside it.
    print("\nStability, the same measurement over each half:")
    charged = profiles[CRITERION_COST_BPS]
    if charged is not None and len(charged.periods) >= 4:
        print(_profile_line("first half", charged.half(first=True)))
        print(_profile_line("second half", charged.half(first=False)))

    print("\nPre-registered criteria, all four required:")
    if charged is None:
        print("  unavailable")
    else:
        statistic = charged.t_statistic
        print(f"  mean spread positive           {charged.mean_spread > 0}")
        print(
            f"  t >= {MINIMUM_T_STATISTIC}                       "
            f"{statistic is not None and statistic >= MINIMUM_T_STATISTIC}"
        )
        stable = (
            charged.half(first=True).mean_spread > 0 and charged.half(first=False).mean_spread > 0
        )
        print(f"  same sign in both halves       {stable}")
        print(f"  survives {CRITERION_COST_BPS} bp per leg          {charged.mean_spread > 0}")
        print(f"\n  VERDICT: {'clears the bar' if charged.clears_the_bar else 'does not clear'}")

    print(
        "\nAbout 230 monthly periods make a t of 2 an annualised Sharpe near 0.45. This design can "
        "see a strong effect and cannot confirm a faint one; a null means we could not see it."
    )
    return 0


def _payload(
    profiles: dict[int, CrossSectionProfile | None],
    args: argparse.Namespace,
    plumbing: dict[str, object],
) -> dict[str, object]:
    return {
        "plumbing": plumbing,
        "formation_months": args.formation_months,
        "holding_months": args.holding_months,
        "bucket_count": args.bucket_count,
        "criterion_cost_bps": CRITERION_COST_BPS,
        "by_cost": {
            str(bps): (
                None
                if profile is None
                else {
                    "periods": len(profile.periods),
                    "mean_spread": str(profile.mean_spread),
                    "standard_error": (
                        None if profile.standard_error is None else str(profile.standard_error)
                    ),
                    "t_statistic": (
                        None if profile.t_statistic is None else str(profile.t_statistic)
                    ),
                    "clears_the_bar": profile.clears_the_bar,
                }
            )
            for bps, profile in profiles.items()
        },
    }


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
