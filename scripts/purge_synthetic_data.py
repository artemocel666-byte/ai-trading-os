"""Remove rows no real provider supplied, and report exactly what would go first.

Verification scripts and the local demo seeder write into the same database the calibrations read,
under their own provider names. On 2026-08-07 that was found to have consequences:

- **30 `local-seed` EURUSD M15 candles sat on the same timestamps as real ones**, quoting 1.1005
  where the market was at 1.1441 — four hundred pips out. The feature engine de-duplicates by
  `(open_time, provider)` and keeps the first, and `local-seed` sorts before `twelve_data`, so the
  invented candle won every one of those thirty timestamps.
- **All five stored economic events were fabricated** — three demo seeds and two stubs from the
  Phase 7B verification run. The two stubs were HIGH impact and fired the event rule twelve times
  over six months of calibration.

Deleting is the smaller half of the fix. The larger half is `load_history` in
`scripts/replay_rules.py`, which now refuses to calibrate over fabricated rows at all.

**Dry run by default.** Nothing is deleted without `--confirm`, and the script prints every row it
would remove first. Take a database dump before confirming; this is not reversible from here.
"""

import argparse
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.config import Settings
from app.core.constants import REAL_MARKET_DATA_PROVIDERS
from app.persistence.database import create_engine

_TABLES = ("candles", "economic_events")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "List, and with --confirm delete, market rows whose provider is not a real one. "
            "Dry run unless --confirm is passed."
        )
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="actually delete; without it the script only reports",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


async def _survey(connection: AsyncConnection) -> dict[str, list[tuple[str, int]]]:
    survey: dict[str, list[tuple[str, int]]] = {}
    for table in _TABLES:
        rows = (
            await connection.execute(
                text(f"SELECT provider, count(*) AS n FROM {table} GROUP BY provider ORDER BY 1")
            )
        ).all()
        survey[table] = [
            (row.provider, row.n) for row in rows if row.provider not in REAL_MARKET_DATA_PROVIDERS
        ]
    return survey


async def _describe_candle_collisions(connection: AsyncConnection) -> int:
    """Fabricated candles sharing a timestamp with a real one are the dangerous kind.

    They do not merely add noise: de-duplication silently prefers whichever provider sorts first, so
    a colliding fake can replace the real observation without any issue being raised.
    """
    return (
        await connection.execute(
            text(
                """
                SELECT count(*) FROM candles fake
                JOIN candles real
                  ON real.open_time = fake.open_time
                 AND real.pair = fake.pair
                 AND real.timeframe = fake.timeframe
                WHERE fake.provider <> ALL(:real_providers)
                  AND real.provider = ANY(:real_providers)
                """
            ),
            {"real_providers": sorted(REAL_MARKET_DATA_PROVIDERS)},
        )
    ).scalar() or 0


async def _main() -> int:
    args = _parse_args()
    settings = Settings(_env_file=None)
    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        async with engine.begin() as connection:
            survey = await _survey(connection)
            collisions = await _describe_candle_collisions(connection)

            total = sum(count for rows in survey.values() for _, count in rows)
            print(f"Real providers: {', '.join(sorted(REAL_MARKET_DATA_PROVIDERS))}")
            for table, rows in survey.items():
                if not rows:
                    print(f"  {table}: nothing fabricated")
                    continue
                for provider, count in rows:
                    print(f"  {table}: {provider} -> {count} row(s)")
            if collisions:
                print(
                    f"\n{collisions} fabricated candle(s) share a timestamp with a real one. "
                    "De-duplication keeps the first provider alphabetically, so these have been "
                    "replacing real observations rather than sitting beside them."
                )
            if total == 0:
                print("\nNothing to remove.")
                return 0

            if not args.confirm:
                print(f"\nDry run: {total} row(s) would be deleted. Re-run with --confirm.")
                return 0

            for table, rows in survey.items():
                for provider, _ in rows:
                    await connection.execute(
                        text(f"DELETE FROM {table} WHERE provider = :provider"),
                        {"provider": provider},
                    )
            print(f"\nDeleted {total} row(s).")
    finally:
        await engine.dispose()
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
