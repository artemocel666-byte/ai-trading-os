import argparse
import asyncio
import sys
from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.config import Settings
from app.core.constants import REAL_MARKET_DATA_PROVIDERS
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Candle, EconomicEvent, Timeframe
from app.domain.entities.calibration import RuleCalibrationReport
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.interfaces.unit_of_work import UnitOfWorkFactory
from app.domain.market_calendar import is_market_open
from app.domain.rule_replay import (
    DEFAULT_STEP_CANDLES,
    DEFAULT_WINDOW_CANDLES,
    replay_windows,
)
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory


def touches_closed_market(candles: Sequence[Candle]) -> bool:
    """Whether any of these candles was recorded while the market was shut.

    The definition now lives in `app/domain/market_calendar.py`, where the analysis path reads it
    too. This wrapper stays because a script needs the question asked of a *range* of candles rather
    than a moment: a window is contaminated if any candle in it is filler, not only its last one.
    """
    return not all(is_market_open(candle.open_time) for candle in candles)


def synthetic_providers(
    candles: Sequence[Candle], events: Sequence[EconomicEvent]
) -> dict[str, int]:
    """Rows in this range that no real provider supplied, counted by provider name.

    Seed and verification scripts write under their own provider names, so this needs no heuristic:
    anything outside `REAL_MARKET_DATA_PROVIDERS` was invented by us.
    """
    counts: dict[str, int] = {}
    for provider in [candle.provider for candle in candles] + [event.provider for event in events]:
        if provider not in REAL_MARKET_DATA_PROVIDERS:
            counts[provider] = counts.get(provider, 0) + 1
    return counts


async def load_history(
    uow_factory: UnitOfWorkFactory,
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    start_at: datetime,
    end_at: datetime,
    window_candles: int,
    currencies: Sequence[str] | None = None,
    allow_synthetic: bool = False,
) -> tuple[list[Candle], list[EconomicEvent]]:
    """Read the replay range once. Read-only: no upsert, no commit, nothing written back.

    **Refuses fabricated rows by default.** Every calibration this project has ever run went through
    here, and on 2026-08-07 the range was found to contain 30 seed candles quoting prices 400 pips
    from the market, plus five invented calendar events — all of which fed the Phase 7C thresholds
    and the Phase 9A-2 baseline unnoticed. Failing closed costs a flag when it is wrong and catches
    a silent corruption when it is right.
    """
    start_utc = normalize_to_utc(start_at)
    end_utc = normalize_to_utc(end_at)
    if end_utc <= start_utc:
        raise ValueError("replay end_at must be later than start_at")
    event_currencies = (
        list(currencies) if currencies is not None else [pair.base_currency, pair.quote_currency]
    )
    # The first window needs history from before start_at, otherwise the oldest windows would
    # look artificially incomplete.
    lead_in = window_candles * TIMEFRAME_TO_DELTA[timeframe]
    async with uow_factory() as uow:
        candles = await uow.candles.list_range(
            pair=pair,
            timeframe=timeframe,
            start_at=start_utc - lead_in,
            end_at=end_utc,
        )
        economic_events = await uow.economic_events.list_window(
            start_at=start_utc - lead_in,
            end_at=end_utc,
            currencies=event_currencies,
        )
    fabricated = synthetic_providers(candles, economic_events)
    if fabricated and not allow_synthetic:
        detail = ", ".join(f"{name}={count}" for name, count in sorted(fabricated.items()))
        raise ValueError(
            f"this range holds rows no real provider supplied ({detail}); "
            "run scripts/purge_synthetic_data.py, or pass --allow-synthetic to measure them anyway"
        )
    return (candles, economic_events)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay the built-in rules over stored history and report how each one behaved. "
            "Read-only: it evaluates and prints, and writes nothing."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=180, help="how far back to replay")
    parser.add_argument("--window-candles", type=int, default=DEFAULT_WINDOW_CANDLES)
    parser.add_argument("--step-candles", type=int, default=DEFAULT_STEP_CANDLES)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--allow-quiet",
        action="append",
        default=[],
        metavar="RULE_ID",
        help=(
            "acknowledge a rule that this history cannot exercise, so it does not fail the run; "
            "repeatable, and every other silent rule still fails"
        ),
    )
    parser.add_argument(
        "--exclude-closed-market",
        action="store_true",
        help=(
            "calibrate only over windows built entirely from traded candles; the provider returns "
            "a 24/7 series and about 28% of it is carried forward while the market is shut"
        ),
    )
    parser.add_argument(
        "--allow-synthetic",
        action="store_true",
        help="measure rows no real provider supplied; off by default because they are invented",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _format_decimal(value: Decimal | None) -> str:
    if value is None:
        return "-"
    quantized = value.quantize(Decimal("0.00001")).normalize()
    return f"{quantized:f}"


def _print_report(report: RuleCalibrationReport) -> None:
    print(
        f"Replay: {report.pair.value} {report.timeframe.value} "
        f"{report.replay_start.isoformat()} .. {report.replay_end.isoformat()}"
    )
    print(
        f"Windows: {report.window_count} "
        f"(window={report.window_candles} candles, step={report.step_candles})"
    )
    print(
        f"Ruleset outcomes: ready={report.ready_for_review_ruleset_count} "
        f"warned={report.warned_ruleset_count} "
        f"not_ready={report.not_ready_ruleset_count} blocked={report.blocked_ruleset_count}"
    )

    print("\nField distributions (numeric fields only):")
    header = (
        f"  {'field':<40} {'n':>7} {'n/a':>7} {'min':>12} {'p05':>12} "
        f"{'p25':>12} {'median':>12} {'p75':>12} {'p95':>12} {'max':>12}"
    )
    print(header)
    for distribution in report.distributions:
        print(
            f"  {distribution.field_ref:<40} {distribution.observed_count:>7} "
            f"{distribution.unavailable_count:>7} "
            f"{_format_decimal(distribution.minimum):>12} "
            f"{_format_decimal(distribution.p05):>12} "
            f"{_format_decimal(distribution.p25):>12} "
            f"{_format_decimal(distribution.median):>12} "
            f"{_format_decimal(distribution.p75):>12} "
            f"{_format_decimal(distribution.p95):>12} "
            f"{_format_decimal(distribution.maximum):>12}"
        )

    print("\nRule behaviour:")
    print(
        f"  {'rule':<42} {'severity':<9} {'passed':>8} {'failed':>8} "
        f"{'n/a':>8} {'fires':>8}  behaviour"
    )
    for tally in report.tallies:
        failing_share = tally.failing_share
        fires = "-" if failing_share is None else f"{failing_share * 100:.2f}%"
        print(
            f"  {tally.rule_id:<42} {tally.severity.value:<9} {tally.passed_count:>8} "
            f"{tally.failed_count:>8} {tally.unavailable_count:>8} {fires:>8}  "
            f"{tally.behaviour.value}"
        )

    dead = report.dead_rules
    if dead:
        print(
            "\nRules that never reported anything over this history "
            "(a rule that cannot fire is a defect):"
        )
        for tally in dead:
            print(f"  - {tally.rule_id} ({tally.behaviour.value})")
    else:
        print("\nEvery rule both passed and failed at least once over this history.")


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
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
        report = replay_windows(
            pair=pair,
            timeframe=timeframe,
            candles=candles,
            economic_events=economic_events,
            window_candles=args.window_candles,
            step_candles=args.step_candles,
            skip_closed_market=args.exclude_closed_market,
        )
    except ValueError as error:
        print(f"Replay could not run: {error}")
        return 1
    finally:
        await engine.dispose()

    if args.format == "json":
        print(report.model_dump_json(indent=2))
    else:
        _print_report(report)

    # A rule that never fired over real history cannot report anything, so the run is a finding
    # rather than a success — unless the operator has acknowledged that this history could not
    # exercise it, which must be a named, deliberate exception rather than a blanket flag.
    acknowledged = set(args.allow_quiet)
    unacknowledged = [tally for tally in report.dead_rules if tally.rule_id not in acknowledged]
    if unacknowledged:
        return 1
    if acknowledged:
        print(f"Acknowledged as not exercisable by this history: {', '.join(sorted(acknowledged))}")
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
