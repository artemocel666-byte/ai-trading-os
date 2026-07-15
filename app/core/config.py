from decimal import Decimal
from functools import lru_cache
from typing import Any

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DEVELOPMENT_INTERNAL_API_KEY = "development-internal-key-change-me"


class Settings(BaseSettings):
    app_name: str = "AI Trading OS"
    app_env: str = "development"
    app_timezone: str = "Europe/Stockholm"
    storage_timezone: str = "UTC"
    log_level: str = "INFO"

    database_url: SecretStr = SecretStr(
        "postgresql+asyncpg://ai_trading_os:ai_trading_os@postgres:5432/ai_trading_os"
    )
    test_database_url: SecretStr | None = SecretStr(
        "postgresql+asyncpg://ai_trading_os:ai_trading_os@localhost:5432/ai_trading_os_test"
    )
    internal_api_key: SecretStr = SecretStr(DEFAULT_DEVELOPMENT_INTERNAL_API_KEY)

    telegram_enabled: bool = False
    telegram_bot_token: SecretStr | None = None
    telegram_allowed_user_id: int | None = None
    telegram_allowed_chat_id: int | None = None

    openai_enabled: bool = False
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1"

    market_data_enabled: bool = False
    twelve_data_api_key: SecretStr | None = None
    twelve_data_base_url: str = "https://api.twelvedata.com"

    calendar_enabled: bool = False
    fmp_api_key: SecretStr | None = None
    fmp_base_url: str = "https://financialmodelingprep.com"

    provider_connect_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    provider_read_timeout_seconds: float = Field(default=10.0, gt=0, le=60)
    provider_write_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    provider_pool_timeout_seconds: float = Field(default=5.0, gt=0, le=30)
    provider_retry_count: int = Field(default=2, ge=0, le=5)
    provider_retry_backoff_seconds: float = Field(default=0.1, ge=0, le=5)
    provider_max_request_range_days: int = Field(default=31, ge=1, le=370)
    require_integration_tests: bool = False

    scan_enabled: bool = False
    scheduled_digest_enabled: bool = False
    scheduled_digest_interval_minutes: int = Field(default=60, ge=1, le=1440)
    setup_score_threshold: int = Field(default=85, ge=0, le=100)

    paper_account_currency: str = "EUR"
    paper_account_balance: Decimal = Field(default=Decimal("10000"), gt=Decimal("0"))
    paper_risk_percent: Decimal = Field(default=Decimal("0.5"), ge=Decimal("0"))
    max_open_risk_percent: Decimal = Field(default=Decimal("1.0"), ge=Decimal("0"))
    max_daily_loss_percent: Decimal = Field(default=Decimal("1.5"), ge=Decimal("0"))
    max_weekly_loss_percent: Decimal = Field(default=Decimal("4.0"), ge=Decimal("0"))
    max_consecutive_losses: int = Field(default=3, ge=0)

    signal_valid_minutes: int = Field(default=30, ge=1)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator(
        "telegram_bot_token",
        "telegram_allowed_user_id",
        "telegram_allowed_chat_id",
        "openai_api_key",
        "twelve_data_api_key",
        "fmp_api_key",
        "test_database_url",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        if value == "":
            return None
        return value

    @field_validator("paper_account_currency")
    @classmethod
    def currency_code_must_be_uppercase(cls, value: str) -> str:
        if len(value) != 3 or not value.isalpha() or value.upper() != value:
            raise ValueError("paper account currency must be a three-letter uppercase code")
        return value

    @model_validator(mode="after")
    def validate_conditional_settings(self) -> "Settings":
        errors: list[str] = []
        if not self.internal_api_key.get_secret_value().strip():
            errors.append("INTERNAL_API_KEY is required")
        if self.storage_timezone != "UTC":
            errors.append("STORAGE_TIMEZONE must be UTC")
        if (
            self.app_env != "development"
            and self.internal_api_key.get_secret_value() == DEFAULT_DEVELOPMENT_INTERNAL_API_KEY
        ):
            errors.append("Default development INTERNAL_API_KEY is rejected outside development")
        if self.telegram_enabled:
            if not self.telegram_bot_token:
                errors.append("TELEGRAM_BOT_TOKEN is required when TELEGRAM_ENABLED=true")
            if self.telegram_allowed_user_id is None:
                errors.append("TELEGRAM_ALLOWED_USER_ID is required when TELEGRAM_ENABLED=true")
            if self.telegram_allowed_chat_id is None:
                errors.append("TELEGRAM_ALLOWED_CHAT_ID is required when TELEGRAM_ENABLED=true")
        if self.openai_enabled and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required when OPENAI_ENABLED=true")
        if self.market_data_enabled and not self.twelve_data_api_key:
            errors.append("TWELVE_DATA_API_KEY is required when MARKET_DATA_ENABLED=true")
        if self.calendar_enabled and not self.fmp_api_key:
            errors.append("FMP_API_KEY is required when CALENDAR_ENABLED=true")
        if errors:
            raise ValueError("; ".join(errors))
        return self

    def database_dsn(self) -> str:
        return self.database_url.get_secret_value()

    def test_database_dsn(self) -> str | None:
        return self.test_database_url.get_secret_value() if self.test_database_url else None

    def enabled_integrations(self) -> dict[str, bool]:
        return {
            "telegram": self.telegram_enabled,
            "openai": self.openai_enabled,
            "market_data": self.market_data_enabled,
            "calendar": self.calendar_enabled,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
