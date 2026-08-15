import argparse
import asyncio
import sys
from collections.abc import Sequence
from datetime import datetime, timedelta

from app.adapters.factories import create_market_data_provider, create_provider_clients
from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.currency_universe import UNIVERSE_CURRENCIES, universe_pairs
from app.domain.entities import Timeframe
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.interfaces.providers import MarketDataProvider
from app.domain.value_objects import CurrencyPair
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.services.market_data_backfill_service import (
    DEFAULT_CHUNK_CANDLES,
    DEFAULT_DELAY_SECONDS,
    MarketDataBackfillService,
    backfill_chunks,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backfill historical closed candles chunk by chunk. Run deliberately: this spends "
            "provider request quota and is never scheduled."
        )
    )
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument(
        "--universe",
        action="store_true",
        help=(
            "fill every pair the Phase 9D-1 currency universe implies instead of --pair. Each pair "
            "is probed with one small request first, so a pair the provider does not quote costs "
            "one call rather than a whole history, and is reported rather than dropped in silence"
        ),
    )
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=30, help="how far back to fill")
    parser.add_argument("--chunk-candles", type=int, default=DEFAULT_CHUNK_CANDLES)
    parser.add_argument("--delay-seconds", type=float, default=DEFAULT_DELAY_SECONDS)
    parser.add_argument(
        "--max-request-range-days",
        type=int,
        default=None,
        help=(
            "override PROVIDER_MAX_REQUEST_RANGE_DAYS. The 31-day default protects intraday "
            "requests from silent truncation; a daily series returns years in one call, and "
            "leaving it at 31 would turn a nineteen-year fill into hundreds of requests"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the chunk plan and request count without calling the provider",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _probe_available(
    provider: MarketDataProvider,
    pairs: Sequence[CurrencyPair],
    *,
    timeframe: Timeframe,
    end_at: datetime,
    delay_seconds: float,
) -> tuple[list[CurrencyPair], list[tuple[str, str]]]:
    """Ask for one small slice per pair to learn which the provider quotes at all.

    A refusal is an observation about the provider, not a reason to shrink the universe quietly:
    the caller prints both lists, so a later run over a different set of pairs is visibly different
    rather than mysteriously so.
    """
    available: list[CurrencyPair] = []
    refused: list[tuple[str, str]] = []
    probe_start = end_at - (8 * TIMEFRAME_TO_DELTA[timeframe])
    for index, pair in enumerate(pairs):
        if index:
            await asyncio.sleep(delay_seconds)
        try:
            candles = await provider.get_closed_candles(pair, timeframe, probe_start, end_at)
        except Exception as error:  # any provider refusal is exactly the answer being sought
            refused.append((pair.value, type(error).__name__))
            continue
        if candles:
            available.append(pair)
        else:
            refused.append((pair.value, "no candles returned"))
    return available, refused


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    # The override has to land in the *settings*, not beside them. The backfill service and the
    # provider each hold their own copy of this limit — the service to size a chunk, the adapter to
    # refuse an oversized request before any network call. Overriding only the service made it ask
    # for thousand-day chunks that the adapter then rejected one by one, and the run reported the
    # pairs as unavailable. One value, read twice, is the only shape that cannot disagree.
    overrides: dict[str, int] = {}
    if args.max_request_range_days is not None:
        overrides["provider_max_request_range_days"] = args.max_request_range_days
    settings = Settings(_env_file=None, **overrides)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)
    max_request_range = timedelta(days=settings.provider_max_request_range_days)

    if args.universe:
        return await _run_universe(
            args,
            settings=settings,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            max_request_range=max_request_range,
        )

    chunks = backfill_chunks(
        timeframe=timeframe,
        start_at=start_at,
        end_at=end_at,
        chunk_candles=args.chunk_candles,
        max_request_range=max_request_range,
    )
    print(
        f"Plan: {pair.value} {timeframe.value} {start_at.isoformat()}..{end_at.isoformat()} "
        f"-> {len(chunks)} request(s), delay {args.delay_seconds}s between them"
    )
    if args.dry_run:
        for index, (chunk_start, chunk_end) in enumerate(chunks, start=1):
            print(f"  [{index}] {chunk_start.isoformat()} .. {chunk_end.isoformat()}")
        print("Dry run: no provider request was made.")
        return 0

    if not settings.market_data_enabled:
        print(
            "MARKET_DATA_ENABLED is false; the disabled provider refuses before any network call."
        )
        return 1

    engine = create_engine(args.database_url or settings.database_dsn())
    clients = create_provider_clients(settings)
    try:
        service = MarketDataBackfillService(
            provider=create_market_data_provider(settings, client=clients.market_data),
            uow_factory=build_uow_factory(create_session_factory(engine)),
            chunk_candles=args.chunk_candles,
            max_request_range=max_request_range,
            delay_seconds=args.delay_seconds,
        )
        result = await service.backfill(
            pair=pair,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
        )
    finally:
        await clients.aclose()
        await engine.dispose()

    for index, chunk in enumerate(result.chunk_results, start=1):
        flags = []
        if chunk.failed:
            flags.append("FAILED")
        if chunk.possibly_truncated:
            flags.append("POSSIBLY TRUNCATED")
        suffix = f"  <- {', '.join(flags)}" if flags else ""
        print(
            f"  [{index}] {chunk.chunk_start.isoformat()} .. {chunk.chunk_end.isoformat()} "
            f"fetched={chunk.fetched_count} inserted={chunk.inserted_count} "
            f"updated={chunk.updated_count}{suffix}"
        )
    print(
        f"Total: fetched={result.total_fetched} inserted={result.total_inserted} "
        f"updated={result.total_updated} failed_chunks={result.failed_chunk_count} "
        f"truncated_chunks={result.truncated_chunk_count}"
    )
    if not result.succeeded:
        print(
            "Backfill did NOT complete cleanly. Treat the stored history as incomplete: "
            "a truncated chunk means the provider dropped the oldest bars of that range."
        )
        return 1
    print("Backfill completed cleanly.")
    return 0


async def _run_universe(
    args: argparse.Namespace,
    *,
    settings: Settings,
    timeframe: Timeframe,
    start_at: datetime,
    end_at: datetime,
    max_request_range: timedelta,
) -> int:
    pairs = universe_pairs()
    chunks_each = len(
        backfill_chunks(
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            chunk_candles=args.chunk_candles,
            max_request_range=max_request_range,
        )
    )
    print(
        f"Universe: {len(pairs)} pairs from {len(UNIVERSE_CURRENCIES)} currencies, "
        f"{timeframe.value}, {start_at.date()}..{end_at.date()}"
    )
    print(
        f"Cost: {len(pairs)} probe request(s) + up to {len(pairs)} x {chunks_each} fill "
        f"request(s), {args.delay_seconds}s apart"
    )
    if args.dry_run:
        for item in pairs:
            print(f"  {item.value}")
        print("Dry run: no provider request was made.")
        return 0

    if not settings.market_data_enabled:
        print(
            "MARKET_DATA_ENABLED is false; the disabled provider refuses before any network call."
        )
        return 1

    engine = create_engine(args.database_url or settings.database_dsn())
    clients = create_provider_clients(settings)
    filled: list[tuple[str, int, bool]] = []
    try:
        provider = create_market_data_provider(settings, client=clients.market_data)
        available, refused = await _probe_available(
            provider,
            pairs,
            timeframe=timeframe,
            end_at=end_at,
            delay_seconds=args.delay_seconds,
        )
        print(f"\nQuoted by the provider: {len(available)} of {len(pairs)}")
        for symbol, reason in refused:
            print(f"  refused  {symbol:<8} {reason}")

        service = MarketDataBackfillService(
            provider=provider,
            uow_factory=build_uow_factory(create_session_factory(engine)),
            chunk_candles=args.chunk_candles,
            max_request_range=max_request_range,
            delay_seconds=args.delay_seconds,
        )
        print()
        for item in available:
            result = await service.backfill(
                pair=item, timeframe=timeframe, start_at=start_at, end_at=end_at
            )
            filled.append((item.value, result.total_fetched, result.succeeded))
            flag = "" if result.succeeded else "  <- INCOMPLETE"
            print(
                f"  {item.value:<8} fetched={result.total_fetched:>6} "
                f"inserted={result.total_inserted:>6} updated={result.total_updated:>6}{flag}"
            )
            # Every failed chunk, named. A run that reports only *that* something broke leaves the
            # cause to be guessed from the shape of the holes, which is how a whole day was spent.
            for chunk in result.chunk_results:
                if chunk.failed:
                    print(
                        f"           FAILED {chunk.chunk_start.date()}..{chunk.chunk_end.date()} "
                        f"{chunk.failure_reason or 'unknown'}"
                    )
                elif chunk.possibly_truncated:
                    print(
                        f"           TRUNCATED? {chunk.chunk_start.date()}.."
                        f"{chunk.chunk_end.date()} first={chunk.first_candle_open_time}"
                    )
    finally:
        await clients.aclose()
        await engine.dispose()

    clean = sum(1 for _, _, succeeded in filled if succeeded)
    print(
        f"\nFilled {clean} of {len(filled)} pair(s) cleanly; "
        f"{len(pairs) - len(filled)} pair(s) the provider does not quote."
    )
    _report_coverage(filled)
    if clean != len(filled):
        print(
            "At least one pair did not complete. Treat its history as incomplete: a truncated "
            "chunk means the provider dropped the oldest bars of that range."
        )
        return 1
    return 0


#: How far below the sample's own median a pair may sit and still be called comparable. A tenth is
#: loose enough for instruments whose real histories differ by a little and tight enough to catch a
#: pair that lost a chunk: one missing chunk of seven is fourteen percent.
COVERAGE_TOLERANCE_PERCENT = 10


def coverage_shortfalls(counts: Sequence[tuple[str, int]]) -> tuple[int, list[tuple[str, int]]]:
    """The sample's median bar count, and the pairs that fall more than a tenth below it.

    The check Phase 9D-1 lacked. A fill can report success per pair and still leave a universe whose
    members cover different spans — and a cross-section over instruments silently absent in some
    years is the bias that manufactures a finding.

    Deliberately *relative*, against the sample's own median: the right absolute count depends on an
    instrument's real history, which this script has no way to know. It is a comparability test, not
    a completeness one.
    """
    if not counts:
        return (0, [])
    ordered = sorted(count for _, count in counts)
    median = ordered[(len(ordered) - 1) // 2]
    if median == 0:
        return (0, [])
    floor = median * (100 - COVERAGE_TOLERANCE_PERCENT)
    short = [(symbol, count) for symbol, count in counts if count * 100 < floor]
    return (median, sorted(short, key=lambda item: item[1]))


def _report_coverage(filled: Sequence[tuple[str, int, bool]]) -> None:
    counts = [(symbol, count) for symbol, count, _ in filled]
    median, short = coverage_shortfalls(counts)
    if median == 0:
        print("Coverage: nothing was fetched, so there is nothing to compare.")
        return
    fetched = sorted(count for _, count in counts)
    print(f"Coverage: median {median} bars per pair, range {fetched[0]}..{fetched[-1]}")
    if not short:
        print(
            f"  every pair is within {COVERAGE_TOLERANCE_PERCENT}% of the median "
            "— the universe is comparable"
        )
        return
    print(f"  {len(short)} pair(s) more than {COVERAGE_TOLERANCE_PERCENT}% short of it:")
    for symbol, count in short:
        print(f"    {symbol:<8} {count:>6} bars ({count * 100 // median}% of median)")
    print("  A cross-section is not comparable until these are equal. Do not measure on this.")


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
