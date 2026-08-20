"""Run the daily universe sweep once, by hand, on the same path the scheduler uses.

Phase 10-1. The cron job fires at a fixed UTC hour, which is right for a worker and useless when
you want to see the thing work now — after a deploy, after a gap, or while verifying that it works
at all. This calls exactly the job the scheduler calls, so what runs here is what runs at two in the
morning; a separate hand-rolled path would prove something adjacent to the real one.

Writes candles, and only candles. Reports the refusals by pair and by exception **type name** — a
provider message can quote a URL carrying the API key, so only the type travels.
"""

import argparse
import asyncio
import sys
import time

from app.adapters.factories import create_market_data_provider, create_provider_clients
from app.core.config import get_settings
from app.core.exceptions import ConfigurationInvalidError
from app.domain.currency_universe import universe_pairs
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.scheduler.jobs import daily_universe_ingestion_job
from app.scheduler.worker import _build_universe_ingestion_config
from app.services.data_freshness_service import DataFreshnessService
from app.services.market_data_ingestion_service import MarketDataIngestionService
from app.services.system_state_service import SystemStateService


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch daily bars for the whole currency universe once, then check freshness."
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _main() -> int:
    args = _parse_args()
    settings = get_settings()
    if not settings.market_data_enabled:
        print("MARKET_DATA_ENABLED is false; nothing would be fetched.")
        return 1

    engine = create_engine(args.database_url or settings.database_dsn())
    clients = create_provider_clients(settings)
    try:
        if clients.market_data is None:
            raise ConfigurationInvalidError("Для загрузки требуется HTTP-клиент.")
        uow_factory = build_uow_factory(create_session_factory(engine))
        system_state_service = SystemStateService(uow_factory)
        pairs = universe_pairs()

        print(
            f"Requesting {len(pairs)} pairs at >= "
            f"{settings.provider_min_request_interval_seconds}s apart "
            f"(about {len(pairs) * settings.provider_min_request_interval_seconds / 60:.1f} min)"
        )
        started = time.monotonic()
        result = await daily_universe_ingestion_job(
            MarketDataIngestionService(
                config=_build_universe_ingestion_config(settings),
                provider=create_market_data_provider(settings, client=clients.market_data),
                uow_factory=uow_factory,
                system_state_service=system_state_service,
            ),
            DataFreshnessService(
                uow_factory=uow_factory,
                system_state_service=system_state_service,
                tolerance_bars=settings.data_freshness_tolerance_bars,
            ),
            tuple(pair.value for pair in pairs),
        )
        elapsed = time.monotonic() - started
    finally:
        await clients.aclose()
        await engine.dispose()

    # The pacing floor, measured rather than assumed. A setting that is silently ignored reads as
    # protection while inviting the request count to be raised behind it.
    requests_made = len(result.item_results)
    floor = (requests_made - 1) * settings.provider_min_request_interval_seconds
    print(
        f"\nItems: {requests_made}   failed: {result.failed_item_count}   "
        f"fetched: {result.total_fetched}   inserted: {result.total_inserted}   "
        f"updated: {result.total_updated}"
    )
    print(
        f"Elapsed: {elapsed:.1f}s   pacing floor for {requests_made} requests: {floor:.1f}s   "
        f"{'OK' if elapsed >= floor else 'BELOW FLOOR'}"
    )
    for item in result.item_results:
        if item.failed:
            print(f"  REFUSED {item.pair.value:<8} {item.failure_reason}")
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
