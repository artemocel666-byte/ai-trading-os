from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.config import ExplanationProviderKind, Settings


def test_default_settings_keep_external_integrations_disabled() -> None:
    settings = Settings(_env_file=None)

    assert settings.telegram_enabled is False
    assert settings.explanation_provider is ExplanationProviderKind.DISABLED
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
        ("OPENAI_API_KEY", {"explanation_provider": "openai"}),
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
    settings = Settings(_env_file=None, telegram_enabled=False)

    assert settings.enabled_integrations() == {
        "telegram": False,
        "openai": False,
        "local_llm": False,
        "market_data": False,
        "calendar": False,
    }


def test_a_local_model_is_not_reported_as_an_external_integration() -> None:
    """`openai` in the status payload has always meant "something leaves this machine".

    A local model does not, so it gets its own key rather than reusing one whose meaning would
    quietly change for anybody reading `/api/v1/system/status`.
    """
    settings = Settings(_env_file=None, explanation_provider="local")

    integrations = settings.enabled_integrations()

    assert integrations["openai"] is False
    assert integrations["local_llm"] is True


def test_the_replaced_openai_flag_is_refused() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, openai_enabled=False)

    assert "EXPLANATION_PROVIDER" in str(exc_info.value)


def test_storage_timezone_must_be_utc() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, storage_timezone="Europe/Stockholm")


def test_require_integration_tests_defaults_to_false() -> None:
    assert Settings(_env_file=None).require_integration_tests is False
