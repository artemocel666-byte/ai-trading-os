"""Rank the currency universe by interest rate differential each month, and report what followed.

Phase 9D-4, and the first question this project has asked of something that is not a price. Six
pre-registered measurements returned nothing and every one read past prices of the instrument
itself; 9D-2 drew that boundary explicitly. This crosses it.

**Every choice here was fixed in the Phase 9D-3 plan, before a single rate was looked at**: the
two-month lag, terciles, monthly rebalance, one-month holding, total return as the headline with the
decomposition always beside it, and all four criteria. Nothing in this script chooses anything.

**The ranking is identical across the three components.** Total, spot and carry are measured over
the same buckets, cut on the same differential — a decomposition of one measurement rather than
three measurements that happen to be adjacent.

**The tail is read out loud.** Carry is the most-traded anomaly in currencies and its signature
failure is *positive mean, catastrophic tail*: it broke violently in 2008 and on the franc in 2015.
A t-statistic cannot see that, so the worst month and the worst twelve-month stretch are reported
whether or not the mean passes.

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
from app.domain.carry import (
    RATE_LAG_MONTHS,
    CarryComponent,
    build_carry_reading,
    lagged_rates_for_anchor,
    observations,
)
from app.domain.cross_section import (
    build_cross_section_profile,
    forward_return,
    latest_close_at,
)
from app.domain.currency_universe import UNIVERSE_CURRENCIES, universe_pairs
from app.domain.entities import Timeframe
from app.domain.entities.carry import CarryReading
from app.domain.entities.cross_section import (
    BUCKET_COUNT,
    MINIMUM_T_STATISTIC,
    CrossSectionProfile,
)
from app.domain.entities.market_data import Candle
from app.domain.market_calendar import shift_months
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory

#: Round-trip cost per leg in basis points, the same grid Phase 9D-2 used so the two runs are read
#: on one scale. Both legs rebalance every month, so the profile charges twice this.
DEFAULT_COST_GRID_BPS: tuple[int, ...] = (0, 1, 2, 5, 10)

#: The cost the pre-registered criterion reads.
CRITERION_COST_BPS = 2

#: The stretch the tail reading covers. Twelve months because carry's documented failures unfolded
#: over quarters rather than days, and a one-month worst case alone would understate them.
TAIL_RUN_MONTHS = 12


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rank the currency universe by lagged interest rate differential each month, hold one "
            "month, and report the top-minus-bottom spread with its decomposition. Read-only."
        )
    )
    parser.add_argument("--holding-months", type=int, default=1)
    parser.add_argument("--bucket-count", type=int, default=BUCKET_COUNT)
    parser.add_argument("--lag-months", type=int, default=RATE_LAG_MONTHS)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


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


async def _load(
    database_url: str,
) -> tuple[dict[str, list[Candle]], dict[str, dict[datetime, Decimal]]]:
    """Daily candles per pair and monthly rates per currency, both from storage only."""
    engine = create_engine(database_url)
    by_pair: dict[str, list[Candle]] = {}
    by_currency: dict[str, dict[datetime, Decimal]] = {}
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        async with uow_factory() as uow:
            for pair in universe_pairs():
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
            for currency in sorted(UNIVERSE_CURRENCIES):
                rates = await uow.interest_rates.list_range(currency=currency)
                if rates:
                    by_currency[currency] = {rate.as_of: rate.annual_rate for rate in rates}
    finally:
        await engine.dispose()
    return by_pair, by_currency


def _criteria(charged: CrossSectionProfile) -> dict[str, bool]:
    statistic = charged.t_statistic
    return {
        "mean spread positive": charged.mean_spread > 0,
        f"t >= {MINIMUM_T_STATISTIC}": statistic is not None and statistic >= MINIMUM_T_STATISTIC,
        "same sign in both halves": (
            len(charged.periods) >= 4
            and charged.half(first=True).mean_spread > 0
            and charged.half(first=False).mean_spread > 0
        ),
        f"survives {CRITERION_COST_BPS} bp per leg": charged.mean_spread > 0,
    }


async def _main() -> int:
    """One linear report, written to be read top to bottom."""
    args = _parse_args()
    if args.holding_months < 1:
        raise ValueError("a holding window is at least one month")
    settings = Settings(_env_file=None)
    by_pair, by_currency = await _load(args.database_url or settings.database_dsn())

    if not by_pair:
        print("No daily candles are stored. Run the Phase 9D-1 universe backfill first.")
        return 1
    if not by_currency:
        print("No interest rates are stored. Run the Phase 9D-3 rate backfill first.")
        return 1

    earliest = min(candles[0].close_time for candles in by_pair.values())
    latest = max(candles[-1].close_time for candles in by_pair.values())

    readings_by_anchor: dict[datetime, list[CarryReading]] = defaultdict(list)
    examined = 0
    excluded_for_rates: list[datetime] = []
    absent_prices = 0

    anchor = shift_months(earliest, 1)
    while shift_months(anchor, args.holding_months) <= latest:
        examined += 1
        rates = lagged_rates_for_anchor(
            anchor, by_currency, UNIVERSE_CURRENCIES, lag_months=args.lag_months
        )
        if rates is None:
            # Pre-registered in Phase 9D-3: the whole date goes, not the pairs that touch the
            # missing currency. One absent rate removes nine of forty-five pairs and reshapes every
            # bucket boundary, so ranking the survivors would be a different measurement.
            excluded_for_rates.append(anchor)
            anchor = shift_months(anchor, 1)
            continue
        settled_at = shift_months(anchor, args.holding_months)
        for symbol, candles in by_pair.items():
            here = latest_close_at(candles, anchor)
            after = latest_close_at(candles, settled_at)
            if here is None or after is None:
                absent_prices += 1
                continue
            spot = forward_return([here, after])
            if spot is None:
                absent_prices += 1
                continue
            readings_by_anchor[anchor].append(
                build_carry_reading(
                    anchor=anchor,
                    instrument=symbol,
                    base_currency=symbol[:3],
                    quote_currency=symbol[3:],
                    rates=rates,
                    spot_return=spot,
                    holding_months=args.holding_months,
                )
            )
        anchor = shift_months(anchor, 1)

    grouped = [
        readings_by_anchor[key] for key in sorted(readings_by_anchor) if readings_by_anchor[key]
    ]
    widths = sorted(len(group) for group in grouped)

    # Plumbing before any result. A cross-section that lost most of its dates or most of its width
    # invalidates everything after it, and reading the verdict first makes that easy to miss. In
    # JSON mode it travels inside the payload rather than ahead of it: printing it there would have
    # emitted text before the opening brace and produced output no reader could parse.
    plumbing: dict[str, object] = {
        "pairs_derived": len(universe_pairs()),
        "pairs_with_daily_history": len(by_pair),
        "currencies_with_rates": len(by_currency),
        "currencies_in_universe": len(UNIVERSE_CURRENCIES),
        "history_from": str(earliest.date()),
        "history_to": str(latest.date()),
        "anchors_examined": examined,
        "anchors_excluded_for_incomplete_rates": [str(m.date()) for m in excluded_for_rates],
        "rebalance_dates": len(grouped),
        "instruments_per_date_min": widths[0] if widths else 0,
        "instruments_per_date_max": widths[-1] if widths else 0,
        "instrument_dates_dropped_for_missing_prices": absent_prices,
    }
    if args.format == "text":
        print(f"Universe: {len(universe_pairs())} pairs derived, {len(by_pair)} with daily history")
        print(f"Rates: {len(by_currency)} of {len(UNIVERSE_CURRENCIES)} currencies stored")
        print(
            f"History: {earliest.date()} .. {latest.date()}   "
            f"lag {args.lag_months}m, holding {args.holding_months}m, {args.bucket_count} buckets"
        )
        print(
            f"Anchors examined: {examined}   "
            f"excluded for an incomplete rate cross-section: {len(excluded_for_rates)}"
        )
        for moment in excluded_for_rates[:6]:
            print(f"    excluded {moment.date()}")
        if len(excluded_for_rates) > 6:
            print(f"    ... and {len(excluded_for_rates) - 6} more")
        if widths:
            print(
                f"Rebalance dates: {len(grouped)}   instruments per date: "
                f"min {widths[0]}, median {widths[len(widths) // 2]}, max {widths[-1]}   "
                f"instrument-dates dropped for missing prices: {absent_prices}"
            )

    if not grouped:
        print("\nNo rebalance date survived; there is nothing to measure.")
        return 1

    profiles = {
        bps: build_cross_section_profile(
            [observations(group, CarryComponent.TOTAL) for group in grouped],
            field_ref="carry_differential",
            bucket_count=args.bucket_count,
            cost_per_leg=Decimal(bps) / Decimal(10000),
        )
        for bps in DEFAULT_COST_GRID_BPS
    }
    components = {
        component: build_cross_section_profile(
            [observations(group, component) for group in grouped],
            field_ref=f"carry_differential:{component}",
            bucket_count=args.bucket_count,
        )
        for component in CarryComponent
    }
    charged = profiles[CRITERION_COST_BPS]
    if charged is None or profiles[0] is None:
        print("\nNo rebalance date could support the ordering; there is nothing to measure.")
        return 1

    if args.format == "json":
        print(json.dumps(_payload(profiles, components, args, plumbing), indent=2))
        return 0

    print("\nTotal return, top-minus-bottom by carry, per month, both legs charged:")
    print(f"  {'cost/leg':<22} {'periods':>10} {'mean':>14} {'se':>12} {'t':>9}")
    for bps, profile in profiles.items():
        print(_profile_line(f"{bps} bp", profile))

    print("\nDecomposition, gross, over the same buckets:")
    for component in CarryComponent:
        print(_profile_line(str(component), components[component]))
    print(
        "  The spot and carry lines sum to the total: the same ranking measured on the two halves "
        "of one return, not three separate results."
    )

    print("\nStability, the same measurement over each half:")
    if len(charged.periods) >= 4:
        print(_profile_line("first half", charged.half(first=True)))
        print(_profile_line("second half", charged.half(first=False)))

    print(f"\nTail, at {CRITERION_COST_BPS} bp per leg — what a mean and a t cannot show:")
    for length in (1, TAIL_RUN_MONTHS):
        run = charged.worst_run(length=length)
        label = "worst month" if length == 1 else f"worst {length}-month stretch"
        if run is None:
            print(f"  {label:<22} fewer than {length} periods")
            continue
        print(
            f"  {label:<22} {_share(run.cumulative_spread):>10}   "
            f"{run.started_at.date()} .. {run.ended_at.date()}"
        )

    print("\nPre-registered criteria, all four required:")
    for label, passed in _criteria(charged).items():
        print(f"  {label:<30} {passed}")
    print(f"\n  VERDICT: {'clears the bar' if charged.clears_the_bar else 'does not clear'}")

    print(
        f"\nAbout {len(charged.periods)} monthly periods make a t of 2 an annualised Sharpe near "
        "0.45. This design can see a strong effect and cannot confirm a faint one; a null means we "
        "could not see it. A mean that passes while the tail above is ruinous is not a finding."
    )
    return 0


def _payload(
    profiles: dict[int, CrossSectionProfile | None],
    components: dict[CarryComponent, CrossSectionProfile | None],
    args: argparse.Namespace,
    plumbing: dict[str, object],
) -> dict[str, object]:
    def summarise(profile: CrossSectionProfile | None) -> dict[str, object] | None:
        if profile is None:
            return None
        worst = profile.worst_run(length=TAIL_RUN_MONTHS)
        return {
            "periods": len(profile.periods),
            "mean_spread": str(profile.mean_spread),
            "standard_error": (
                None if profile.standard_error is None else str(profile.standard_error)
            ),
            "t_statistic": (None if profile.t_statistic is None else str(profile.t_statistic)),
            "worst_run": None if worst is None else str(worst.cumulative_spread),
            "clears_the_bar": profile.clears_the_bar,
        }

    return {
        "lag_months": args.lag_months,
        "holding_months": args.holding_months,
        "bucket_count": args.bucket_count,
        "criterion_cost_bps": CRITERION_COST_BPS,
        "plumbing": plumbing,
        "by_cost": {str(bps): summarise(profile) for bps, profile in profiles.items()},
        "by_component": {str(name): summarise(profile) for name, profile in components.items()},
    }


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
