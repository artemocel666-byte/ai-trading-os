import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.error_handlers import register_error_handlers
from app.core.exceptions import IntegrationDisabledError
from app.core.security import redact_secrets, redact_text


@pytest.mark.asyncio
async def test_application_exception_maps_to_consistent_error_schema() -> None:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/raise")
    async def raise_error() -> None:
        raise IntegrationDisabledError("openai")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/raise", headers={"X-Request-ID": "req-1"})

    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "INTEGRATION_DISABLED"
    assert body["error"]["message_ru"] == "Интеграция отключена настройками."
    assert "details" in body["error"]


def test_secret_redaction_masks_sensitive_keys() -> None:
    payload = {
        "database_url": "postgresql+asyncpg://user:password@host/db",
        "nested": {"telegram_bot_token": "123:secret"},
        "normal": "visible",
    }

    assert redact_secrets(payload) == {
        "database_url": "***REDACTED***",
        "nested": {"telegram_bot_token": "***REDACTED***"},
        "normal": "visible",
    }


def test_redaction_masks_api_keys_inside_strings() -> None:
    text = "provider failed for url=https://example.test/data?api_key=secret-value&pair=EURUSD"

    assert "secret-value" not in redact_text(text)


def test_redaction_masks_passwords_inside_dsns() -> None:
    text = "db=postgresql+asyncpg://user:secret-password@localhost:5432/app"

    redacted = redact_text(text)

    assert "secret-password" not in redacted
    assert "***REDACTED***" in redacted


def test_redaction_masks_authorization_headers() -> None:
    text = "Authorization: Bearer very-secret-token"

    assert redact_text(text) == "Authorization: ***REDACTED***"


def test_redaction_masks_provider_urls_containing_query_parameters() -> None:
    payload = {
        "message": "GET https://calendar.test/events?token=abc123&currency=EUR",
        "url": "https://market.test/candles?apikey=abc123",
    }

    redacted = redact_secrets(payload)

    assert "abc123" not in str(redacted)
    assert "***REDACTED***" in str(redacted)


def test_database_skip_messages_do_not_expose_full_dsn() -> None:
    message = redact_text(
        "PostgreSQL test database is unavailable: "
        "postgresql+asyncpg://user:secret@localhost:5432/test"
    )

    assert "secret" not in message
