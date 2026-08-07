"""Measure what happened after each historical window, for both directions.

The counterpart to `scripts/replay_rules.py`: that walk looks backward and scores rules, this one
looks forward and scores plans. It is the only place in the project that slices candles from after
a window's `as_of`, and it does so only once the plan for that window is already fixed.

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
from app.domain.entities.outcome import OutcomeStatistics, WindowOutcome
from app.domain.entities.signal_contract import SignalDirection
from app.domain.outcome_measurement import (
    DEFAULT_HORIZON_CANDLES,
    aggregate_outcomes,
    measure_outcome,
)
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Walk stored history, build the Phase 9A levels for each window, and record whether "
            "the target or the protective level was reached first. Read-only."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=180, help="how far back to measure")
    parser.add_argument("--window-candles", type=int, default=DEFAULT_WINDOW_CANDLES)
    parser.add_argument("--step-candles", type=int, default=DEFAULT_STEP_CANDLES)
    parser.add_argument(
        "--horizon-candles",
        type=int,
        default=DEFAULT_HORIZON_CANDLES,
        help="how many candles after the window a plan is given to resolve",
    )
    parser.add_argument("--stop-multiplier", type=Decimal, default=None)
    parser.add_argument("--target-multiplier", type=Decimal, default=None)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--allow-synthetic",
        action="store_true",
        help="measure rows no real provider supplied; off by default because they are invented",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _multipliers(args: argparse.Namespace) -> LevelMultipliers:
    """Command-line overrides on top of the Phase 9A defaults.

    Sweeping these is the point of the script: the 9A multipliers are conventions, and comparing
    outcomes across a few combinations is the first evidence they have ever had.
    """
    defaults = LevelMultipliers()
    stop = args.stop_multiplier if args.stop_multiplier is not None else defaults.stop
    target = args.target_multiplier if args.target_multiplier is not None else defaults.target_1
    # A second target has no bearing on which level is reached first, and carrying the default
    # would make target_2 <= target_1 an error on any sweep that raises target_1 past 3.
    return LevelMultipliers(
        entry_band=defaults.entry_band, stop=stop, target_1=target, target_2=None
    )


def _share(value: Decimal | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.2f}%"


def _statistics_row(label: str, statistics: OutcomeStatistics) -> str:
    average_bars = statistics.average_bars_to_resolution
    bars = "-" if average_bars is None else f"{average_bars:.1f}"
    return (
        f"  {label:<8} {statistics.measured_count:>8} {statistics.target_first_count:>9} "
        f"{statistics.stop_first_count:>9} {statistics.ambiguous_count:>10} "
        f"{statistics.timeout_count:>9} {statistics.no_data_count:>8} "
        f"{_share(statistics.target_first_share):>10} {_share(statistics.ambiguous_share):>10} "
        f"{_share(statistics.timeout_share):>9} {bars:>7}"
    )


def _statistics_payload(statistics: OutcomeStatistics) -> dict[str, object]:
    payload: dict[str, object] = json.loads(statistics.model_dump_json())
    payload["resolved_count"] = statistics.resolved_count
    payload["conservative_stop_first_count"] = statistics.conservative_stop_first_count
    for name in ("target_first_share", "ambiguous_share", "timeout_share"):
        value: Decimal | None = getattr(statistics, name)
        payload[name] = None if value is None else str(value)
    return payload


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    multipliers = _multipliers(args)
    settings = Settings(_env_file=None)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)

    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        candles, economic_events = await load_history(
            build_uow_factory(create_session_factory(engine)),
            pair=pair,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            window_candles=args.window_candles,
            allow_synthetic=args.allow_synthetic,
        )
        ordered = order_candles(candles, pair=pair, timeframe=timeframe)
        if len(ordered) < args.window_candles:
            raise ValueError("not enough stored candles to measure a single window")

        outcomes: dict[SignalDirection, list[WindowOutcome]] = {
            SignalDirection.LONG: [],
            SignalDirection.SHORT: [],
        }
        skipped: dict[SignalDirection, int] = dict.fromkeys(outcomes, 0)
        for window in iter_replay_windows(
            pair=pair,
            timeframe=timeframe,
            ordered_candles=ordered,
            ordered_events=sorted(economic_events, key=lambda event: event.scheduled_at),
            window_candles=args.window_candles,
            step_candles=args.step_candles,
        ):
            # The only forward slice in the project. It starts one candle after the window's own
            # `as_of` candle, so nothing the plan was built from is measured as its own outcome.
            forward = ordered[window.candle_index + 1 :]
            for direction in outcomes:
                plan = build_price_plan(direction, window.snapshot, multipliers=multipliers)
                if plan is None:
                    skipped[direction] += 1
                    continue
                outcomes[direction].append(
                    measure_outcome(direction, plan, forward, horizon_candles=args.horizon_candles)
                )
    except ValueError as error:
        print(f"Measurement could not run: {error}")
        return 1
    finally:
        await engine.dispose()

    statistics = {direction: aggregate_outcomes(items) for direction, items in outcomes.items()}

    if args.format == "json":
        print(
            json.dumps(
                {
                    "pair": pair.value,
                    "timeframe": timeframe.value,
                    "window_candles": args.window_candles,
                    "step_candles": args.step_candles,
                    "horizon_candles": args.horizon_candles,
                    "stop_multiplier": str(multipliers.stop),
                    "target_multiplier": str(multipliers.target_1),
                    "windows_without_a_plan": {
                        direction.value: count for direction, count in skipped.items()
                    },
                    "gross_of_costs": True,
                    "statistics": {
                        direction.value: _statistics_payload(item)
                        for direction, item in statistics.items()
                    },
                },
                indent=2,
            )
        )
        return 0

    print(
        f"Outcomes: {pair.value} {timeframe.value} over {args.days} days "
        f"(window={args.window_candles}, step={args.step_candles}, "
        f"horizon={args.horizon_candles} candles)"
    )
    print(f"Levels: stop={multipliers.stop} ATR, target={multipliers.target_1} ATR")
    print(
        f"  {'dir':<8} {'measured':>8} {'target':>9} {'stop':>9} {'ambiguous':>10} "
        f"{'timeout':>9} {'no_data':>8} {'target%':>10} {'ambig%':>10} {'timeout%':>9} "
        f"{'bars':>7}"
    )
    for direction, item in statistics.items():
        print(_statistics_row(direction.value, item))

    if any(skipped.values()):
        detail = ", ".join(f"{key.value}={count}" for key, count in skipped.items())
        print(f"\nWindows with no plan (flat or incomplete): {detail}")
    print(
        "\nGross of costs: the project stores OHLC and no spread, so every figure above ignores "
        "the spread paid on entry and exit. Real results are worse."
    )
    print(
        "'target%' is the share of resolved windows that reached the target first, with every "
        "ambiguous window counted against the plan."
    )
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
