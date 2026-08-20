import asyncio
import logging
import time
from collections.abc import Sequence
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx
from pydantic import ValidationError

from app.adapters.json_decoding import decode_json_with_decimal_numbers
from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderInvalidPayloadError,
    ProviderMalformedJsonError,
    ProviderPlanRestrictedError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedRequestError,
)
from app.core.security import redact_text
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Candle, Timeframe
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA as DOMAIN_TIMEFRAME_TO_DELTA
from app.domain.value_objects import CurrencyPair

logger = logging.getLogger(__name__)

PROVIDER_NAME = "twelve_data"

#: How much of one response may be impossible before the whole response is refused.
#:
#: The rows in question are days whose close sits a few pips *outside* the bar's own high-low range
#: — not a rounding artefact, which is what this was first mistaken for, but a real inconsistency of
#: a few pips against a daily range of tens. Measured on the live provider over the same 1000-day
#: window: 1.3% of EURGBP days, 5.5% of EURSEK days. Data quality differs by pair by a factor of
#: four, which is itself worth knowing before a cross-section is built on it.
#:
#: The ceiling is deliberately set far above that, where *broken* lives rather than merely lossy: a
#: quarter of a response being impossible is a feed to refuse, five percent is a series to note.
#: Setting it just above the worst sample would be fitting a threshold to the data it must judge,
#: which is the habit this project spent five phases avoiding.
MALFORMED_ROW_TOLERANCE_PERCENT = 25

#: This provider's own name for each timeframe. Genuinely adapter-specific — another provider would
#: spell them differently — so it stays here and is the one mapping this module defines.
TIMEFRAME_TO_INTERVAL = {Timeframe.M15: "15min", Timeframe.H1: "1h", Timeframe.D1: "1day"}

#: How long a bar lasts is a fact about the timeframe, not about the provider. This module kept a
#: third copy of it until Phase 9D-1, when adding `D1` in two of the three places left the adapter
#: quietly refusing every daily request — before any network call, so the failure looked like the
#: provider not quoting the pair. Imported now, so a new timeframe can only be half-added once.
TIMEFRAME_TO_DELTA = DOMAIN_TIMEFRAME_TO_DELTA


def _parse_provider_datetime(value: object) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("provider timestamp must be a non-empty string")
    text = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=utc_now().tzinfo)
    return normalize_to_utc(parsed)


def _decimal_from_provider(value: object, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise ValueError(f"{field_name} must not be parsed from float")
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must not be boolean")
    if isinstance(value, Decimal):
        decimal_value = value
    elif isinstance(value, int):
        decimal_value = Decimal(value)
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(f"{field_name} must not be empty")
        try:
            decimal_value = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(f"{field_name} is not a valid decimal") from exc
    else:
        raise ValueError(f"{field_name} has unsupported value type")
    if not decimal_value.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return decimal_value


def _is_closed_from_provider(row: dict[str, Any], close_time: datetime) -> bool:
    if "is_closed" not in row:
        return close_time <= utc_now()
    value = row["is_closed"]
    if not isinstance(value, bool):
        raise ValueError("is_closed must be a JSON boolean")
    return value


class TwelveDataMarketDataAdapter:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        api_key: str,
        base_url: str,
        timeout: httpx.Timeout,
        retry_count: int,
        retry_backoff_seconds: float,
        max_request_range: timedelta,
        min_request_interval_seconds: float,
    ) -> None:
        self._client = client
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_backoff_seconds = retry_backoff_seconds
        self._max_request_range = max_request_range
        self._min_request_interval_seconds = min_request_interval_seconds
        # Held across the wait as well as the stamp, so two callers cannot both read the same
        # "last request" and then fire together — which is the failure this exists to prevent.
        self._request_gate = asyncio.Lock()
        self._last_request_at: float | None = None

    async def get_closed_candles(
        self,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> Sequence[Candle]:
        start_utc = normalize_to_utc(start_at)
        end_utc = normalize_to_utc(end_at)
        self._validate_request(pair, timeframe, start_utc, end_utc)
        payload = await self._request_time_series(pair, timeframe, start_utc, end_utc)
        return self._parse_candles(payload, pair, timeframe, start_utc, end_utc)

    def _validate_request(
        self,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> None:
        if not isinstance(pair, CurrencyPair):
            raise ProviderUnsupportedRequestError(PROVIDER_NAME, details={"reason": "invalid_pair"})
        if timeframe not in TIMEFRAME_TO_INTERVAL:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME,
                details={"reason": "unsupported_timeframe", "timeframe": str(timeframe)},
            )
        if start_at >= end_at:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME, details={"reason": "invalid_range"}
            )
        if end_at - start_at > self._max_request_range:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME, details={"reason": "range_too_large"}
            )

    async def _request_time_series(
        self,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> Any:
        url = f"{self._base_url}/time_series"
        params = {
            "symbol": f"{pair.base_currency}/{pair.quote_currency}",
            "interval": TIMEFRAME_TO_INTERVAL[timeframe],
            "start_date": start_at.isoformat(),
            "end_date": end_at.isoformat(),
            "format": "JSON",
            "timezone": "UTC",
        }
        headers = {"Authorization": f"apikey {self._api_key}"}
        response = await self._send_with_retries(url, params=params, headers=headers)
        try:
            payload = decode_json_with_decimal_numbers(response.content)
        except ValueError as exc:
            raise ProviderMalformedJsonError(PROVIDER_NAME) from exc
        self._raise_for_provider_payload_error(payload)
        return payload

    async def _send_with_retries(
        self,
        url: str,
        *,
        params: dict[str, str],
        headers: dict[str, str],
    ) -> httpx.Response:
        attempts = self._retry_count + 1
        last_timeout: httpx.TimeoutException | None = None
        last_transport_error: httpx.TransportError | None = None
        last_5xx_status: int | None = None
        for attempt in range(attempts):
            await self._wait_for_turn()
            try:
                response = await self._client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self._timeout,
                )
            except httpx.TimeoutException as exc:
                last_timeout = exc
                if attempt < attempts - 1:
                    await self._sleep_before_retry()
                    continue
                break
            except httpx.TransportError as exc:
                last_transport_error = exc
                if attempt < attempts - 1:
                    await self._sleep_before_retry()
                    continue
                break
            if response.status_code in (401, 403):
                raise ProviderAuthenticationError(
                    PROVIDER_NAME, details={"status_code": response.status_code}
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    PROVIDER_NAME, details={"status_code": response.status_code}
                )
            if response.status_code == 402:
                # A well-formed request the plan does not include. Distinguished from a 4xx we
                # could fix, because nothing in the request can be corrected.
                raise ProviderPlanRestrictedError(
                    PROVIDER_NAME, details={"status_code": response.status_code}
                )
            if response.status_code >= 500:
                last_5xx_status = response.status_code
                if attempt < attempts - 1:
                    await self._sleep_before_retry()
                    continue
                break
            if response.status_code >= 400:
                raise ProviderUnsupportedRequestError(
                    PROVIDER_NAME, details={"status_code": response.status_code}
                )
            return response
        if last_timeout is not None:
            raise ProviderTimeoutError(PROVIDER_NAME) from last_timeout
        if last_transport_error is not None:
            raise ProviderUnavailableError(PROVIDER_NAME) from last_transport_error
        raise ProviderUnavailableError(PROVIDER_NAME, details={"status_code": last_5xx_status})

    async def _wait_for_turn(self) -> None:
        """Hold every request at least `min_request_interval_seconds` apart.

        Phase 10-1. The daily universe job asks for forty-five pairs in one tick; fired
        back-to-back they trip a per-minute limit, and the resulting refusals arrive looking like
        provider faults rather than like our own pacing. Phase 9D-1 spent a run on that confusion
        once, when diagnostics running alongside a fill produced a real `ProviderRateLimitError`
        that took a `failure_reason` to tell apart from a malformed payload.

        A retry counts as a request, so this sits inside the retry loop rather than around it.
        """
        if self._min_request_interval_seconds <= 0:
            return
        async with self._request_gate:
            if self._last_request_at is not None:
                elapsed = time.monotonic() - self._last_request_at
                if elapsed < self._min_request_interval_seconds:
                    await asyncio.sleep(self._min_request_interval_seconds - elapsed)
            self._last_request_at = time.monotonic()

    async def _sleep_before_retry(self) -> None:
        if self._retry_backoff_seconds > 0:
            await asyncio.sleep(self._retry_backoff_seconds)

    def _raise_for_provider_payload_error(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME, details={"reason": "payload_not_object"}
            )
        if payload.get("status") != "error":
            return
        code = payload.get("code")
        message = redact_text(str(payload.get("message", "")))[:200]
        details = {"provider_code": code, "provider_message": message}
        if code in (401, 403):
            raise ProviderAuthenticationError(PROVIDER_NAME, details=details)
        if code == 429:
            raise ProviderRateLimitError(PROVIDER_NAME, details=details)
        if code in (400, 404):
            raise ProviderUnsupportedRequestError(PROVIDER_NAME, details=details)
        raise ProviderInvalidPayloadError(PROVIDER_NAME, details=details)

    def _parse_candles(
        self,
        payload: Any,
        pair: CurrencyPair,
        timeframe: Timeframe,
        start_at: datetime,
        end_at: datetime,
    ) -> list[Candle]:
        values = payload.get("values")
        if values is None:
            raise ProviderInvalidPayloadError(PROVIDER_NAME, details={"reason": "missing_values"})
        if not isinstance(values, list):
            raise ProviderInvalidPayloadError(PROVIDER_NAME, details={"reason": "values_not_list"})
        candles: list[Candle] = []
        malformed: list[str] = []
        for row in values:
            if not isinstance(row, dict):
                raise ProviderInvalidPayloadError(
                    PROVIDER_NAME, details={"reason": "row_not_object"}
                )
            try:
                open_time = _parse_provider_datetime(row["datetime"])
                close_time = (
                    _parse_provider_datetime(row["close_time"])
                    if row.get("close_time")
                    else open_time + TIMEFRAME_TO_DELTA[timeframe]
                )
                is_closed = _is_closed_from_provider(row, close_time)
                if not is_closed:
                    continue
                # Market-data inclusion policy: only fully contained closed candles are returned.
                if open_time < start_at or close_time > end_at:
                    continue
                candle = Candle(
                    provider=PROVIDER_NAME,
                    pair=pair,
                    timeframe=timeframe,
                    open_time=open_time,
                    close_time=close_time,
                    open=_decimal_from_provider(row["open"], "open"),
                    high=_decimal_from_provider(row["high"], "high"),
                    low=_decimal_from_provider(row["low"], "low"),
                    close=_decimal_from_provider(row["close"], "close"),
                    volume=(
                        _decimal_from_provider(row["volume"], "volume")
                        if row.get("volume") is not None
                        else None
                    ),
                    is_closed=True,
                )
            except (KeyError, ValueError, ValidationError) as exc:
                # One impossible row must not destroy the rest of the response. Phase 9D-1 found
                # this the expensive way: the provider emits occasional daily bars whose low sits
                # a few units of the eighth decimal *above* the close — a rounding artefact, and
                # physically impossible, so `Candle` is right to refuse it. Refusing the whole
                # payload for it left multi-year holes in most of the currency universe.
                #
                # The row is skipped and counted, never repaired: widening the low to admit the
                # close would be editing an observation, which is the one thing this project does
                # not do. What is lost is named rather than silently absent.
                malformed.append(str(row.get("datetime", "?")))
                logger.warning(
                    "twelve_data returned an impossible candle; skipping it",
                    extra={
                        "provider": PROVIDER_NAME,
                        "pair": pair.value,
                        "timeframe": timeframe.value,
                        "candle_datetime": str(row.get("datetime", "?")),
                        "reason": type(exc).__name__,
                    },
                )
                continue
            candles.append(candle)

        # A handful of artefacts is the provider being imprecise; a payload that is mostly
        # impossible is a broken feed, and tolerating it would turn this guard into decoration.
        if malformed and len(malformed) * 100 > len(values) * MALFORMED_ROW_TOLERANCE_PERCENT:
            raise ProviderInvalidPayloadError(
                PROVIDER_NAME,
                details={
                    "reason": "too_many_invalid_candles",
                    "malformed_count": len(malformed),
                    "row_count": len(values),
                },
            )
        return candles
