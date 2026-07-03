# AI Trading OS - Phase 2 final defect corrections verification packet

Generated at: `2026-07-03T16:43:06.689026+00:00`

## Scope

This packet covers only the final Phase 2 defect corrections for provider JSON decoding, exact local range filtering, typed numeric failures, strict `is_closed` parsing, documentation, version-control initialization, and verification.

Phase 3 was not started. No strategies, indicators, scoring, signals, AI agents, OpenAI calls, paper trading, broker APIs, order execution, live position management, or real trading were added.

## Git Metadata

`.git` was absent at the start of this pass and was initialized with `git init`.

- Inside work tree: `true`

- Current branch after init: `main`

- HEAD before initial commit: unavailable (`fatal: ambiguous argument 'HEAD'`)

### `git status --short` after init and before initial commit

```text
?? .dockerignore
?? .env.example
?? .gitignore
?? AGENTS.md
?? Dockerfile
?? LICENSE
?? Makefile
?? PLANS.md
?? README.md
?? alembic.ini
?? app/
?? compose.yaml
?? docs/
?? migrations/
?? pyproject.toml
?? scripts/
?? tests/
?? uv.lock
```

## Summary Of Corrections

- Added standard-library JSON decoding with `Decimal` parsing for provider JSON numbers.

- Replaced `response.json()` in Twelve Data and FMP adapters.

- FMP events are locally filtered by exact UTC request bounds: `start_at <= scheduled_at < end_at`.

- Market candles are locally filtered by full containment: `start_at <= open_time` and `close_time <= end_at`.

- Twelve Data numeric parsing rejects invalid, empty, unsupported, boolean, and non-finite values as `ProviderInvalidPayloadError`.

- Economic calendar normalized numerics now reject non-finite `Decimal` values.

- `is_closed` now accepts only real JSON booleans; strings, integers, and null are invalid.

- README.md and AGENTS.md now state `Current project phase: phase_2_data_adapters`.

## Files Changed In This Defect Pass

- `AGENTS.md`

- `README.md`

- `app/adapters/json_decoding.py`

- `app/adapters/twelve_data.py`

- `app/adapters/fmp_calendar.py`

- `app/domain/entities/market_data.py`

- `tests/contract/test_provider_contracts.py`

- `tests/fixtures/economic_calendar/fmp_success.json`

- `tests/fixtures/economic_calendar/fmp_non_numeric_values.json`

- `docs/chatgpt-verification-packet.md`

## Explicit Regression Tests Added

- `test_twelve_data_json_numeric_literals_decode_to_exact_decimals`

- `test_fmp_calendar_json_numeric_literals_decode_to_exact_decimals`

- `test_fmp_calendar_filters_exact_requested_datetime_range_and_currency`

- `test_twelve_data_candles_are_restricted_to_requested_interval`

- `test_twelve_data_invalid_numeric_values_raise_typed_error`

- `test_fmp_calendar_rejects_non_finite_numeric_values`

- `test_twelve_data_is_closed_false_boolean_is_excluded`

- `test_twelve_data_is_closed_true_boolean_is_accepted`

- `test_twelve_data_is_closed_rejects_non_boolean_values`

## Verification Commands Actually Run

### `uv run ruff format --check .`

```text
85 files already formatted
```

### `uv run ruff check .`

```text
All checks passed!
```

### `uv run mypy app`

```text
Success: no issues found in 61 source files
```

### `uv run pytest`

```text
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/artem.otsel/Documents/ai-trading-os
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.1, asyncio-0.26.0
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 146 items

tests/contract/test_agent_contracts.py ......                            [  4%]
tests/contract/test_api_error_schema.py .                                [  4%]
tests/contract/test_architecture_boundaries.py ..                        [  6%]
tests/contract/test_provider_contracts.py .............................. [ 26%]
...............................                                          [ 47%]
tests/contract/test_safety_boundaries.py .........                       [ 54%]
tests/integration/test_database_and_api.py ssss                          [ 56%]
tests/unit/test_domain_market_models.py ..................               [ 69%]
tests/unit/test_errors_and_redaction.py .......                          [ 73%]
tests/unit/test_internal_api_key.py ....                                 [ 76%]
tests/unit/test_settings.py .........                                    [ 82%]
tests/unit/test_system_state_service.py .....                            [ 86%]
tests/unit/test_telegram_commands.py ..                                  [ 87%]
tests/unit/test_telegram_policy.py .....                                 [ 91%]
tests/unit/test_time.py ...                                              [ 93%]
tests/unit/test_unit_of_work_lifecycle.py ......                         [ 97%]
tests/unit/test_value_objects_and_enums.py ....                          [100%]

=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /Users/artem.otsel/Documents/ai-trading-os/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 142 passed, 4 skipped, 1 warning in 0.68s ===================
```

### `uv run python scripts/security_check.py`

```text
<no output; exit code 0>
```

## Runtime Verification Not Claimed

Docker, PostgreSQL runtime connectivity, and Alembic runtime migration checks were not run in this pass, so this packet does not claim they passed. The full `pytest` run reported four skipped integration tests.

## Changed File Contents

### `AGENTS.md`

```markdown
# AI Trading OS Agent Guide

AI Trading OS is a foundation for a future Forex analysis and paper-trading platform.

Current project phase: phase_2_data_adapters.
Phase 3 has not started. External integrations are disabled by default. The project contains no
strategy, no signals, no broker order APIs, and no real trading.

## Start and Checks

- Install: `uv sync`
- Start Docker stack: `docker compose up --build`
- Migrate: `uv run alembic upgrade head`
- Test: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type-check: `uv run mypy app`
- Full check: `make check`

## Repository Layout

- `app/api`: API adapters.
- `app/services`: application services.
- `app/domain`: domain value objects and contracts.
- `app/persistence`: database models, repositories, unit of work.
- `app/telegram`: Telegram adapter.
- `app/scheduler`: worker process.
- `docs`: detailed project documentation.

## Rules

- Dependency direction is adapters -> application services -> domain.
- Domain code must not import FastAPI, Telegram, SQLAlchemy, PostgreSQL, APScheduler, OpenAI, market-data providers, or calendar providers.
- Use async SQLAlchemy sessions only; one `AsyncSession` per unit of work or task.
- Use `Decimal` for financial values. Do not use binary floating point for money, prices, percentages, or risk.
- Store timestamps in UTC; present user-facing time in Europe/Stockholm when needed.
- Telegram user-facing text must be Russian.
- Every Telegram message must contain exactly one semantic emoji at the beginning.
- Never add real trading execution, broker order APIs, real account credentials, or live position management.
- Never fabricate market data, calendar data, agent evidence, or scan results.
- LLM output may explain deterministic results only; it must not change prices, scores, risk, or rejected decisions.
- Update documentation when architecture or safety boundaries change.

## Definition of Done

Code is complete only when tests, formatting, linting, type checking, migrations, and relevant Docker checks have been run or a truthful limitation is documented in `docs/foundation-report.md`.

```

### `README.md`

```markdown
# AI Trading OS

AI Trading OS is a safety-first foundation for a future modular Forex analysis and paper-trading platform. The current repository implements only infrastructure: API health/status endpoints, async PostgreSQL persistence, a scheduler heartbeat, Telegram command foundations, strict configuration, and safety contracts.

## Current Status

- Current project phase: phase_2_data_adapters.
- Trading strategy: not implemented.
- Real trading: disabled and unsupported.
- External integrations: disabled by default.
- Telegram: can run in disabled mode without a token.
- Phase 3: not started.

## Safety Warning

This project must not open, modify, or close real financial positions. It contains no broker order API, no real account credentials, and no automatic trading execution.

## Phase 2 Status

Phase 2 adds hardened runtime defaults, stronger secret redaction, strict UTC normalization, typed
`Candle` and `EconomicEvent` domain models, typed provider contracts, disabled-by-default provider
adapters, production Twelve Data and FMP adapters tested through `httpx.MockTransport`, and
architecture/safety verification. It still does not add strategy, indicators, analysis, signals,
OpenAI calls, or trading execution.

## Prerequisites

- Python 3.12
- uv
- Docker and Docker Compose
- PostgreSQL for local non-Docker development

## Mac and Linux Setup

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Windows Setup

Use PowerShell with Python 3.12 and uv installed:

```powershell
uv sync
Copy-Item .env.example .env
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload
```

## Docker Startup

The default configuration starts without paid API keys. Compose uses `.env` as an optional
local override file and does not use `.env.example` at runtime:

```bash
docker compose up --build
```

The Compose stack runs PostgreSQL, applies Alembic migrations, starts the API, starts the worker, and starts the Telegram process in disabled mode when `TELEGRAM_ENABLED=false`.

## Environment Configuration

Copy `.env.example` to `.env` for local overrides. The example keeps:

```text
TELEGRAM_ENABLED=false
OPENAI_ENABLED=false
MARKET_DATA_ENABLED=false
CALENDAR_ENABLED=false
SCAN_ENABLED=false
```

Secrets are required only when the matching integration is enabled.

## Migrations

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "message"
```

## Tests and Checks

```bash
make check
make test
make lint
make typecheck
```

Integration tests require a reachable `TEST_DATABASE_URL`; otherwise they skip with a clear message.

## API Endpoints

- `GET /health`
- `GET /ready`
- `GET /api/v1/system/status`
- `POST /api/v1/system/scanning/start`
- `POST /api/v1/system/scanning/stop`

State-changing endpoints require the `X-Internal-API-Key` header.
The default development key is rejected when `APP_ENV` is not `development`.

## Telegram Disabled Mode

When `TELEGRAM_ENABLED=false`, the bot process starts and remains healthy without creating a Telegram client or making network calls. When enabled, a bot token, allowed user ID, and allowed chat ID are required.

## Current Limitations

- No strategy, indicators, signals, OpenAI calls, backtesting, position sizing, broker execution, or real trading.
- `/scan_now` explicitly reports that the analytical engine is not implemented.
- Worker jobs only update heartbeat and run foundation health checks.

## Directory Overview

- `app/api`: FastAPI adapters.
- `app/core`: configuration, errors, logging, time, security, enums.
- `app/domain`: provider and repository contracts plus financial value objects.
- `app/persistence`: SQLAlchemy models, repositories, unit of work.
- `app/services`: application services.
- `app/telegram`: Telegram authorization, formatting, commands, delivery.
- `app/scheduler`: worker process and jobs.
- `docs`: product, architecture, database, operations, and implementation notes.
- `tests`: unit, integration, and contract tests.

```

### `app/adapters/json_decoding.py`

```python
import json
from decimal import Decimal
from typing import Any


def decode_json_with_decimal_numbers(content: bytes) -> Any:
    return json.loads(
        content,
        parse_float=Decimal,
        parse_int=Decimal,
        parse_constant=Decimal,
    )

```

### `app/adapters/twelve_data.py`

```python
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

```

### `app/adapters/fmp_calendar.py`

```python
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

```

### `app/domain/entities/market_data.py`

```python
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.value_objects import CurrencyPair

MAX_CALENDAR_RAW_LENGTH = 200
MAX_CALENDAR_ABS_VALUE = Decimal("1000000000000000")


class Timeframe(StrEnum):
    M15 = "M15"
    H1 = "H1"


class EconomicImpact(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


def _reject_float(value: object, field_name: str) -> object:
    if isinstance(value, float):
        raise ValueError(f"{field_name} must use Decimal-compatible inputs, not float")
    return value


def _normalize_decimal(value: object, field_name: str) -> tuple[Decimal | None, str | None]:
    if value is None:
        return None, None
    if isinstance(value, float):
        raise ValueError(f"{field_name} must use Decimal-compatible inputs, not float")
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must not be boolean")
    if isinstance(value, Decimal):
        decimal_value = value
    elif isinstance(value, int):
        decimal_value = Decimal(value)
    elif isinstance(value, str):
        text = value.strip()
        if len(text) > MAX_CALENDAR_RAW_LENGTH:
            raise ValueError(f"{field_name} raw value is too large")
        if not text:
            return None, None
        try:
            decimal_value = Decimal(text)
        except InvalidOperation:
            return None, text
    else:
        raise ValueError(f"{field_name} has unsupported value type")
    if not decimal_value.is_finite():
        raise ValueError(f"{field_name} must be finite")
    if abs(decimal_value) > MAX_CALENDAR_ABS_VALUE:
        raise ValueError(f"{field_name} value is unreasonably large")
    return decimal_value, None


class Candle(BaseModel):
    provider: str = Field(min_length=1)
    pair: CurrencyPair
    timeframe: Timeframe
    open_time: datetime
    close_time: datetime
    open: Decimal = Field(gt=Decimal("0"))
    high: Decimal = Field(gt=Decimal("0"))
    low: Decimal = Field(gt=Decimal("0"))
    close: Decimal = Field(gt=Decimal("0"))
    volume: Decimal | None = Field(default=None, ge=Decimal("0"))
    is_closed: bool

    model_config = ConfigDict(frozen=True)

    @field_validator("provider")
    @classmethod
    def provider_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("provider must not be empty")
        return stripped

    @field_validator("open_time", "close_time")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("open", "high", "low", "close", "volume", mode="before")
    @classmethod
    def reject_float_prices(cls, value: object) -> object:
        return _reject_float(value, "candle numeric value")

    @model_validator(mode="after")
    def validate_market_invariants(self) -> Self:
        if self.close_time <= self.open_time:
            raise ValueError("close_time must be later than open_time")
        if not self.is_closed:
            raise ValueError("only closed candles are accepted")
        if self.high < self.open:
            raise ValueError("high must be greater than or equal to open")
        if self.high < self.close:
            raise ValueError("high must be greater than or equal to close")
        if self.high < self.low:
            raise ValueError("high must be greater than or equal to low")
        if self.low > self.open:
            raise ValueError("low must be less than or equal to open")
        if self.low > self.close:
            raise ValueError("low must be less than or equal to close")
        return self


class EconomicEvent(BaseModel):
    provider: str = Field(min_length=1)
    provider_event_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    country: str | None = None
    impact: EconomicImpact
    scheduled_at: datetime
    actual: Decimal | None = None
    forecast: Decimal | None = None
    previous: Decimal | None = None
    actual_raw: str | None = Field(default=None, max_length=MAX_CALENDAR_RAW_LENGTH)
    forecast_raw: str | None = Field(default=None, max_length=MAX_CALENDAR_RAW_LENGTH)
    previous_raw: str | None = Field(default=None, max_length=MAX_CALENDAR_RAW_LENGTH)
    fetched_at: datetime

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_calendar_values(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        normalized = dict(values)
        for field_name in ("actual", "forecast", "previous"):
            decimal_value, raw_value = _normalize_decimal(normalized.get(field_name), field_name)
            normalized[field_name] = decimal_value
            raw_field_name = f"{field_name}_raw"
            if raw_value is not None and not normalized.get(raw_field_name):
                normalized[raw_field_name] = raw_value
        return normalized

    @field_validator("provider", "provider_event_id", "title")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text field must not be empty")
        return stripped

    @field_validator("country")
    @classmethod
    def country_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("currency")
    @classmethod
    def currency_must_be_uppercase(cls, value: str) -> str:
        if value.upper() != value:
            raise ValueError("currency must be uppercase")
        return value

    @field_validator("scheduled_at", "fetched_at")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

```

### `tests/contract/test_provider_contracts.py`

```python
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.adapters.disabled import DisabledEconomicCalendarProvider, DisabledMarketDataProvider
from app.adapters.factories import (
    create_economic_calendar_provider,
    create_market_data_provider,
    create_provider_clients,
)
from app.adapters.fmp_calendar import FMPEconomicCalendarAdapter
from app.adapters.twelve_data import TwelveDataMarketDataAdapter
from app.core.config import Settings
from app.core.exceptions import (
    ConfigurationInvalidError,
    IntegrationDisabledError,
    ProviderAuthenticationError,
    ProviderInvalidPayloadError,
    ProviderMalformedJsonError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ProviderUnsupportedRequestError,
)
from app.core.security import redact_text
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair
from app.main import create_app

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
MARKET_FIXTURES = FIXTURES_DIR / "market_data"
CALENDAR_FIXTURES = FIXTURES_DIR / "economic_calendar"


def _fixture(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _timeout() -> httpx.Timeout:
    return httpx.Timeout(connect=1, read=1, write=1, pool=1)


async def _market_adapter(
    handler: Callable[[httpx.Request], httpx.Response],
) -> tuple[TwelveDataMarketDataAdapter, httpx.AsyncClient]:
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = TwelveDataMarketDataAdapter(
        client=client,
        api_key="secret-market-key",
        base_url="https://twelve.test",
        timeout=_timeout(),
        retry_count=1,
        retry_backoff_seconds=0,
        max_request_range=timedelta(days=10),
    )
    return adapter, client


async def _calendar_adapter(
    handler: Callable[[httpx.Request], httpx.Response],
) -> tuple[FMPEconomicCalendarAdapter, httpx.AsyncClient]:
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = FMPEconomicCalendarAdapter(
        client=client,
        api_key="secret-calendar-key",
        base_url="https://fmp.test",
        timeout=_timeout(),
        retry_count=1,
        retry_backoff_seconds=0,
        max_request_range=timedelta(days=10),
    )
    return adapter, client


def _response_from_fixture(path: Path, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code=status_code, content=_fixture(path).encode("utf-8"))


def _market_response_from_values(values_json: str) -> httpx.Response:
    return httpx.Response(200, content=f'{{"values":[{values_json}]}}'.encode())


def _market_candle_json(
    *,
    open_time: str = "2026-07-02T08:00:00Z",
    close_time: str = "2026-07-02T08:15:00Z",
    open_value: str = '"1.1000"',
    is_closed: str = "true",
) -> str:
    return (
        "{"
        f'"datetime":"{open_time}",'
        f'"close_time":"{close_time}",'
        f'"open":{open_value},'
        '"high":"1.2000",'
        '"low":"1.0000",'
        '"close":"1.1500",'
        '"volume":"100",'
        f'"is_closed":{is_closed}'
        "}"
    )


def _fmp_payload_without_stable_id(
    *,
    event: str = "Consumer Price Index",
    date: str = "2026-07-02T08:30:00Z",
    country: str = "Eurozone",
    currency: str = "EUR",
) -> dict[str, str]:
    return {
        "date": date,
        "event": event,
        "currency": currency,
        "country": country,
        "impact": "High",
        "actual": "2.2",
        "estimate": "2.1",
        "previous": "2.0",
        "fetched_at": "2026-07-02T08:00:00Z",
    }


def _assert_fmp_apikey_query_param(request: httpx.Request) -> None:
    api_key = request.url.params.get("apikey")
    if api_key != "secret-calendar-key":
        pytest.fail("FMP apikey query parameter was missing or incorrect.")


@pytest.mark.asyncio
async def test_twelve_data_m15_parsing_uses_decimal_and_utc() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return _response_from_fixture(MARKET_FIXTURES / "twelve_data_m15_success.json")

    adapter, client = await _market_adapter(handler)
    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )

    assert len(candles) == 1
    assert isinstance(candles[0], Candle)
    assert candles[0].open == Decimal("1.1000")
    assert candles[0].open_time == datetime(2026, 7, 2, 8, 0, tzinfo=UTC)
    assert captured_request is not None
    assert captured_request.url.path == "/time_series"
    assert captured_request.url.params["timezone"] == "UTC"
    assert captured_request.headers["Authorization"] == "apikey secret-market-key"
    assert "secret-market-key" not in str(captured_request.url)


@pytest.mark.asyncio
async def test_twelve_data_json_numeric_literals_decode_to_exact_decimals() -> None:
    payload = b"""
    {
      "values": [
        {
          "datetime": "2026-07-02T08:00:00Z",
          "close_time": "2026-07-02T08:15:00Z",
          "open": 1.1,
          "high": 1.2,
          "low": 1.0,
          "close": 1.15,
          "volume": 100,
          "is_closed": true
        }
      ]
    }
    """
    adapter, client = await _market_adapter(lambda request: httpx.Response(200, content=payload))

    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 8, 15, tzinfo=UTC),
        )

    assert len(candles) == 1
    assert type(candles[0].open) is Decimal
    assert type(candles[0].high) is Decimal
    assert type(candles[0].low) is Decimal
    assert type(candles[0].close) is Decimal
    assert type(candles[0].volume) is Decimal
    assert candles[0].open == Decimal("1.1")
    assert candles[0].high == Decimal("1.2")
    assert candles[0].low == Decimal("1.0")
    assert candles[0].close == Decimal("1.15")
    assert candles[0].volume == Decimal("100")


@pytest.mark.asyncio
async def test_twelve_data_h1_parsing() -> None:
    adapter, client = await _market_adapter(
        lambda request: _response_from_fixture(MARKET_FIXTURES / "twelve_data_h1_success.json")
    )
    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.H1,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 12, 0, tzinfo=UTC),
        )

    assert len(candles) == 1
    assert candles[0].close_time == datetime(2026, 7, 2, 9, 0, tzinfo=UTC)


@pytest.mark.asyncio
async def test_twelve_data_empty_valid_response() -> None:
    adapter, client = await _market_adapter(
        lambda request: _response_from_fixture(MARKET_FIXTURES / "twelve_data_empty.json")
    )
    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )

    assert candles == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("fixture", "expected_error"),
    [
        ("twelve_data_malformed.json", ProviderMalformedJsonError),
        ("twelve_data_invalid_payload.json", ProviderInvalidPayloadError),
        ("twelve_data_invalid_ohlc.json", ProviderInvalidPayloadError),
        ("twelve_data_auth_error.json", ProviderAuthenticationError),
        ("twelve_data_rate_limit.json", ProviderRateLimitError),
    ],
)
async def test_twelve_data_provider_errors(
    fixture: str,
    expected_error: type[Exception],
) -> None:
    adapter, client = await _market_adapter(
        lambda request: _response_from_fixture(MARKET_FIXTURES / fixture)
    )
    async with client:
        with pytest.raises(expected_error):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )


@pytest.mark.asyncio
async def test_twelve_data_open_candle_is_excluded() -> None:
    adapter, client = await _market_adapter(
        lambda request: _response_from_fixture(MARKET_FIXTURES / "twelve_data_open_candle.json")
    )
    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )

    assert candles == []


@pytest.mark.asyncio
async def test_twelve_data_candles_are_restricted_to_requested_interval() -> None:
    values_json = ",".join(
        [
            _market_candle_json(
                open_time="2026-07-02T07:45:00Z",
                close_time="2026-07-02T08:00:00Z",
            ),
            _market_candle_json(
                open_time="2026-07-02T08:00:00Z",
                close_time="2026-07-02T08:15:00Z",
            ),
            _market_candle_json(
                open_time="2026-07-02T08:45:00Z",
                close_time="2026-07-02T09:00:00Z",
            ),
            _market_candle_json(
                open_time="2026-07-02T08:50:00Z",
                close_time="2026-07-02T09:05:00Z",
            ),
            _market_candle_json(
                open_time="2026-07-02T09:00:00Z",
                close_time="2026-07-02T09:15:00Z",
            ),
        ]
    )
    adapter, client = await _market_adapter(
        lambda request: _market_response_from_values(values_json)
    )

    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )

    assert [(candle.open_time, candle.close_time) for candle in candles] == [
        (
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 8, 15, tzinfo=UTC),
        ),
        (
            datetime(2026, 7, 2, 8, 45, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        ),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bad_open",
    ['"abc"', '""', "null", '"NaN"', '"Infinity"', "NaN", "Infinity", "true", "{}"],
)
async def test_twelve_data_invalid_numeric_values_raise_typed_error(bad_open: str) -> None:
    adapter, client = await _market_adapter(
        lambda request: _market_response_from_values(_market_candle_json(open_value=bad_open))
    )

    async with client:
        with pytest.raises(ProviderInvalidPayloadError):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )


@pytest.mark.asyncio
async def test_twelve_data_is_closed_false_boolean_is_excluded() -> None:
    adapter, client = await _market_adapter(
        lambda request: _market_response_from_values(_market_candle_json(is_closed="false"))
    )

    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )

    assert candles == []


@pytest.mark.asyncio
async def test_twelve_data_is_closed_true_boolean_is_accepted() -> None:
    adapter, client = await _market_adapter(
        lambda request: _market_response_from_values(_market_candle_json(is_closed="true"))
    )

    async with client:
        candles = await adapter.get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )

    assert len(candles) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_is_closed", ['"false"', "1"])
async def test_twelve_data_is_closed_rejects_non_boolean_values(bad_is_closed: str) -> None:
    adapter, client = await _market_adapter(
        lambda request: _market_response_from_values(_market_candle_json(is_closed=bad_is_closed))
    )

    async with client:
        with pytest.raises(ProviderInvalidPayloadError):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )


@pytest.mark.asyncio
async def test_twelve_data_timeout_and_retry_limit() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("timeout", request=request)

    adapter, client = await _market_adapter(handler)
    async with client:
        with pytest.raises(ProviderTimeoutError):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )

    assert attempts == 2


@pytest.mark.asyncio
async def test_twelve_data_5xx_is_retried_then_unavailable() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return _response_from_fixture(MARKET_FIXTURES / "twelve_data_server_error.json", 500)

    adapter, client = await _market_adapter(handler)
    async with client:
        with pytest.raises(ProviderUnavailableError):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )

    assert attempts == 2


@pytest.mark.asyncio
async def test_twelve_data_request_validation() -> None:
    adapter, client = await _market_adapter(
        lambda request: _response_from_fixture(MARKET_FIXTURES / "twelve_data_empty.json")
    )
    async with client:
        with pytest.raises(ProviderUnsupportedRequestError):
            await adapter.get_closed_candles(  # type: ignore[arg-type]
                "EUR/USD",
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )
        with pytest.raises(ProviderUnsupportedRequestError):
            await adapter.get_closed_candles(  # type: ignore[arg-type]
                CurrencyPair(value="EURUSD"),
                "M5",
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )
        with pytest.raises(ValueError, match="timezone-aware"):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )
        with pytest.raises(ProviderUnsupportedRequestError):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            )
        with pytest.raises(ProviderUnsupportedRequestError):
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 1, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 20, 8, 0, tzinfo=UTC),
            )


@pytest.mark.asyncio
async def test_fmp_calendar_success_and_non_numeric_values() -> None:
    adapter, client = await _calendar_adapter(
        lambda request: _response_from_fixture(CALENDAR_FIXTURES / "fmp_non_numeric_values.json")
    )
    async with client:
        events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert len(events) == 1
    assert isinstance(events[0], EconomicEvent)
    assert events[0].actual is None
    assert events[0].actual_raw == "N/A"
    assert events[0].forecast is None
    assert events[0].forecast_raw == "-"
    assert events[0].previous == Decimal("2.0")


@pytest.mark.asyncio
async def test_fmp_calendar_success_decimal_and_utc() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return _response_from_fixture(CALENDAR_FIXTURES / "fmp_success.json")

    adapter, client = await _calendar_adapter(handler)
    async with client:
        events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert len(events) == 1
    assert events[0].provider_event_id == "eur-cpi-1"
    assert events[0].title == "Consumer Price Index"
    assert events[0].country == "Eurozone"
    assert events[0].currency == "EUR"
    assert events[0].impact is EconomicImpact.HIGH
    assert events[0].actual == Decimal("2.2")
    assert events[0].forecast == Decimal("2.1")
    assert events[0].previous == Decimal("2.0")
    assert events[0].scheduled_at == datetime(2026, 7, 2, 8, 30, tzinfo=UTC)
    assert captured_request is not None
    assert captured_request.url.path == "/stable/economic-calendar"
    assert captured_request.url.params["from"] == "2026-07-02"
    assert captured_request.url.params["to"] == "2026-07-02"
    assert captured_request.url.params["currencies"] == "EUR"
    _assert_fmp_apikey_query_param(captured_request)
    assert "authorization" not in captured_request.headers
    redacted_url = redact_text(str(captured_request.url))
    assert "secret-calendar-key" not in redacted_url
    assert "apikey=***REDACTED***" in redacted_url


@pytest.mark.asyncio
async def test_fmp_calendar_json_numeric_literals_decode_to_exact_decimals() -> None:
    payload = b"""
    [
      {
        "id": "eur-cpi-numeric",
        "date": "2026-07-02T08:30:00Z",
        "event": "Consumer Price Index",
        "currency": "EUR",
        "country": "Eurozone",
        "impact": "High",
        "actual": 2.2,
        "estimate": 2.1,
        "previous": 2.0,
        "fetched_at": "2026-07-02T08:00:00Z"
      }
    ]
    """
    adapter, client = await _calendar_adapter(lambda request: httpx.Response(200, content=payload))

    async with client:
        events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert len(events) == 1
    assert type(events[0].actual) is Decimal
    assert type(events[0].forecast) is Decimal
    assert type(events[0].previous) is Decimal
    assert events[0].actual == Decimal("2.2")
    assert events[0].forecast == Decimal("2.1")
    assert events[0].previous == Decimal("2.0")


@pytest.mark.asyncio
async def test_fmp_calendar_filters_exact_requested_datetime_range_and_currency() -> None:
    payload = [
        {
            **_fmp_payload_without_stable_id(event="before-start", date="2026-07-02T07:59:00Z"),
            "id": "before-start",
        },
        {
            **_fmp_payload_without_stable_id(event="at-start", date="2026-07-02T08:00:00Z"),
            "id": "at-start",
        },
        {
            **_fmp_payload_without_stable_id(event="wrong-currency", currency="USD"),
            "id": "wrong-currency",
        },
        {
            **_fmp_payload_without_stable_id(event="before-end", date="2026-07-02T08:59:00Z"),
            "id": "before-end",
        },
        {
            **_fmp_payload_without_stable_id(event="at-end", date="2026-07-02T09:00:00Z"),
            "id": "at-end",
        },
        {
            **_fmp_payload_without_stable_id(event="later-same-date", date="2026-07-02T14:00:00Z"),
            "id": "later-same-date",
        },
    ]
    adapter, client = await _calendar_adapter(lambda request: httpx.Response(200, json=payload))

    async with client:
        events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert [event.title for event in events] == ["at-start", "before-end"]


@pytest.mark.asyncio
async def test_fmp_calendar_accepts_forecast_when_estimate_is_absent() -> None:
    payload = [_fmp_payload_without_stable_id()]
    payload[0].pop("estimate")
    payload[0]["forecast"] = "2.1"
    adapter, client = await _calendar_adapter(lambda request: httpx.Response(200, json=payload))

    async with client:
        events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert len(events) == 1
    assert events[0].forecast == Decimal("2.1")


@pytest.mark.asyncio
async def test_fmp_calendar_accepts_title_when_event_is_absent() -> None:
    payload = [_fmp_payload_without_stable_id()]
    payload[0].pop("event")
    payload[0]["title"] = "Consumer Price Index"
    adapter, client = await _calendar_adapter(lambda request: httpx.Response(200, json=payload))

    async with client:
        events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert len(events) == 1
    assert events[0].title == "Consumer Price Index"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "missing_field",
    ["date", "event", "country", "currency", "actual", "estimate", "previous", "impact"],
)
async def test_fmp_calendar_rejects_missing_required_provider_fields(missing_field: str) -> None:
    payload = [_fmp_payload_without_stable_id()]
    payload[0].pop(missing_field)
    adapter, client = await _calendar_adapter(lambda request: httpx.Response(200, json=payload))

    async with client:
        with pytest.raises(ProviderInvalidPayloadError):
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
                currencies=["EUR"],
            )


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_actual", ['"NaN"', '"Infinity"', "NaN", "Infinity"])
async def test_fmp_calendar_rejects_non_finite_numeric_values(bad_actual: str) -> None:
    payload = (
        "["
        "{"
        '"id":"bad-calendar-numeric",'
        '"date":"2026-07-02T08:30:00Z",'
        '"event":"Consumer Price Index",'
        '"currency":"EUR",'
        '"country":"Eurozone",'
        '"impact":"High",'
        f'"actual":{bad_actual},'
        '"estimate":2.1,'
        '"previous":2.0,'
        '"fetched_at":"2026-07-02T08:00:00Z"'
        "}"
        "]"
    ).encode()
    adapter, client = await _calendar_adapter(lambda request: httpx.Response(200, content=payload))

    async with client:
        with pytest.raises(ProviderInvalidPayloadError):
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
                currencies=["EUR"],
            )


@pytest.mark.asyncio
async def test_fmp_calendar_derived_event_id_is_deterministic() -> None:
    adapter, client = await _calendar_adapter(
        lambda request: httpx.Response(200, json=[_fmp_payload_without_stable_id()])
    )

    async with client:
        first_events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )
        second_events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    first_id = first_events[0].provider_event_id
    assert first_id == second_events[0].provider_event_id
    assert len(first_id) == 64


@pytest.mark.asyncio
async def test_fmp_calendar_derived_event_id_changes_when_identity_changes() -> None:
    responses = [
        [_fmp_payload_without_stable_id()],
        [_fmp_payload_without_stable_id(event="Core Consumer Price Index")],
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=responses.pop(0))

    adapter, client = await _calendar_adapter(handler)
    async with client:
        first_events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )
        second_events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert first_events[0].provider_event_id != second_events[0].provider_event_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("fixture", "expected_error"),
    [
        ("fmp_malformed.json", ProviderMalformedJsonError),
        ("fmp_invalid_payload.json", ProviderInvalidPayloadError),
        ("fmp_auth_error.json", ProviderAuthenticationError),
        ("fmp_rate_limit.json", ProviderRateLimitError),
    ],
)
async def test_fmp_calendar_provider_errors(
    fixture: str,
    expected_error: type[Exception],
) -> None:
    adapter, client = await _calendar_adapter(
        lambda request: _response_from_fixture(CALENDAR_FIXTURES / fixture)
    )
    async with client:
        with pytest.raises(expected_error):
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
                currencies=["EUR"],
            )


@pytest.mark.asyncio
async def test_fmp_calendar_empty_valid_response() -> None:
    adapter, client = await _calendar_adapter(
        lambda request: _response_from_fixture(CALENDAR_FIXTURES / "fmp_empty.json")
    )
    async with client:
        events = await adapter.get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            currencies=["EUR"],
        )

    assert events == []


@pytest.mark.asyncio
async def test_fmp_calendar_5xx_is_retried_then_unavailable() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return _response_from_fixture(CALENDAR_FIXTURES / "fmp_server_error.json", 500)

    adapter, client = await _calendar_adapter(handler)
    async with client:
        with pytest.raises(ProviderUnavailableError):
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            )

    assert attempts == 2


@pytest.mark.asyncio
async def test_fmp_calendar_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timeout", request=request)

    adapter, client = await _calendar_adapter(handler)
    async with client:
        with pytest.raises(ProviderTimeoutError):
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
            )


@pytest.mark.asyncio
async def test_fmp_calendar_request_validation() -> None:
    adapter, client = await _calendar_adapter(
        lambda request: _response_from_fixture(CALENDAR_FIXTURES / "fmp_empty.json")
    )
    async with client:
        with pytest.raises(ProviderUnsupportedRequestError):
            await adapter.get_events(
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            )
        with pytest.raises(ProviderUnsupportedRequestError):
            await adapter.get_events(
                datetime(2026, 7, 1, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 20, 8, 0, tzinfo=UTC),
            )
        with pytest.raises(ProviderUnsupportedRequestError):
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
                currencies=["eur"],
            )
        with pytest.raises(ValueError, match="timezone-aware"):
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )


@pytest.mark.asyncio
async def test_provider_exceptions_and_urls_do_not_expose_api_key() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return _response_from_fixture(MARKET_FIXTURES / "twelve_data_auth_error.json")

    adapter, client = await _market_adapter(handler)
    async with client:
        with pytest.raises(ProviderAuthenticationError) as exc_info:
            await adapter.get_closed_candles(
                CurrencyPair(value="EURUSD"),
                Timeframe.M15,
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
            )

    assert captured_request is not None
    assert "secret-market-key" not in str(captured_request.url)
    assert "secret-market-key" not in str(exc_info.value)
    assert "secret-market-key" not in str(exc_info.value.details)


@pytest.mark.asyncio
async def test_fmp_query_api_key_is_redacted_from_diagnostics() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return _response_from_fixture(CALENDAR_FIXTURES / "fmp_auth_error.json")

    adapter, client = await _calendar_adapter(handler)
    async with client:
        with pytest.raises(ProviderAuthenticationError) as exc_info:
            await adapter.get_events(
                datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
                datetime(2026, 7, 2, 10, 0, tzinfo=UTC),
                currencies=["EUR"],
            )

    assert captured_request is not None
    assert captured_request.url.path == "/stable/economic-calendar"
    _assert_fmp_apikey_query_param(captured_request)
    redacted_request_diagnostic = redact_text(f"{captured_request.method} {captured_request.url}")
    assert "secret-calendar-key" not in redacted_request_diagnostic
    assert "secret-calendar-key" not in str(exc_info.value)
    assert "secret-calendar-key" not in str(exc_info.value.details)


@pytest.mark.asyncio
async def test_disabled_adapters_fail_without_network() -> None:
    with pytest.raises(IntegrationDisabledError):
        await DisabledMarketDataProvider().get_closed_candles(
            CurrencyPair(value="EURUSD"),
            Timeframe.M15,
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )
    with pytest.raises(IntegrationDisabledError):
        await DisabledEconomicCalendarProvider().get_events(
            datetime(2026, 7, 2, 8, 0, tzinfo=UTC),
            datetime(2026, 7, 2, 9, 0, tzinfo=UTC),
        )


@pytest.mark.asyncio
async def test_provider_factory_behavior() -> None:
    disabled_settings = Settings(_env_file=None)
    assert isinstance(create_market_data_provider(disabled_settings), DisabledMarketDataProvider)
    assert isinstance(
        create_economic_calendar_provider(disabled_settings), DisabledEconomicCalendarProvider
    )
    disabled_clients = create_provider_clients(disabled_settings)
    assert disabled_clients.market_data is None
    assert disabled_clients.economic_calendar is None

    enabled_market = Settings(
        _env_file=None,
        market_data_enabled=True,
        twelve_data_api_key="market-key",
    )
    enabled_calendar = Settings(
        _env_file=None,
        calendar_enabled=True,
        fmp_api_key="calendar-key",
    )
    with pytest.raises(ConfigurationInvalidError):
        create_market_data_provider(enabled_market)
    with pytest.raises(ConfigurationInvalidError):
        create_economic_calendar_provider(enabled_calendar)

    client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    )
    try:
        assert isinstance(
            create_market_data_provider(enabled_market, client=client),
            TwelveDataMarketDataAdapter,
        )
        assert isinstance(
            create_economic_calendar_provider(enabled_calendar, client=client),
            FMPEconomicCalendarAdapter,
        )
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_provider_client_lifecycle_closes_owned_clients() -> None:
    settings = Settings(
        _env_file=None,
        market_data_enabled=True,
        twelve_data_api_key="market-key",
        calendar_enabled=True,
        fmp_api_key="calendar-key",
    )
    clients = create_provider_clients(settings)

    assert clients.market_data is not None
    assert clients.economic_calendar is not None
    assert not clients.market_data.is_closed
    assert not clients.economic_calendar.is_closed

    await clients.aclose()

    assert clients.market_data.is_closed
    assert clients.economic_calendar.is_closed


def test_application_lifespan_closes_owned_provider_clients() -> None:
    settings = Settings(
        _env_file=None,
        market_data_enabled=True,
        twelve_data_api_key="market-key",
        calendar_enabled=True,
        fmp_api_key="calendar-key",
    )
    app = create_app(settings)

    with TestClient(app):
        clients = app.state.provider_clients
        market_data_client = clients.market_data
        economic_calendar_client = clients.economic_calendar
        assert market_data_client is not None
        assert economic_calendar_client is not None
        assert not market_data_client.is_closed
        assert not economic_calendar_client.is_closed

    assert market_data_client.is_closed
    assert economic_calendar_client.is_closed

```

### `tests/fixtures/economic_calendar/fmp_success.json`

```json
[
  {
    "id": "eur-cpi-1",
    "date": "2026-07-02T08:30:00Z",
    "event": "Consumer Price Index",
    "currency": "EUR",
    "country": "Eurozone",
    "impact": "High",
    "actual": "2.2",
    "estimate": "2.1",
    "previous": "2.0",
    "fetched_at": "2026-07-02T08:00:00Z"
  }
]

```

### `tests/fixtures/economic_calendar/fmp_non_numeric_values.json`

```json
[
  {
    "id": "eur-cpi-2",
    "date": "2026-07-02T09:30:00Z",
    "event": "Consumer Price Index",
    "currency": "EUR",
    "country": "Eurozone",
    "impact": "Medium",
    "actual": "N/A",
    "estimate": "-",
    "previous": "2.0",
    "fetched_at": "2026-07-02T09:00:00Z"
  }
]

```
