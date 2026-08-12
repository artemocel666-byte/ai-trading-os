"""Show what happened after windows grouped by where a descriptive field landed.

Phase 9C-2 found the three market-facing rules separate nothing, and that two of them could barely
have: calibrated to fire on 1-10% of windows, a cut accepting 98% of a population cannot partition
it. This asks the question the rules could not — whether the *field* carries information the cut
throws away.

**Not a threshold sweep.** Sweeping cuts and keeping the best is fitting, and 9A-3 already showed
what that costs. Windows are bucketed by decile, boundaries supplied by the sample, and the whole
profile is printed rather than a winning point. Two readings are fixed in advance: a gradient (top
decile against bottom) and a band (the extremes against the middle eight), because the rule under
examination assumes a U-shape that a monotone reading would miss.

Read-only: it evaluates and prints, and writes nothing.
"""

import argparse
import asyncio
import json
import sys
from datetime import timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Timeframe
from app.domain.entities.field_outcome import FieldOutcomeProfile
from app.domain.entities.outcome import OutcomeStatistics, WindowOutcome
from app.domain.entities.signal_contract import SignalDirection
from app.domain.field_outcome_profile import FieldObservation, build_field_outcome_profile
from app.domain.outcome_measurement import DEFAULT_HORIZON_CANDLES, measure_outcome
from app.domain.rule_replay import (
    DEFAULT_STEP_CANDLES,
    DEFAULT_WINDOW_CANDLES,
    iter_replay_windows,
    order_candles,
)
from app.domain.signal_price_plan import LevelMultipliers, build_price_plan
from app.domain.strategy_field_resolver import resolve_field
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from scripts.replay_rules import load_history

#: The fields worth profiling: normalised or bounded, so a four-series criterion can be applied.
#: `market_context.max_close_drawdown` is deliberately absent — raw price units are not comparable
#: between EURUSD and NOKSEK, so agreement across instruments would mean nothing for it.
PROFILABLE_FIELDS: tuple[str, ...] = (
    "market_context.volatility_ratio",
    "market_context.max_close_excursion_atr",
    "market_context.max_close_drawdown_atr",
    "market_context.move_efficiency",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bucket windows by a field's value into deciles and report what happened after each. "
            "Read-only."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument(
        "--field",
        action="append",
        choices=PROFILABLE_FIELDS,
        default=None,
        help="repeatable; defaults to every profilable field",
    )
    parser.add_argument("--window-candles", type=int, default=DEFAULT_WINDOW_CANDLES)
    parser.add_argument("--step-candles", type=int, default=DEFAULT_STEP_CANDLES)
    parser.add_argument("--horizon-candles", type=int, default=DEFAULT_HORIZON_CANDLES)
    parser.add_argument(
        "--exclude-closed-market",
        action="store_true",
        help="measure only windows built entirely from traded candles",
    )
    parser.add_argument(
        "--cost-price",
        type=Decimal,
        default=Decimal("0"),
        help=(
            "assumed round-trip execution cost in price units, applied to every window; zero by "
            "default, and assumed rather than observed — see scripts/profile_execution_cost.py"
        ),
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _share(value: Decimal | None) -> str:
    return "-" if value is None else f"{value * 100:.2f}%"


def _points(value: Decimal | None) -> str:
    return "-" if value is None else f"{value * 100:+.2f}"


def _statistics_payload(statistics: OutcomeStatistics) -> dict[str, object]:
    payload: dict[str, object] = json.loads(statistics.model_dump_json())
    payload["resolved_count"] = statistics.resolved_count
    for name in ("target_first_share", "ambiguous_share", "timeout_share"):
        value: Decimal | None = getattr(statistics, name)
        payload[name] = None if value is None else str(value)
    return payload


def _profile_payload(profile: FieldOutcomeProfile) -> dict[str, object]:
    return {
        "field_ref": profile.field_ref,
        "total_window_count": profile.total_window_count,
        "unavailable_count": profile.unavailable_count,
        "gradient_edge": (None if profile.gradient_edge is None else str(profile.gradient_edge)),
        "band_edge": None if profile.band_edge is None else str(profile.band_edge),
        "pooled": _statistics_payload(profile.pooled_statistics),
        "deciles": [
            {
                "index": decile.index,
                "lower_bound": str(decile.lower_bound),
                "upper_bound": str(decile.upper_bound),
                "window_count": decile.window_count,
                "statistics": _statistics_payload(decile.statistics),
            }
            for decile in profile.deciles
        ],
    }


def _print_profile(profile: FieldOutcomeProfile) -> None:
    print(f"\n{profile.field_ref}  ({profile.pair} {profile.timeframe})")
    print(
        f"  windows {profile.total_window_count}, unavailable {profile.unavailable_count}, "
        f"pooled target {_share(profile.pooled_statistics.target_first_share)}"
    )
    print(
        f"  {'decile':>6} {'from':>14} {'to':>14} {'windows':>8} "
        f"{'target%':>9} {'timeout%':>9} {'ambig%':>8}"
    )
    for decile in profile.deciles:
        print(
            f"  {decile.index:>6} {decile.lower_bound:>14.6f} {decile.upper_bound:>14.6f} "
            f"{decile.window_count:>8} "
            f"{_share(decile.statistics.target_first_share):>9} "
            f"{_share(decile.statistics.timeout_share):>9} "
            f"{_share(decile.statistics.ambiguous_share):>8}"
        )
    # ASCII only: a Windows console defaults to cp1252 and raises on anything outside it.
    print(
        f"  gradient (top decile - bottom): {_points(profile.gradient_edge)} points   "
        f"band (middle eight - extremes): {_points(profile.band_edge)} points"
    )


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    fields = tuple(args.field) if args.field else PROFILABLE_FIELDS
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

        per_field: dict[str, list[FieldObservation]] = {field: [] for field in fields}
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
            outcomes: dict[SignalDirection, WindowOutcome] = {}
            for direction in SignalDirection:
                plan = build_price_plan(direction, snapshot, multipliers=multipliers)
                if plan is None:
                    break
                outcomes[direction] = measure_outcome(
                    direction,
                    plan,
                    forward,
                    horizon_candles=args.horizon_candles,
                    cost=args.cost_price,
                )
            if len(outcomes) != len(SignalDirection):
                # Both directions or neither, so a bucket cannot be tilted toward whichever
                # direction happened to produce a plan.
                continue
            for field in fields:
                resolved = resolve_field(field, snapshot)
                per_field[field].append(
                    FieldObservation(
                        value=resolved if isinstance(resolved, Decimal) else None,
                        outcomes=outcomes,
                    )
                )
    except ValueError as error:
        print(f"Measurement could not run: {error}")
        return 1
    finally:
        await engine.dispose()

    profiles = [
        build_field_outcome_profile(
            per_field[field], pair=pair.value, timeframe=timeframe.value, field_ref=field
        )
        for field in fields
    ]

    if args.format == "json":
        print(
            json.dumps(
                {
                    "pair": pair.value,
                    "timeframe": timeframe.value,
                    "days": args.days,
                    "horizon_candles": args.horizon_candles,
                    "assumed_cost": str(args.cost_price),
                    "gross_of_costs": args.cost_price == 0,
                    "profiles": [_profile_payload(profile) for profile in profiles],
                },
                indent=2,
            )
        )
        return 0

    cost_note = (
        "gross of costs"
        if args.cost_price == 0
        else f"at an assumed round-trip cost of {args.cost_price}"
    )
    print(f"Field profiles: {pair.value} {timeframe.value} over {args.days} days, {cost_note}")
    for profile in profiles:
        _print_profile(profile)
    print(
        "\nDeciles are equal in window count, not in value range, so the ten shares are comparable."
    )
    print(
        "No threshold is chosen here. A promising shape earns a cut selected on one instrument and "
        "tested once on the other, with criteria fixed first."
    )
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
