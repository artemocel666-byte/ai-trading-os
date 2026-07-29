import argparse
import asyncio
import sys
from datetime import timedelta

from app.adapters.factories import create_market_data_provider, create_provider_clients
from app.core.config import Settings
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Timeframe
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
    parser.add_argument("--timeframe", choices=[item.value for item in Timeframe], default="M15")
    parser.add_argument("--days", type=int, default=30, help="how far back to fill")
    parser.add_argument("--chunk-candles", type=int, default=DEFAULT_CHUNK_CANDLES)
    parser.add_argument("--delay-seconds", type=float, default=DEFAULT_DELAY_SECONDS)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the chunk plan and request count without calling the provider",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _main() -> int:
    args = _parse_args()
    if args.days < 1:
        raise ValueError("--days must be at least one day")
    pair = CurrencyPair(value=args.pair.upper())
    timeframe = Timeframe(args.timeframe.upper())
    settings = Settings(_env_file=None)
    end_at = normalize_to_utc(utc_now())
    start_at = end_at - timedelta(days=args.days)
    max_request_range = timedelta(days=settings.provider_max_request_range_days)

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


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
