"""Speculative positioning from the CFTC Commitments of Traders report.

Phase 10-4. The second adapter fetching something other than a price, and the last source on the
shortlist drawn up after 9D-4.

**No API key.** The CFTC serves the whole legacy futures report through a public Socrata endpoint,
133 fields a row, which is why this was worth probing before a plan was written around it.

**Mapped by contract code, never by name — and this is the finding the phase turned on.** Both
`NZ DOLLAR` and `USD INDEX` were renamed in early 2022; querying their present names returns
history starting 2022-02-01, while the codes `112741` and `098662` return 1999 and 1992 unchanged.
A name-keyed mapping would have produced two truncated series beside six complete ones, and every
percentile computed against them would have been a percentile of the wrong history — a wrong answer
wearing the shape of a real one, exactly as the half-added timeframe did in 9D-1.

**Eight of ten currencies exist here.** There is no Norwegian krone contract at all, and the only
Swedish krona one died in 1998 on an exchange that no longer exists. Those two are absences to be
named by the caller, never zeros.

**A row without open interest yields no reading.** The share this project stores is a position
divided by open interest, and a zero denominator would arrive downstream as a position of zero —
the substitution every module in this project refuses to make.
"""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

import httpx

from app.core.exceptions import (
    ProviderInvalidPayloadError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedRequestError,
)
from app.domain.entities.positioning import CFTC_PROVIDER_NAME, PositioningReading

logger = logging.getLogger(__name__)

PROVIDER_NAME = CFTC_PROVIDER_NAME

DEFAULT_BASE_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

#: Contract codes, which survive the renames the names do not. Verified at the source before this
#: file existed: every code below returns history from the 1980s or 1990s.
CURRENCY_TO_CONTRACT: dict[str, str] = {
    "EUR": "099741",
    "JPY": "097741",
    "GBP": "096742",
    "CHF": "092741",
    "CAD": "090741",
    "AUD": "232741",
    "NZD": "112741",
    "USD": "098662",
}

#: The dollar entry is an index against a basket rather than a bilateral rate, and the difference
#: has to reach the reader rather than living in somebody's memory.
BASKET_CURRENCIES: frozenset[str] = frozenset({"USD"})

#: Socrata caps a page; every series here is under two thousand rows, so one request covers it.
PAGE_LIMIT = 5000


class CftcPositioningAdapter:
    """One request per currency. Read-only, and it never writes anything."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        base_url: str = DEFAULT_BASE_URL,
        timeout: httpx.Timeout | None = None,
    ) -> None:
        self._client = client
        self._base_url = base_url
        self._timeout = timeout or httpx.Timeout(30.0)

    async def get_positioning(self, currency: str) -> Sequence[PositioningReading]:
        code = CURRENCY_TO_CONTRACT.get(currency.upper())
        if code is None:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME, details={"reason": "no_contract_mapped", "currency": currency}
            )
        payload = await self._request(code)
        return self._parse(payload, currency=currency.upper(), contract_code=code)

    async def _request(self, code: str) -> Any:
        params = {
            "$select": (
                "report_date_as_yyyy_mm_dd,cftc_contract_market_code,"
                "noncomm_positions_long_all,noncomm_positions_short_all,open_interest_all"
            ),
            "$where": f"cftc_contract_market_code='{code}'",
            "$order": "report_date_as_yyyy_mm_dd ASC",
            "$limit": str(PAGE_LIMIT),
        }
        try:
            response = await self._client.get(self._base_url, params=params, timeout=self._timeout)
        except httpx.TimeoutException as error:
            raise ProviderTimeoutError(PROVIDER_NAME) from error
        except httpx.TransportError as error:
            raise ProviderUnavailableError(PROVIDER_NAME) from error
        if response.status_code >= 500:
            raise ProviderUnavailableError(
                PROVIDER_NAME, details={"status_code": response.status_code}
            )
        if response.status_code >= 400:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME, details={"status_code": response.status_code}
            )
        try:
            return response.json()
        except ValueError as error:
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME, details={"reason": "payload_not_json"}
            ) from error

    def _parse(
        self, payload: Any, *, currency: str, contract_code: str
    ) -> Sequence[PositioningReading]:
        if not isinstance(payload, list):
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME, details={"reason": "payload_not_a_list"}
            )
        readings: list[PositioningReading] = []
        skipped = 0
        for row in payload:
            reading = self._row(row, currency=currency, contract_code=contract_code)
            if reading is None:
                skipped += 1
                continue
            readings.append(reading)
        if not readings:
            # A series that is empty throughout is a refusal, not an answer. Silence is not data.
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME, details={"reason": "series_empty", "currency": currency}
            )
        if skipped:
            logger.warning(
                "cftc_rows_skipped",
                extra={"currency": currency, "skipped": skipped, "kept": len(readings)},
            )
        return readings

    def _row(self, row: Any, *, currency: str, contract_code: str) -> PositioningReading | None:
        if not isinstance(row, dict):
            return None
        try:
            report_date = datetime.fromisoformat(str(row["report_date_as_yyyy_mm_dd"])).replace(
                tzinfo=UTC
            )
            long_side = int(row["noncomm_positions_long_all"])
            short_side = int(row["noncomm_positions_short_all"])
            open_interest = int(row["open_interest_all"])
        except (KeyError, TypeError, ValueError):
            return None
        if open_interest <= 0 or long_side < 0 or short_side < 0:
            # No denominator means no share. An absence, never a position of zero.
            return None
        return PositioningReading(
            provider=PROVIDER_NAME,
            contract_code=contract_code,
            currency=currency,
            report_date=report_date,
            noncommercial_long=long_side,
            noncommercial_short=short_side,
            open_interest=open_interest,
            is_basket=currency in BASKET_CURRENCIES,
        )
