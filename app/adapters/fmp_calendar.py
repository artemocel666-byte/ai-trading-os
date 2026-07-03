import asyncio
import hashlib
import re
from collections.abc import Sequence
from datetime import datetime, timedelta
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
from app.domain.entities import EconomicEvent, EconomicImpact

PROVIDER_NAME = "fmp"
PROVIDER_EVENT_ID_FIELDS = ("id", "eventId", "event_id", "calendarId", "provider_event_id")
WHITESPACE_RE = re.compile(r"\s+")


def _parse_provider_datetime(value: object) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("provider timestamp must be a non-empty string")
    text = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        parsed = parsed.replace(tzinfo=utc_now().tzinfo)
    return normalize_to_utc(parsed)


def _impact_from_provider(value: object) -> EconomicImpact:
    text = str(value or "").strip().lower()
    if text in {"high", "h", "3"}:
        return EconomicImpact.HIGH
    if text in {"medium", "med", "m", "2"}:
        return EconomicImpact.MEDIUM
    if text in {"low", "l", "1"}:
        return EconomicImpact.LOW
    return EconomicImpact.UNKNOWN


def _required_value(row: dict[str, Any], field_names: Sequence[str], label: str) -> object:
    for field_name in field_names:
        if field_name in row:
            return row[field_name]
    raise ValueError(f"missing required provider field: {label}")


def _required_text(row: dict[str, Any], field_names: Sequence[str], label: str) -> str:
    value = _required_value(row, field_names, label)
    text = str(value).strip() if value is not None else ""
    if not text:
        raise ValueError(f"blank required provider field: {label}")
    return text


def _normalized_identity_text(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value.strip()).casefold()


def _stable_provider_event_id(row: dict[str, Any]) -> str | None:
    for field_name in PROVIDER_EVENT_ID_FIELDS:
        value = row.get(field_name)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _derive_provider_event_id(
    *,
    scheduled_at: datetime,
    currency: str,
    country: str,
    title: str,
) -> str:
    canonical = "|".join(
        (
            PROVIDER_NAME,
            normalize_to_utc(scheduled_at).isoformat(),
            currency.upper(),
            _normalized_identity_text(country),
            _normalized_identity_text(title),
        )
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class FMPEconomicCalendarAdapter:
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

    async def get_events(
        self,
        start_at: datetime,
        end_at: datetime,
        currencies: Sequence[str] | None = None,
    ) -> Sequence[EconomicEvent]:
        start_utc = normalize_to_utc(start_at)
        end_utc = normalize_to_utc(end_at)
        self._validate_request(start_utc, end_utc, currencies)
        payload = await self._request_calendar(start_utc, end_utc, currencies)
        return self._parse_events(payload, start_utc, end_utc, currencies)

    def _validate_request(
        self,
        start_at: datetime,
        end_at: datetime,
        currencies: Sequence[str] | None,
    ) -> None:
        if start_at >= end_at:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME, details={"reason": "invalid_range"}
            )
        if end_at - start_at > self._max_request_range:
            raise ProviderUnsupportedRequestError(
                PROVIDER_NAME, details={"reason": "range_too_large"}
            )
        if currencies is not None:
            for currency in currencies:
                if len(currency) != 3 or not currency.isalpha() or currency.upper() != currency:
                    raise ProviderUnsupportedRequestError(
                        PROVIDER_NAME,
                        details={"reason": "invalid_currency"},
                    )

    async def _request_calendar(
        self,
        start_at: datetime,
        end_at: datetime,
        currencies: Sequence[str] | None,
    ) -> Any:
        url = f"{self._base_url}/stable/economic-calendar"
        params = {
            "from": start_at.date().isoformat(),
            "to": end_at.date().isoformat(),
            "apikey": self._api_key,
        }
        if currencies:
            params["currencies"] = ",".join(currencies)
        response = await self._send_with_retries(url, params=params)
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
            raise ProviderTimeoutError(PROVIDER_NAME) from None
        if last_transport_error is not None:
            raise ProviderUnavailableError(PROVIDER_NAME) from None
        raise ProviderUnavailableError(PROVIDER_NAME, details={"status_code": last_5xx_status})

    async def _sleep_before_retry(self) -> None:
        if self._retry_backoff_seconds > 0:
            await asyncio.sleep(self._retry_backoff_seconds)

    def _raise_for_provider_payload_error(self, payload: Any) -> None:
        if isinstance(payload, dict) and payload.get("Error Message"):
            message = redact_text(str(payload.get("Error Message", "")))[:200]
            raise ProviderAuthenticationError(PROVIDER_NAME, details={"provider_message": message})
        if isinstance(payload, dict) and payload.get("status") == "error":
            code = payload.get("code")
            message = redact_text(str(payload.get("message", "")))[:200]
            details = {"provider_code": code, "provider_message": message}
            if code in (401, 403):
                raise ProviderAuthenticationError(PROVIDER_NAME, details=details)
            if code == 429:
                raise ProviderRateLimitError(PROVIDER_NAME, details=details)
            raise ProviderInvalidPayloadError(PROVIDER_NAME, details=details)

    def _parse_events(
        self,
        payload: Any,
        start_at: datetime,
        end_at: datetime,
        currencies: Sequence[str] | None,
    ) -> list[EconomicEvent]:
        if not isinstance(payload, list):
            raise ProviderInvalidPayloadError(PROVIDER_NAME, details={"reason": "payload_not_list"})
        events: list[EconomicEvent] = []
        for row in payload:
            if not isinstance(row, dict):
                raise ProviderInvalidPayloadError(
                    PROVIDER_NAME, details={"reason": "row_not_object"}
                )
            try:
                scheduled_at = _parse_provider_datetime(
                    _required_value(row, ("date", "scheduled_at"), "scheduled timestamp")
                )
                title = _required_text(row, ("event", "title"), "event title")
                country = _required_text(row, ("country",), "country")
                currency = _required_text(row, ("currency",), "currency").upper()
                if currencies is not None and currency not in currencies:
                    continue
                if scheduled_at < start_at or scheduled_at >= end_at:
                    continue
                forecast = _required_value(row, ("estimate", "forecast"), "estimate/forecast")
                actual = _required_value(row, ("actual",), "actual")
                previous = _required_value(row, ("previous",), "previous")
                impact = _impact_from_provider(
                    _required_text(row, ("impact", "importance"), "impact")
                )
                provider_event_id = _stable_provider_event_id(row) or _derive_provider_event_id(
                    scheduled_at=scheduled_at,
                    currency=currency,
                    country=country,
                    title=title,
                )
                event = EconomicEvent(
                    provider=PROVIDER_NAME,
                    provider_event_id=provider_event_id,
                    title=title,
                    currency=currency,
                    country=country,
                    impact=impact,
                    scheduled_at=scheduled_at,
                    actual=actual,
                    forecast=forecast,
                    previous=previous,
                    fetched_at=_parse_provider_datetime(row["fetched_at"])
                    if row.get("fetched_at")
                    else utc_now(),
                )
            except (KeyError, ValueError, ValidationError) as exc:
                raise ProviderInvalidPayloadError(
                    PROVIDER_NAME, details={"reason": "invalid_event"}
                ) from exc
            events.append(event)
        return events
