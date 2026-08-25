"""Fetch and store speculative positioning for the currencies that have a contract.

Phase 10-4. **Coverage is reported before anything is stored**, the habit Phase 9D-1 paid a day to
learn: earliest and latest report date per currency, so a truncated series is visible immediately
rather than after a percentile has already been computed against it.

That check is not decorative here. Both `NZ DOLLAR` and `USD INDEX` were renamed in early 2022, and
a name-keyed mapping would return those two series starting 2022-02-01 while the other six run for
decades. This project maps by contract code instead, and the report below is what proves it worked.

Run deliberately. The CFTC publishes weekly, so there is no scheduled job in this slice.
"""

import argparse
import asyncio
import sys
from collections import defaultdict

import httpx

from app.adapters.cftc_positioning import CURRENCY_TO_CONTRACT, CftcPositioningAdapter
from app.core.config import Settings
from app.core.time import utc_now
from app.domain.currency_universe import UNIVERSE_CURRENCIES
from app.domain.entities.positioning import PositioningReading
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory

#: The rename happened here. Any currency whose earliest stored date is later than this while its
#: contract is older is a mapping failure, and the report says so rather than leaving it to be
#: noticed downstream.
RENAME_BOUNDARY = "2022-02-01"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch CFTC speculative positioning for the mapped currencies and store it. "
            "Reports coverage before anything else."
        )
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="fetch and report coverage without writing anything"
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _report(fetched: dict[str, list[PositioningReading]]) -> None:
    uncovered = sorted(UNIVERSE_CURRENCIES - set(CURRENCY_TO_CONTRACT))
    print(
        f"Universe: {len(UNIVERSE_CURRENCIES)} currencies, "
        f"{len(CURRENCY_TO_CONTRACT)} with a contract, {len(fetched)} fetched"
    )
    if uncovered:
        # Named, never zeroed. There is no Norwegian krone contract at all, and the only Swedish
        # krona one died in 1998 on an exchange that no longer exists.
        print(f"  no contract exists for: {', '.join(uncovered)}")

    print(f"  {'ccy':<5} {'code':<8} {'rows':>6} {'from':>12} {'to':>12} {'basket':>7}")
    suspicious: list[str] = []
    for currency in sorted(fetched):
        rows = fetched[currency]
        first = rows[0].report_date.date()
        last = rows[-1].report_date.date()
        print(
            f"  {currency:<5} {rows[0].contract_code:<8} {len(rows):>6} "
            f"{first!s:>12} {last!s:>12} {'yes' if rows[0].is_basket else 'no':>7}"
        )
        if str(first) >= RENAME_BOUNDARY:
            suspicious.append(currency)

    if suspicious:
        print(
            f"\n  WARNING: {', '.join(suspicious)} start at or after {RENAME_BOUNDARY}. "
            "That is where the contract renames happened, so this is what a name-keyed mapping "
            "looks like when it silently truncates history."
        )
    else:
        print(
            f"\n  Every series reaches back before {RENAME_BOUNDARY}, which is what mapping by "
            "contract code rather than by name buys."
        )


async def _main() -> int:
    args = _parse_args()
    settings = Settings(_env_file=None)
    fetched: dict[str, list[PositioningReading]] = defaultdict(list)

    async with httpx.AsyncClient() as client:
        adapter = CftcPositioningAdapter(client=client)
        for currency in sorted(CURRENCY_TO_CONTRACT):
            try:
                readings = await adapter.get_positioning(currency)
            except Exception as error:  # a refusal is the answer, and it must be named
                print(f"  {currency}: FAILED {type(error).__name__}")
                continue
            fetched[currency] = list(readings)

    if not fetched:
        print("Nothing was fetched; there is nothing to report or store.")
        return 1

    _report(fetched)

    if args.dry_run:
        print("\nDry run: nothing was written.")
        return 0

    engine = create_engine(args.database_url or settings.database_dsn())
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))
        inserted = 0
        updated = 0
        async with uow_factory() as uow:
            for currency in sorted(fetched):
                result = await uow.positioning.upsert_many(fetched[currency])
                inserted += result.inserted
                updated += result.updated
            await uow.commit()
    finally:
        await engine.dispose()

    print(f"\nStored: inserted={inserted} updated={updated}   at {utc_now().isoformat()}")
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
