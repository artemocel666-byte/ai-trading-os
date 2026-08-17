"""Three-month interbank rates from FRED, one series per currency.

Phase 9D-3. The first adapter in this project that fetches something other than a price.

**No API key.** FRED serves each series as CSV from a public graph endpoint, which is why this was
the candidate worth checking first: the data that could break a six-null streak turned out to cost
nothing.

**Percent becomes a fraction here and only here.** The source publishes `3.84` meaning 3.84% per
annum. Every consumer downstream sees `0.0384`, because the place that knows a source's units is the
place that reads the source — the same reason candle prices are normalised in `twelve_data.py`.

**An empty value is a missing month, not a zero.** The USD series has no value for April 2020, and a
zero there would say "the rate was zero", which is false and would quietly poison an average. Such
rows are skipped and counted, the same treatment Phase 9D-1 settled on for impossible candles.
"""

import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

import httpx

from app.core.exceptions import (
    ProviderInvalidPayloadError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedRequestError,
)
from app.domain.entities.interest_rate import FRED_PROVIDER_NAME, InterestRate

logger = logging.getLogger(__name__)

PROVIDER_NAME = FRED_PROVIDER_NAME

#: OECD "Immediate rates: less than 24 hours" is a different series family; this is the three-month
#: interbank rate, which is closer to what a position is actually funded at and is published on one
#: consistent definition across all ten countries.
CURRENCY_TO_SERIES: dict[str, str] = {
    "USD": "IR3TIB01USM156N",
    "EUR": "IR3TIB01EZM156N",
    "GBP": "IR3TIB01GBM156N",
    "JPY": "IR3TIB01JPM156N",
    "CHF": "IR3TIB01CHM156N",
    "AUD": "IR3TIB01AUM156N",
    "CAD": "IR3TIB01CAM156N",
    "NZD": "IR3TIB01NZM156N",
    "NOK": "IR3TIB01NOM156N",
    "SEK": "IR3TIB01SEM156N",
}

#: The source quotes percent per annum; storage holds a fraction.
PERCENT = Decimal("100")


class FredInterestRateAdapter:
    """One CSV request per currency. Read-only, and it never writes anything."""

    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        base_url: str = "https://fred.stlouisfed.org",
        timeout: httpx.Timeout | None = None,
    ) -> None:
        self._client = client
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout or httpx.Timeout(30.0)

    async def get_monthly_rates(self, currency: str) -> Sequence[InterestRate]:
        """Every month the source publishes for one currency, oldest first."""
        code = currency.strip().upper()
        series = CURRENCY_TO_SERIES.get(code)
        if series is None:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME, details={"reason": "unknown_currency", "currency": code}
            )

        text = await self._request_series(series)
        return self._parse_series(text, currency=code, series=series)

    async def _request_series(self, series: str) -> str:
        url = f"{self._base_url}/graph/fredgraph.csv"
        try:
            response = await self._client.get(
                url, params={"id": series}, timeout=self._timeout, follow_redirects=True
            )
        except httpx.TimeoutException as error:
            raise ProviderTimeoutError(PROVIDER_NAME) from error
        except httpx.TransportError as error:
            raise ProviderUnavailableError(PROVIDER_NAME) from error
        if response.status_code >= 500:
            raise ProviderUnavailableError(
                PROVIDER_NAME, details={"status_code": response.status_code}
            )
        if response.status_code != 200:
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME,
                details={"reason": "unexpected_status", "status_code": response.status_code},
            )
        return response.text

    def _parse_series(self, text: str, *, currency: str, series: str) -> list[InterestRate]:
        lines = [line for line in text.strip().splitlines() if line.strip()]
        if len(lines) < 2:
            raise ProviderInvalidPayloadError(PROVIDER_NAME, details={"reason": "empty_series"})
        header = lines[0].split(",")
        if len(header) < 2 or header[0].strip().lower() != "observation_date":
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME, details={"reason": "unexpected_header", "series": series}
            )

        rates: list[InterestRate] = []
        skipped = 0
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) < 2:
                raise ProviderInvalidPayloadError(
                    PROVIDER_NAME, details={"reason": "short_row", "series": series}
                )
            stamp, raw = parts[0].strip(), parts[1].strip()
            if not raw or raw == ".":
                # The source leaves a month blank when it has no observation. Recording a zero
                # would state a rate that was never published.
                skipped += 1
                continue
            try:
                as_of = datetime.strptime(stamp, "%Y-%m-%d").replace(tzinfo=UTC)
                annual_rate = Decimal(raw) / PERCENT
            except (ValueError, InvalidOperation) as error:
                raise ProviderInvalidPayloadError(
                    PROVIDER_NAME, details={"reason": "unparsable_row", "series": series}
                ) from error
            rates.append(
                InterestRate(
                    provider=PROVIDER_NAME,
                    source_series=series,
                    currency=currency,
                    as_of=as_of,
                    annual_rate=annual_rate,
                )
            )

        if skipped:
            logger.warning(
                "fred left months without an observation; they are absent rather than zero",
                extra={"provider": PROVIDER_NAME, "series": series, "missing_months": skipped},
            )
        if not rates:
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME, details={"reason": "no_observations", "series": series}
            )
        rates.sort(key=lambda rate: rate.as_of)
        return rates
