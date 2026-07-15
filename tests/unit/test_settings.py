from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_default_settings_keep_external_integrations_disabled() -> None:
    settings = Settings(_env_file=None)

    assert settings.telegram_enabled is False
    assert settings.openai_enabled is False
    assert settings.market_data_enabled is False
    assert settings.calendar_enabled is False
    assert settings.scan_enabled is False
    assert settings.scheduled_digest_enabled is False
    assert settings.scheduled_digest_interval_minutes == 60
    assert settings.paper_account_balance == Decimal("10000")


@pytest.mark.parametrize(
    ("field", "enabled_kwargs"),
    [
        ("TELEGRAM_BOT_TOKEN", {"telegram_enabled": True}),
        ("OPENAI_API_KEY", {"openai_enabled": True}),
        ("TWELVE_DATA_API_KEY", {"market_data_enabled": True}),
        ("FMP_API_KEY", {"calendar_enabled": True}),
    ],
)
def test_conditional_secret_requirements(field: str, enabled_kwargs: dict[str, bool]) -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, **enabled_kwargs)

    assert field in str(exc_info.value)


def test_telegram_enabled_requires_allowed_identity() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, telegram_enabled=True, telegram_bot_token="token")

    assert "TELEGRAM_ALLOWED_USER_ID" in str(exc_info.value)
    assert "TELEGRAM_ALLOWED_CHAT_ID" in str(exc_info.value)


def test_enabled_integrations_are_safe_booleans() -> None:
    settings = Settings(_env_file=None, telegram_enabled=False, openai_enabled=False)

    assert settings.enabled_integrations() == {
        "telegram": False,
        "openai": False,
        "market_data": False,
        "calendar": False,
    }


def test_storage_timezone_must_be_utc() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, storage_timezone="Europe/Stockholm")


def test_require_integration_tests_defaults_to_false() -> None:
    assert Settings(_env_file=None).require_integration_tests is False
