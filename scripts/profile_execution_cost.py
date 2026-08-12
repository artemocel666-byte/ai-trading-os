"""Measure the same windows again under a range of assumed execution costs.

Every outcome figure this project has published is gross. `scripts/measure_outcomes.py` says so
under each of its tables, and `PLANS.md` has carried spread data as an open item since Phase 9A-2.
This turns that caveat into an axis.

**The cost is assumed, not observed.** The project stores OHLC and no spread. What follows is
therefore a model, and the honest form of a model is the whole curve rather than one flattering
point: a reader with a broker's quote can find their own cost on it. Nothing computed here is
written anywhere.

**Not a sweep in search of a best value.** The grid is fixed in advance and reported entire, the
same defence `scripts/profile_field_outcomes.py` makes for its deciles. Two readings are taken off
the curve, both defined before the run: the cost at which the plan drops below break-even, and the
cost worth as much target-first share as the five-point bar this project uses to call a field
informative.

Read-only: it evaluates and prints, and writes nothing.
"""

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Timeframe
from app.domain.entities.execution_cost import (
    CostReading,
    CostReadingStatus,
    CostSensitivityProfile,
)
from app.domain.entities.outcome import WindowOutcome
from app.domain.entities.signal_contract import SignalDirection
from app.domain.execution_cost import build_cost_sensitivity_profile
from app.domain.outcome_measurement import DEFAULT_HORIZON_CANDLES, measure_outcome
from app.domain.rule_replay import (
    DEFAULT_STEP_CANDLES,
    DEFAULT_WINDOW_CANDLES,
    iter_replay_windows,
    order_candles,
)
from app.domain.signal_price_plan import LevelMultipliers, build_price_plan
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from scripts.replay_rules import load_history

#: Round-trip cost in price units, fixed before any run. Both instruments the project stores are
#: quoted to five decimals, so one grid means the same thing on each. It spans from a fifth of a
#: pip to five pips; the top of it is roughly a whole average candle range on EURUSD M15 and should
#: destroy the plan outright, which is what makes it a usable sanity anchor rather than padding.
#:
#: Deliberately in price units rather than in average true ranges: a broker charges about the same
#: spread whether the market is quiet or lively, and ATR does not. The report prints the sample's
#: median ATR so the two can be converted either way.
DEFAULT_COST_GRID: tuple[Decimal, ...] = (
    Decimal("0"),
    Decimal("0.00002"),
    Decimal("0.00005"),
    Decimal("0.00010"),
    Decimal("0.00020"),
    Decimal("0.00050"),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Re-measure stored windows under a grid of assumed round-trip execution costs and "
            "report what each one costs in target-first share. Read-only."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument(
        "--cost",
        action="append",
        type=Decimal,
        default=None,
        help="repeatable round-trip cost in price units; defaults to the pre-registered grid",
    )
    parser.add_argument("--window-candles", type=int, default=DEFAULT_WINDOW_CANDLES)
    parser.add_argument("--step-candles", type=int, default=DEFAULT_STEP_CANDLES)
    parser.add_argument("--horizon-candles", type=int, default=DEFAULT_HORIZON_CANDLES)
    parser.add_argument(
        "--exclude-closed-market",
        action="store_true",
        help="measure only windows built entirely from traded candles",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _share(value: Decimal | None) -> str:
    return "-" if value is None else f"{value * 100:.2f}%"


def _median(values: Sequence[Decimal]) -> Decimal | None:
    """The middle value, or the lower of the two middles. Enough to convert a cost into ATR."""
    if not values:
        return None
    ordered = sorted(values)
    return ordered[(len(ordered) - 1) // 2]


def _reading(label: str, reading: CostReading, gross: Decimal | None, benchmark: str) -> str:
    """Printed ASCII-only: a Windows console defaults to cp1252 and raises on anything else."""
    match reading.status:
        case CostReadingStatus.FOUND:
            return f"  {label}: {reading.cost}"
        case CostReadingStatus.ALREADY_BELOW_AT_ZERO:
            return (
                f"  {label}: no cost is small enough. {_share(gross)} is already below "
                f"{benchmark} before anything was charged"
            )
        case CostReadingStatus.BEYOND_THE_GRID:
            return f"  {label}: beyond the swept grid; a wider grid would answer it"
        case CostReadingStatus.UNAVAILABLE:
            return f"  {label}: unavailable, because some point on the curve resolved nothing"


def _profile_payload(profile: CostSensitivityProfile, atr: Decimal | None) -> dict[str, object]:
    return {
        "pair": profile.pair,
        "timeframe": profile.timeframe,
        "break_even_share": str(profile.break_even_share),
        "median_average_true_range": None if atr is None else str(atr),
        "cost_is_assumed_not_observed": True,
        "break_even_cost": json.loads(profile.break_even_cost.model_dump_json()),
        "finding_equivalent_cost": json.loads(profile.finding_equivalent_cost.model_dump_json()),
        "points": [
            {
                "cost": str(point.cost),
                "measured_count": point.statistics.measured_count,
                "resolved_count": point.statistics.resolved_count,
                "target_first_share": (
                    None
                    if point.statistics.target_first_share is None
                    else str(point.statistics.target_first_share)
                ),
                "timeout_share": (
                    None
                    if point.statistics.timeout_share is None
                    else str(point.statistics.timeout_share)
                ),
                "ambiguous_share": (
                    None
                    if point.statistics.ambiguous_share is None
                    else str(point.statistics.ambiguous_share)
                ),
            }
            for point in profile.points
        ],
    }


def _print_profile(profile: CostSensitivityProfile, atr: Decimal | None, days: int) -> None:
    print(f"Execution cost sweep: {profile.pair} {profile.timeframe} over {days} days")
    print(f"Break-even target share for this geometry: {_share(profile.break_even_share)}")
    if atr is not None:
        print(f"Median average true range over the sample: {atr}")
    print(
        f"  {'cost':>10} {'cost/ATR':>9} {'measured':>9} {'resolved':>9} "
        f"{'target%':>9} {'timeout%':>9} {'ambig%':>8} {'vs b/e':>9}"
    )
    for point in profile.points:
        relative = "-" if atr is None or atr == 0 else f"{point.cost / atr:.3f}"
        share = point.statistics.target_first_share
        against = "-" if share is None else f"{(share - profile.break_even_share) * 100:+.2f}"
        print(
            f"  {point.cost:>10} {relative:>9} {point.statistics.measured_count:>9} "
            f"{point.statistics.resolved_count:>9} "
            f"{_share(share):>9} {_share(point.statistics.timeout_share):>9} "
            f"{_share(point.statistics.ambiguous_share):>8} {against:>9}"
        )

    gross = profile.zero_cost_share
    print()
    print(
        _reading(
            "break-even cost",
            profile.break_even_cost,
            gross,
            f"break-even of {_share(profile.break_even_share)}",
        )
    )
    print(
        _reading(
            "cost worth 5.00 points of target share",
            profile.finding_equivalent_cost,
            gross,
            "five points below its own gross figure",
        )
    )
    print(
        "\nThe cost is assumed, not observed: the project stores OHLC and no spread. It is a "
        "parameter of this report and is never written anywhere."
    )
    print(
        "Cost moves both levels against the position and leaves the distance between them alone, "
        "so a win and a loss still pay what they always did and only the odds change."
    )


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    costs = tuple(args.cost) if args.cost else DEFAULT_COST_GRID
    if Decimal("0") not in costs:
        raise ValueError("the grid must include a zero-cost point to measure the others against")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    settings = Settings(_env_file=None)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)
    defaults = LevelMultipliers()
    multipliers = LevelMultipliers(
        entry_band=defaults.entry_band,
        stop=defaults.stop,
        target_1=defaults.target_1,
        target_2=None,
    )

    engine = create_engine(args.database_url or settings.database_dsn())
    average_true_ranges: list[Decimal] = []
    try:
        candles, economic_events = await load_history(
            build_uow_factory(create_session_factory(engine)),
            pair=pair,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            window_candles=args.window_candles,
        )
        ordered = order_candles(candles, pair=pair, timeframe=timeframe)
        if len(ordered) < args.window_candles:
            raise ValueError("not enough stored candles to measure a single window")

        per_cost: dict[Decimal, list[WindowOutcome]] = {cost: [] for cost in costs}
        for window in iter_replay_windows(
            pair=pair,
            timeframe=timeframe,
            ordered_candles=ordered,
            ordered_events=sorted(economic_events, key=lambda event: event.scheduled_at),
            window_candles=args.window_candles,
            step_candles=args.step_candles,
            skip_closed_market=args.exclude_closed_market,
        ):
            snapshot = window.snapshot
            forward = ordered[window.candle_index + 1 :]
            plans = {
                direction: build_price_plan(direction, snapshot, multipliers=multipliers)
                for direction in SignalDirection
            }
            if any(plan is None for plan in plans.values()):
                # Both directions or neither. A curve built from windows that produced a plan for
                # only one side would carry that side's drift into every point on it.
                continue
            for cost in costs:
                for direction, plan in plans.items():
                    if plan is None:  # pragma: no cover - excluded by the check above
                        continue
                    per_cost[cost].append(
                        measure_outcome(
                            direction,
                            plan,
                            forward,
                            horizon_candles=args.horizon_candles,
                            cost=cost,
                        )
                    )
            if snapshot.feature_snapshot is not None:
                observed = snapshot.feature_snapshot.candle_summary.average_true_range
                if observed is not None:
                    average_true_ranges.append(observed)

        profile = build_cost_sensitivity_profile(
            ((cost, outcomes) for cost, outcomes in per_cost.items()),
            pair=pair.value,
            timeframe=timeframe.value,
            stop=multipliers.stop,
            target=multipliers.target_1,
        )
    except ValueError as error:
        print(f"Measurement could not run: {error}")
        return 1
    finally:
        await engine.dispose()

    median_atr = _median(average_true_ranges)
    if args.format == "json":
        print(json.dumps(_profile_payload(profile, median_atr), indent=2))
        return 0

    _print_profile(profile, median_atr, args.days)
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
