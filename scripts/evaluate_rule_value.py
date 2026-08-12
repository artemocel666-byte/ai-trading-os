"""Ask whether the rules that claim something about the market earn their place.

The two halves of this project have never been crossed. `scripts/replay_rules.py` reports how often
each rule fires; `scripts/measure_outcomes.py` reports what happened after each window. This walks
history once and holds both, so a rule can be judged on the windows it passed against the windows it
failed.

**Biased in favour of the rules, on purpose, and readable only one way.** The thresholds were fitted
on this very history, so separation here proves only that the fit is self-consistent. What the run
*can* establish is the negative: a rule that fails to separate outcomes on the data it was tuned on
has no case left. Read a positive result as "not yet disproved", never as evidence.

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
from app.domain.entities.rule_value import RuleValueComparison, RuleValueReport
from app.domain.entities.signal_contract import SignalDirection
from app.domain.outcome_measurement import DEFAULT_HORIZON_CANDLES, measure_outcome
from app.domain.rule_replay import (
    DEFAULT_STEP_CANDLES,
    DEFAULT_WINDOW_CANDLES,
    iter_replay_windows,
    order_candles,
)
from app.domain.rule_value import WindowObservation, evaluate_rule_value
from app.domain.signal_price_plan import LevelMultipliers, build_price_plan
from app.domain.snapshot_review import build_snapshot_backed_review
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from scripts.replay_rules import load_history


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare, for each market-facing rule, what happened after the windows it passed "
            "against the windows it failed. Read-only."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=180)
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


def _points(value: Decimal | None) -> str:
    return "-" if value is None else f"{value * 100:+.2f}"


def _statistics_payload(statistics: OutcomeStatistics) -> dict[str, object]:
    payload: dict[str, object] = json.loads(statistics.model_dump_json())
    payload["resolved_count"] = statistics.resolved_count
    for name in ("target_first_share", "ambiguous_share", "timeout_share"):
        value: Decimal | None = getattr(statistics, name)
        payload[name] = None if value is None else str(value)
    return payload


def _comparison_payload(comparison: RuleValueComparison) -> dict[str, object]:
    return {
        "rule_id": comparison.rule_id,
        "passed_window_count": comparison.passed_window_count,
        "failed_window_count": comparison.failed_window_count,
        "failure_share": (
            None if comparison.failure_share is None else str(comparison.failure_share)
        ),
        "target_first_edge": (
            None if comparison.target_first_edge is None else str(comparison.target_first_edge)
        ),
        "timeout_edge": (None if comparison.timeout_edge is None else str(comparison.timeout_edge)),
        "passed": _statistics_payload(comparison.passed_statistics),
        "failed": _statistics_payload(comparison.failed_statistics),
    }


def _print_report(report: RuleValueReport, *, days: int, horizon: int) -> None:
    print(
        f"Rule value: {report.pair} {report.timeframe} over {days} days (horizon {horizon} candles)"
    )
    print(
        f"  windows measured {report.total_window_count}, "
        f"eligible {report.eligible_window_count} ({_share(report.eligible_share)}), "
        f"no plan {report.windows_without_a_plan}"
    )
    pooled = report.pooled_statistics
    print(
        f"  pooled over eligible windows: target {_share(pooled.target_first_share)}, "
        f"timeout {_share(pooled.timeout_share)}, ambiguous {_share(pooled.ambiguous_share)}"
    )

    print(
        f"\n  {'rule':<40} {'passed':>7} {'failed':>7} {'fires':>7} "
        f"{'target% pass':>13} {'target% fail':>13} {'edge п.п.':>10} {'timeout edge':>13}"
    )
    for comparison in report.comparisons:
        print(
            f"  {comparison.rule_id:<40} "
            f"{comparison.passed_window_count:>7} {comparison.failed_window_count:>7} "
            f"{_share(comparison.failure_share):>7} "
            f"{_share(comparison.passed_statistics.target_first_share):>13} "
            f"{_share(comparison.failed_statistics.target_first_share):>13} "
            f"{_points(comparison.target_first_edge):>10} "
            f"{_points(comparison.timeout_edge):>13}"
        )

    print(
        "\nEdge is passed minus failed on the share of resolved windows that reached a target "
        "first, both directions pooled. Positive means the rule accepted windows that resolved "
        "more decisively."
    )
    print(
        "Read the fire rate first: a rule that failed on a handful of windows has not been "
        "measured, whatever its edge says."
    )
    print(
        "This test is biased in favour of the rules — the thresholds were fitted on this same "
        "history — so it can disconfirm and cannot confirm."
    )


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    settings = Settings(_env_file=None)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)
    # A second target cannot change which level is reached first, and carrying the default would
    # make a raised target_1 fail validation. Same choice as `scripts/measure_outcomes.py`.
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

        observations: list[WindowObservation] = []
        total = 0
        without_a_plan = 0
        for window in iter_replay_windows(
            pair=pair,
            timeframe=timeframe,
            ordered_candles=ordered,
            ordered_events=sorted(economic_events, key=lambda event: event.scheduled_at),
            window_candles=args.window_candles,
            step_candles=args.step_candles,
            skip_closed_market=args.exclude_closed_market,
        ):
            total += 1
            snapshot = window.snapshot
            # The one forward slice, starting one candle after the window's own `as_of`, so nothing
            # the plan was built from is measured as its own outcome.
            forward = ordered[window.candle_index + 1 :]
            outcomes: dict[SignalDirection, WindowOutcome] = {}
            for direction in SignalDirection:
                plan = build_price_plan(direction, snapshot, multipliers=multipliers)
                if plan is None:
                    break
                outcomes[direction] = measure_outcome(
                    direction, plan, forward, horizon_candles=args.horizon_candles
                )
            if len(outcomes) != len(SignalDirection):
                # Both directions or neither: half a window would tilt the pooled statistics toward
                # whichever direction happened to produce a plan.
                without_a_plan += 1
                continue
            decision = build_snapshot_backed_review(snapshot, snapshot.window.as_of).decision
            observations.append(WindowObservation(decision=decision, outcomes=outcomes))
    except ValueError as error:
        print(f"Measurement could not run: {error}")
        return 1
    finally:
        await engine.dispose()

    report = evaluate_rule_value(
        observations,
        pair=pair.value,
        timeframe=timeframe.value,
        total_window_count=total,
        windows_without_a_plan=without_a_plan,
    )

    if args.format == "json":
        print(
            json.dumps(
                {
                    "pair": report.pair,
                    "timeframe": report.timeframe,
                    "days": args.days,
                    "horizon_candles": args.horizon_candles,
                    "total_window_count": report.total_window_count,
                    "eligible_window_count": report.eligible_window_count,
                    "windows_without_a_plan": report.windows_without_a_plan,
                    "gross_of_costs": True,
                    "in_sample": True,
                    "pooled": _statistics_payload(report.pooled_statistics),
                    "comparisons": [
                        _comparison_payload(comparison) for comparison in report.comparisons
                    ],
                },
                indent=2,
            )
        )
        return 0

    _print_report(report, days=args.days, horizon=args.horizon_candles)
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
