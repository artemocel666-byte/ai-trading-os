"""Read the forward ledger and say what is in it.

The counterpart to `scripts/measure_outcomes.py`. That script replays stored history and computes
outcomes now; this one reports outcomes that were committed to before they were known. When both
are run over the same recent window they should agree, and a disagreement is worth more attention
than either number on its own: it means the live path and the historical path have drifted.

Read-only. It queries, aggregates and prints, and writes nothing.
"""

import argparse
import asyncio
import json
import sys
from collections import Counter
from collections.abc import Sequence
from datetime import timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Timeframe
from app.domain.entities.forward_outcome import ForwardOutcomeRecord
from app.domain.entities.outcome import OutcomeStatistics, WindowOutcome
from app.domain.entities.pipeline_decision import PipelineDecisionStatus
from app.domain.entities.signal_contract import SignalDirection
from app.domain.outcome_measurement import aggregate_outcomes
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report the contents of the forward outcome ledger: coverage, what the rules said, "
            "and how the settled rows resolved. Read-only."
        )
    )
    parser.add_argument("--pair", default=None, help="restrict to one pair; default is all")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default=None)
    parser.add_argument("--days", type=int, default=30, help="how far back to read")
    parser.add_argument(
        "--decision-status",
        choices=[item.value for item in PipelineDecisionStatus],
        default=None,
        help="report only windows the pipeline gave this verdict",
    )
    parser.add_argument(
        "--traded-only",
        action="store_true",
        help="report only windows built entirely from traded candles",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _as_window_outcomes(records: Sequence[ForwardOutcomeRecord]) -> list[WindowOutcome]:
    """Settled rows as the entity `aggregate_outcomes` already knows how to count.

    Pending rows are excluded rather than counted as anything: a plan whose horizon has not elapsed
    has no outcome, and `NO_DATA` would claim it had one.
    """
    return [
        WindowOutcome(
            direction=record.direction,
            entry_price=record.anchor_price,
            stop_loss=record.stop_loss,
            take_profit=record.take_profit_1,
            kind=record.outcome_kind,
            bars_to_resolution=record.bars_to_resolution,
        )
        for record in records
        if record.outcome_kind is not None
    ]


def _share(value: Decimal | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.2f}%"


def _statistics_payload(statistics: OutcomeStatistics) -> dict[str, object]:
    payload: dict[str, object] = json.loads(statistics.model_dump_json())
    payload["resolved_count"] = statistics.resolved_count
    for name in ("target_first_share", "ambiguous_share", "timeout_share"):
        value: Decimal | None = getattr(statistics, name)
        payload[name] = None if value is None else str(value)
    return payload


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    pair = CurrencyPair(value=args.pair.upper()) if args.pair else None
    timeframe = Timeframe(args.timeframe.upper()) if args.timeframe else None
    settings = Settings(_env_file=None)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)

    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        async with uow_factory() as uow:
            records = await uow.forward_outcomes.list_recorded(
                pair=pair,
                timeframe=timeframe,
                start_at=start_at,
                end_at=end_at,
            )
    finally:
        await engine.dispose()

    if args.decision_status is not None:
        wanted = PipelineDecisionStatus(args.decision_status)
        records = [record for record in records if record.decision_status == wanted]
    if args.traded_only:
        records = [record for record in records if record.market_open is True]

    by_status = Counter(record.decision_status.value for record in records)
    pending = sum(1 for record in records if record.is_pending)
    statistics = {
        direction: aggregate_outcomes(
            _as_window_outcomes([item for item in records if item.direction == direction])
        )
        for direction in SignalDirection
    }
    configurations = {
        (
            record.pipeline_version,
            record.stop_multiplier,
            record.target_multiplier,
            record.horizon_candles,
        )
        for record in records
    }

    if args.format == "json":
        print(
            json.dumps(
                {
                    "pair": pair.value if pair else None,
                    "timeframe": timeframe.value if timeframe else None,
                    "days": args.days,
                    "record_count": len(records),
                    "pending_count": pending,
                    "settled_count": len(records) - pending,
                    "by_decision_status": dict(by_status),
                    "distinct_configurations": len(configurations),
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

    scope = f"{pair.value if pair else 'all pairs'} {timeframe.value if timeframe else ''}".strip()
    print(f"Forward ledger: {scope} over the last {args.days} days")
    if not records:
        print("\nNothing recorded in this window.")
        return 0

    print(f"  records: {len(records)}   settled: {len(records) - pending}   pending: {pending}")
    print(
        "  by pipeline verdict: "
        + ", ".join(f"{key}={value}" for key, value in by_status.most_common())
    )
    print(
        f"  {'dir':<8} {'settled':>8} {'target':>9} {'stop':>9} {'ambiguous':>10} "
        f"{'timeout':>9} {'target%':>10} {'ambig%':>10} {'timeout%':>9}"
    )
    for direction, item in statistics.items():
        print(
            f"  {direction.value:<8} {item.measured_count:>8} {item.target_first_count:>9} "
            f"{item.stop_first_count:>9} {item.ambiguous_count:>10} {item.timeout_count:>9} "
            f"{_share(item.target_first_share):>10} {_share(item.ambiguous_share):>10} "
            f"{_share(item.timeout_share):>9}"
        )

    if len(configurations) > 1:
        # Not a warning about a bug — a warning about a comparison. Rows written under different
        # multipliers or a different horizon are answers to different questions, and pooling them
        # is the quiet way a ledger stops meaning one thing.
        print(
            f"\n{len(configurations)} distinct configurations appear in this window. "
            "Figures above pool them; narrow the range before reading them as one sample."
        )
    print(
        "\nGross of costs: the project stores OHLC and no spread, so every figure above ignores "
        "the spread paid on entry and exit. Real results are worse."
    )
    print(
        "Both directions are recorded for every window. Neither is a recommendation, and the "
        "difference between them is the period, not skill."
    )
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
