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
