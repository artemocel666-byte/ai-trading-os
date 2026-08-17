"""Fetch and store short-term interest rates for the currency universe.

Phase 9D-3. Six pre-registered measurements returned nothing and every one read past prices; this
brings in the first data that is not a price, so that Phase 9D-4 can ask whether the interest rate
differential orders what prices alone could not.

**Coverage is reported before anything else**, the habit Phase 9D-1 paid a day to learn: months
present and missing per currency, and how many monthly rebalance anchors have all ten currencies
available under the pre-registered two-month lag. That last figure is what 9D-4 depends on, and it
belongs here rather than being discovered there.

Run deliberately. Rates move a few times a year, so there is no scheduled job and the worker is
untouched.
"""

import argparse
import asyncio
import sys
from collections import defaultdict
from datetime import UTC, datetime

import httpx

from app.adapters.fred_rates import CURRENCY_TO_SERIES, FredInterestRateAdapter
from app.core.config import Settings
from app.domain.carry import RATE_LAG_MONTHS
from app.domain.currency_universe import UNIVERSE_CURRENCIES
from app.domain.entities.interest_rate import InterestRate
from app.domain.market_calendar import shift_months
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory

#: The window Phase 9D-2 measured over, so the anchor count here is comparable to the 226 it used.
DEFAULT_FIRST_ANCHOR = datetime(2007, 10, 1, tzinfo=UTC)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch three-month interbank rates for the universe currencies and store them. "
            "Reports coverage before anything else."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="fetch and report coverage without writing anything",
    )
    parser.add_argument("--database-url", default=None)
    return parser.parse_args()


def _missing_months(months: set[datetime], first: datetime, last: datetime) -> list[datetime]:
    """Months the source skipped inside its own range — absences, not the edges of the series."""
    gaps: list[datetime] = []
    cursor = first
    while cursor <= last:
        if cursor not in months:
            gaps.append(cursor)
        cursor = shift_months(cursor, 1)
    return gaps


def _usable_anchors(
    months_by_currency: dict[str, set[datetime]], *, first_anchor: datetime, last_anchor: datetime
) -> tuple[int, int]:
    """How many monthly anchors have every currency available under the two-month lag.

    Returns the complete count and the total examined. A cross-section missing a currency on a date
    is not the same measurement as one that has them all, which is why this is counted here rather
    than assumed there.
    """
    complete = 0
    total = 0
    cursor = first_anchor
    while cursor <= last_anchor:
        total += 1
        needed = shift_months(cursor, -RATE_LAG_MONTHS)
        if all(needed in months for months in months_by_currency.values()):
            complete += 1
        cursor = shift_months(cursor, 1)
    return complete, total


def _report(fetched: dict[str, list[InterestRate]]) -> None:
    print(f"Universe: {len(UNIVERSE_CURRENCIES)} currencies, {len(fetched)} fetched")
    print(f"  {'ccy':<5} {'series':<18} {'months':>7} {'from':>10} {'to':>10} {'gaps':>5}")
    months_by_currency: dict[str, set[datetime]] = {}
    for currency in sorted(fetched):
        rates = fetched[currency]
        months = {rate.as_of for rate in rates}
        months_by_currency[currency] = months
        gaps = _missing_months(months, rates[0].as_of, rates[-1].as_of)
        print(
            f"  {currency:<5} {rates[0].source_series:<18} {len(rates):>7} "
            f"{rates[0].as_of.date()!s:>10} {rates[-1].as_of.date()!s:>10} {len(gaps):>5}"
        )
        for gap in gaps[:4]:
            print(f"        missing {gap.date()}")
        if len(gaps) > 4:
            print(f"        ... and {len(gaps) - 4} more")

    if not months_by_currency:
        return
    last_common = min(max(months) for months in months_by_currency.values())
    last_anchor = shift_months(last_common, RATE_LAG_MONTHS)
    complete, total = _usable_anchors(
        months_by_currency, first_anchor=DEFAULT_FIRST_ANCHOR, last_anchor=last_anchor
    )
    print(
        f"\nAnchors with all {len(months_by_currency)} currencies at a "
        f"{RATE_LAG_MONTHS}-month lag: {complete} of {total}   "
        f"({DEFAULT_FIRST_ANCHOR.date()} .. {last_anchor.date()})"
    )
    if complete != total:
        print(
            "  Not every anchor is complete. Phase 9D-4 must exclude the incomplete ones and say "
            "how many, rather than ranking a cross-section that is missing a currency."
        )


async def _main() -> int:
    args = _parse_args()
    settings = Settings(_env_file=None)
    fetched: dict[str, list[InterestRate]] = defaultdict(list)

    async with httpx.AsyncClient() as client:
        adapter = FredInterestRateAdapter(client=client)
        for currency in sorted(UNIVERSE_CURRENCIES):
            if currency not in CURRENCY_TO_SERIES:
                print(f"  {currency}: no series is mapped for this currency")
                continue
            try:
                rates = await adapter.get_monthly_rates(currency)
            except Exception as error:  # a refusal is the answer, and it must be named
                print(f"  {currency}: FAILED {type(error).__name__}")
                continue
            fetched[currency] = list(rates)

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
                result = await uow.interest_rates.upsert_many(fetched[currency])
                inserted += result.inserted
                updated += result.updated
            await uow.commit()
    finally:
        await engine.dispose()

    print(f"\nStored: inserted={inserted} updated={updated}")
    return 0


def main() -> None:
    sys.exit(asyncio.run(_main()))


if __name__ == "__main__":
    main()
