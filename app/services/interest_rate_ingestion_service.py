"""Keep the stored interest rates current without anyone remembering to run a script.

Phase 10-1. Phase 9D-3 fetched ten series once, by hand, and Phase 9D-4 measured against that
snapshot. It has been going stale ever since for the same reason the daily universe was: nothing
scheduled touches it.

FRED is free and needs no key, and the series are monthly, so the whole refresh is ten requests. A
weekly tick is generous and removes the dependency on somebody's memory.

**A currency that fails is named and skipped, not fatal.** Nine refreshed series and one refusal is
a better outcome than none, and the refusal is recorded by exception type name — never by message,
because a provider message can quote a URL carrying a key.
"""

import logging

from app.adapters.fred_rates import CURRENCY_TO_SERIES, FredInterestRateAdapter
from app.domain.currency_universe import UNIVERSE_CURRENCIES
from app.domain.interfaces.unit_of_work import UnitOfWorkFactory

logger = logging.getLogger(__name__)


class InterestRateIngestionService:
    def __init__(
        self,
        *,
        adapter: FredInterestRateAdapter,
        uow_factory: UnitOfWorkFactory,
    ) -> None:
        self._adapter = adapter
        self._uow_factory = uow_factory

    async def refresh(self) -> int:
        """Fetch every mapped universe currency and store it. Returns how many succeeded.

        Storage is duplicate-safe, so a month that arrives again updates rather than duplicates —
        which is what makes re-fetching the whole series every week harmless, and what lets a source
        revision reach us as a correction to one observation rather than a second one.
        """
        succeeded = 0
        for currency in sorted(UNIVERSE_CURRENCIES):
            if currency not in CURRENCY_TO_SERIES:
                logger.warning("interest_rate_series_unmapped", extra={"currency": currency})
                continue
            try:
                rates = await self._adapter.get_monthly_rates(currency)
            except Exception as error:  # a refusal is the answer, and it must be named
                logger.warning(
                    "interest_rate_fetch_failed",
                    extra={"currency": currency, "reason": type(error).__name__},
                )
                continue
            if not rates:
                logger.warning("interest_rate_series_empty", extra={"currency": currency})
                continue
            async with self._uow_factory() as uow:
                await uow.interest_rates.upsert_many(list(rates))
                await uow.commit()
            succeeded += 1
        return succeeded
