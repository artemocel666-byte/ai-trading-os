"""Read what is stored, for whoever needs it. Compute nothing.

Phase 11-3. Five scripts each opened a connection and wrote their own `_load`, with the same query,
the same provider filter and the same sort — differing only in how far back they asked. That was
right while each was a one-off measurement. It stops being right at a served page, which would have
been the sixth copy, and the sixth copy of anything in this project has historically been the one
that disagreed with the other five.

**This service computes nothing, and that is a rule rather than a habit.** A service that quietly
derives is how a number ends up with two definitions — the fault this project has repaired for a
timeframe delta map, a request-range limit, month arithmetic and a unit-of-work alias. Everything
here loads, filters by provenance, sorts, and hands back entities. The arithmetic lives in
`app/domain/`, where a test can reach it without a database.

**Route-ready by construction.** No `argparse`, no `print`, no `sys.exit`: it takes plain arguments
and returns plain data, so an HTTP handler can call it without a rewrite. That is asserted by a
test rather than left as an intention.

**`replay_rules.py` is deliberately not a caller.** It loads one pair on any timeframe with a
lead-in window so its oldest windows are not artificially incomplete, and economic events beside
them. That is a different question wearing a similar call, and folding it in here would force unlike
things together — the mistake avoided when the 9C-3 decile machinery was refused for a
cross-section.
"""

from datetime import UTC, datetime
from decimal import Decimal

from app.core.constants import REAL_MARKET_DATA_PROVIDERS
from app.core.time import normalize_to_utc, utc_now
from app.domain.currency_universe import UNIVERSE_CURRENCIES, universe_pairs
from app.domain.entities.market_data import Candle, Timeframe
from app.domain.entities.positioning import PositioningReading
from app.domain.interfaces.unit_of_work import UnitOfWorkFactory

#: How far back "everything" reaches. Earlier than any stored candle, so a caller asking for the
#: whole history does not have to name a date the data does not go back to anyway.
_BEGINNING = datetime(2000, 1, 1, tzinfo=UTC)


class MarketReadingService:
    """Three reads over stored data: daily candles, interest rates, positioning."""

    def __init__(self, *, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def daily_candles(self, *, since: datetime | None = None) -> dict[str, list[Candle]]:
        """Real daily candles per universe pair, oldest first, pairs with nothing omitted.

        Filtered to `REAL_MARKET_DATA_PROVIDERS` so a seeded or disabled-provider row can never
        reach a reading. A pair with no stored candle is simply absent from the mapping — the
        caller distinguishes "not quoted" from "quoted and flat", and those must not arrive
        already merged.
        """
        start_at = _BEGINNING if since is None else normalize_to_utc(since)
        end_at = normalize_to_utc(utc_now())
        by_pair: dict[str, list[Candle]] = {}
        async with self._uow_factory() as uow:
            for pair in universe_pairs():
                rows = await uow.candles.list_range(
                    pair=pair,
                    timeframe=Timeframe.D1,
                    start_at=start_at,
                    end_at=end_at,
                )
                real = [row for row in rows if row.provider in REAL_MARKET_DATA_PROVIDERS]
                real.sort(key=lambda candle: candle.close_time)
                if real:
                    by_pair[pair.value] = real
        return by_pair

    async def interest_rates(self) -> dict[str, dict[datetime, Decimal]]:
        """Every stored monthly rate per universe currency, keyed by the month it describes."""
        by_currency: dict[str, dict[datetime, Decimal]] = {}
        async with self._uow_factory() as uow:
            for currency in sorted(UNIVERSE_CURRENCIES):
                rates = await uow.interest_rates.list_range(currency=currency)
                if rates:
                    by_currency[currency] = {rate.as_of: rate.annual_rate for rate in rates}
        return by_currency

    async def positioning(self) -> dict[str, list[PositioningReading]]:
        """Every stored weekly positioning reading per currency, oldest first."""
        by_currency: dict[str, list[PositioningReading]] = {}
        async with self._uow_factory() as uow:
            for currency in sorted(UNIVERSE_CURRENCIES):
                rows = await uow.positioning.list_range(currency=currency)
                if rows:
                    by_currency[currency] = rows
        return by_currency
