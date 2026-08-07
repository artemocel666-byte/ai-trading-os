"""Judge the directional candidate against a coin toss, in-sample and out-of-sample.

The discipline this script exists to enforce: the efficiency threshold is chosen on the **first**
part of history and verified once on the **last** part, which is never used to tune anything. A
number picked after seeing the data it is judged on is not evidence.

Every proposal comes from `propose_direction` itself, asked once per threshold while the window is
still in hand. A parallel reimplementation of the candidate would measure a lookalike and say
nothing about the real one — the same rule Phase 7D-2 set for evaluating through the real
`AnalysisEngine` and composer.

Read-only: it evaluates and prints, and writes nothing.
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.direction_candidate import DEFAULT_MINIMUM_EFFICIENCY, propose_direction
from app.domain.direction_evaluation import WindowProposal, evaluate_direction
from app.domain.entities import Timeframe
from app.domain.entities.direction_evaluation import DirectionEvaluation
from app.domain.entities.outcome import WindowOutcome
from app.domain.entities.signal_contract import SignalDirection
from app.domain.outcome_measurement import DEFAULT_HORIZON_CANDLES, measure_outcome
from app.domain.rule_replay import (
    DEFAULT_STEP_CANDLES,
    DEFAULT_WINDOW_CANDLES,
    iter_replay_windows,
    order_candles,
)
from app.domain.signal_price_plan import build_price_plan
from app.domain.strategy_decision_composer import StrategyDecisionComposer
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from scripts.replay_rules import load_history, touches_closed_market

# The grid was fixed before any evaluation ran, and checked against the observed distribution of
# `market_context.move_efficiency` (median 0.28, p75 0.47, p95 0.76 on both timeframes) so that
# every value separates a real part of the sample rather than sitting off its edge.
SWEEP_THRESHOLDS = (
    Decimal("0.20"),
    Decimal("0.30"),
    Decimal("0.40"),
    Decimal("0.50"),
    Decimal("0.60"),
)
DEFAULT_SPLIT_FRACTION = Decimal("0.60")


@dataclass(frozen=True)
class MeasuredWindow:
    """One window's answers and outcomes, kept so the sweep never rebuilds a snapshot.

    `proposals` holds what `propose_direction` actually said at each threshold. Storing the answers
    rather than the inputs is what keeps this script from growing a second copy of the candidate.
    """

    proposals: dict[Decimal, SignalDirection | None]
    long_outcome: WindowOutcome
    short_outcome: WindowOutcome


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the directional candidate against a coin toss on the windows it selects. "
            "Read-only."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--window-candles", type=int, default=DEFAULT_WINDOW_CANDLES)
    parser.add_argument("--step-candles", type=int, default=DEFAULT_STEP_CANDLES)
    parser.add_argument("--horizon-candles", type=int, default=DEFAULT_HORIZON_CANDLES)
    parser.add_argument("--minimum-efficiency", type=Decimal, default=DEFAULT_MINIMUM_EFFICIENCY)
    parser.add_argument(
        "--split-fraction",
        type=Decimal,
        default=DEFAULT_SPLIT_FRACTION,
        help="share of the history used in-sample; the remainder is held out",
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="run the whole threshold grid in-sample only, printing nothing held out",
    )
    parser.add_argument(
        "--ungated",
        action="store_true",
        help="ignore pipeline readiness, measuring the hypothesis in isolation",
    )
    parser.add_argument(
        "--exclude-weekends",
        action="store_true",
        help=(
            "drop any window whose candles or forward horizon touch a weekend, when this "
            "provider's 24/7 series is carried-forward filler rather than traded prices"
        ),
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--allow-synthetic",
        action="store_true",
        help="measure rows no real provider supplied; off by default because they are invented",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _share(value: Decimal | None) -> str:
    return "-" if value is None else f"{value * 100:.2f}%"


def _edge(value: Decimal | None) -> str:
    return "-" if value is None else f"{value * 100:+.2f}"


def _header() -> str:
    return (
        f"  {'configuration':<22} {'windows':>8} {'coverage':>9} {'resolved':>9} "
        f"{'rule':>10} {'benchmark':>11} {'inverted':>10} {'edge':>8}"
    )


def _row(evaluation: DirectionEvaluation) -> str:
    return (
        f"  {evaluation.label:<22} {evaluation.window_count:>8} "
        f"{_share(evaluation.coverage):>9} {evaluation.resolved_count:>9} "
        f"{_share(evaluation.rule_share):>10} {_share(evaluation.benchmark_share):>11} "
        f"{_share(evaluation.inverted_share):>10} {_edge(evaluation.edge):>8}"
    )


async def _collect(
    args: argparse.Namespace, thresholds: tuple[Decimal, ...]
) -> list[MeasuredWindow]:
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    settings = Settings(_env_file=None)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)
    composer = StrategyDecisionComposer()

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
            raise ValueError("not enough stored candles to evaluate a single window")

        measured: list[MeasuredWindow] = []
        excluded_weekend_windows = 0
        for window in iter_replay_windows(
            pair=pair,
            timeframe=timeframe,
            ordered_candles=ordered,
            ordered_events=sorted(economic_events, key=lambda event: event.scheduled_at),
            window_candles=args.window_candles,
            step_candles=args.step_candles,
        ):
            snapshot = window.snapshot
            if args.exclude_weekends:
                # Whole windows are dropped rather than weekend candles being deleted from the
                # series: removing candles would splice Friday straight onto Monday and invent an
                # adjacency that never existed, trading one distortion for another. The span
                # checked covers the window and the whole forward horizon, so an outcome can never
                # be decided by filler even if it resolved long before reaching any.
                span_start = max(0, window.candle_index - args.window_candles + 1)
                span_end = window.candle_index + 1 + args.horizon_candles
                if touches_closed_market(ordered[span_start:span_end]):
                    excluded_weekend_windows += 1
                    continue
            long_plan = build_price_plan(SignalDirection.LONG, snapshot)
            short_plan = build_price_plan(SignalDirection.SHORT, snapshot)
            if long_plan is None or short_plan is None:
                # No levels, no outcome to measure; the window is dropped from both sides equally.
                continue

            decision = None if args.ungated else composer.compose(snapshot, snapshot.window.as_of)
            # The forward slice is Phase 9A-2's territory and stays behind its own function.
            forward = ordered[window.candle_index + 1 :]
            measured.append(
                MeasuredWindow(
                    proposals={
                        threshold: propose_direction(
                            snapshot, decision=decision, minimum_efficiency=threshold
                        )
                        for threshold in thresholds
                    },
                    long_outcome=measure_outcome(
                        SignalDirection.LONG,
                        long_plan,
                        forward,
                        horizon_candles=args.horizon_candles,
                    ),
                    short_outcome=measure_outcome(
                        SignalDirection.SHORT,
                        short_plan,
                        forward,
                        horizon_candles=args.horizon_candles,
                    ),
                )
            )
        if excluded_weekend_windows:
            print(f"Excluded {excluded_weekend_windows} window(s) touching a closed market.")
        return measured
    finally:
        await engine.dispose()


def _invert(direction: SignalDirection | None) -> SignalDirection | None:
    """The same candidate read backwards, which is how mean reversion is tested for free.

    Note the arithmetic: with the benchmark pooling both sides of each window, the inverted edge is
    always exactly the negative of the rule's. Continuation and reversion are therefore one signed
    result, not two independent chances to find something.
    """
    if direction is None:
        return None
    return SignalDirection.SHORT if direction == SignalDirection.LONG else SignalDirection.LONG


def _proposals(
    measured: list[MeasuredWindow], *, threshold: Decimal, invert: bool
) -> list[WindowProposal]:
    return [
        WindowProposal(
            proposed=_invert(item.proposals[threshold]) if invert else item.proposals[threshold],
            long_outcome=item.long_outcome,
            short_outcome=item.short_outcome,
        )
        for item in measured
    ]


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    if not (Decimal("0.1") <= args.split_fraction <= Decimal("0.9")):
        raise ValueError("--split-fraction must leave both halves usable")

    thresholds = SWEEP_THRESHOLDS if args.sweep else (args.minimum_efficiency,)
    try:
        measured = await _collect(args, thresholds)
    except ValueError as error:
        print(f"Evaluation could not run: {error}")
        return 1

    split_at = int(len(measured) * args.split_fraction)
    in_sample = measured[:split_at]
    out_of_sample = measured[split_at:]

    evaluations: list[DirectionEvaluation] = []
    if args.sweep:
        # In-sample only, deliberately: the held-out part must not be looked at while a threshold is
        # being chosen, or it stops being held out.
        for threshold in SWEEP_THRESHOLDS:
            for invert in (False, True):
                # Labelled by relation to the module, never by the name of a hypothesis. An earlier
                # version said "trend" for the un-inverted row; when the module was turned around,
                # the label silently began describing the opposite of what it measured. A label that
                # restates a fact recorded elsewhere is a label that will eventually lie.
                evaluations.append(
                    evaluate_direction(
                        _proposals(in_sample, threshold=threshold, invert=invert),
                        label=f"{'inverted' if invert else 'candidate'} >= {threshold}",
                    )
                )
    else:
        for name, sample in (("in-sample", in_sample), ("OUT-OF-SAMPLE", out_of_sample)):
            evaluations.append(
                evaluate_direction(
                    _proposals(sample, threshold=args.minimum_efficiency, invert=False),
                    label=name,
                )
            )

    if args.format == "json":
        print(
            json.dumps(
                {
                    "pair": args.pair.upper(),
                    "timeframe": args.timeframe.upper(),
                    "measured_windows": len(measured),
                    "split_at": split_at,
                    "gated_on_readiness": not args.ungated,
                    "gross_of_costs": True,
                    "evaluations": [
                        json.loads(evaluation.model_dump_json()) for evaluation in evaluations
                    ],
                },
                indent=2,
                default=str,
            )
        )
        return 0

    mode = "in-sample sweep" if args.sweep else f"threshold {args.minimum_efficiency}"
    gate = "ungated" if args.ungated else "gated on pipeline readiness"
    weekends = "weekends excluded" if args.exclude_weekends else "weekends included"
    print(
        f"Direction: {args.pair.upper()} {args.timeframe.upper()} over {args.days} days, "
        f"{mode}, {gate}, {weekends}"
    )
    print(
        f"Windows: {len(measured)} measured, split at {split_at} "
        f"({args.split_fraction} in-sample), horizon {args.horizon_candles} candles"
    )
    print(_header())
    for evaluation in evaluations:
        print(_row(evaluation))
    print(
        "\n'edge' is the rule's target-first share minus what a coin toss would have produced on "
        "the same windows, in percentage points. Gross of costs."
    )
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
