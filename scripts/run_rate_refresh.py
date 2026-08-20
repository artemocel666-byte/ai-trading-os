"""Refresh the interest rates once, by hand, on the same path the scheduler uses.

Phase 10-1. The weekly cron job fires on Sunday, which is right for a worker and useless when you
want to see it work now. This calls the same job the scheduler calls, so what runs here is what runs
on Sunday — a hand-rolled variant would prove something adjacent to the real thing.

For the fuller picture — months present and missing per currency, and how many rebalance anchors
have all ten — use `scripts/backfill_interest_rates.py`, which reports coverage before storing
anything. This one just brings the series up to date.

Writes rates, and only rates.
"""

import argparse
import asyncio
import sys

import httpx

from app.adapters.fred_rates import FredInterestRateAdapter
from app.core.config import get_settings
from app.domain.currency_universe import UNIVERSE_CURRENCIES
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.scheduler.jobs import interest_rate_ingestion_job
from app.services.interest_rate_ingestion_service import InterestRateIngestionService


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch and store short-term interest rates for the universe currencies."
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _main() -> int:
    args = _parse_args()
    settings = get_settings()
    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        async with httpx.AsyncClient() as client:
            await interest_rate_ingestion_job(
                InterestRateIngestionService(
                    adapter=FredInterestRateAdapter(client=client),
                    uow_factory=uow_factory,
                )
            )
    finally:
        await engine.dispose()

    print(f"Refreshed against {len(UNIVERSE_CURRENCIES)} universe currencies.")
    print("Read the per-currency counts from the log line above, or run the 9D-3 coverage report.")
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
