import asyncio
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
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedRequestError,
)
from app.core.security import redact_text
from app.core.time import normalize_to_utc, utc_now
from app.domain.entities import Candle, Timeframe
from app.domain.value_objects import CurrencyPair

PROVIDER_NAME = "twelve_data"
TIMEFRAME_TO_INTERVAL = {Timeframe.M15: "15min", Timeframe.H1: "1h"}
TIMEFRAME_TO_DELTA = {Timeframe.M15: timedelta(minutes=15), Timeframe.H1: timedelta(hours=1)}


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
    ) -> None:
        self._client = client
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retry_count = retry_count
        self._retry_backoff_seconds = retry_backoff_seconds
        self._max_request_range = max_request_range

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
                raise ProviderInvalidPayloadError(
                    PROVIDER_NAME, details={"reason": "invalid_candle"}
                ) from exc
            candles.append(candle)
        return candles
