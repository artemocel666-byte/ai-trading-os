from decimal import Decimal
from enum import StrEnum
from functools import lru_cache
from typing import Any

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DEVELOPMENT_INTERNAL_API_KEY = "development-internal-key-change-me"


class ExplanationProviderKind(StrEnum):
    """Which explainer answers, or none.

    One setting rather than a flag per provider: an explainer is a single choice, and two booleans
    can be set to a combination that means nothing. Replaced `OPENAI_ENABLED` in Phase 8D, which is
    rejected rather than ignored — see `validate_conditional_settings`.
    """

    DISABLED = "disabled"
    OPENAI = "openai"
    LOCAL = "local"


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

    explanation_provider: ExplanationProviderKind = ExplanationProviderKind.DISABLED

    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-4.1"
    openai_base_url: str = "https://api.openai.com"
    # Caps what one explanation can cost. Three or four Russian sentences fit comfortably.
    openai_max_output_tokens: int = Field(default=400, ge=50, le=4000)

    # A model on this machine, reached over the same OpenAI-compatible chat-completions protocol.
    # The default host is `host.docker.internal` because the bot runs in a container and LM Studio
    # does not; from the host command line the same server is `http://127.0.0.1:1234`.
    local_llm_base_url: str = "http://host.docker.internal:1234"
    local_llm_model: str = "local-model"
    local_llm_max_output_tokens: int = Field(default=400, ge=50, le=4000)

    #: Read at startup only to refuse it. Phase 8D replaced this flag, and a setting that quietly
    #: stops working is worse than one that fails loudly — both `.env` and `compose.yaml` set it.
    openai_enabled: bool | None = None

    # Second gate for Phase 8C: the provider may exist and still not be allowed to answer a user.
    explanation_delivery_enabled: bool = False
    # A Telegram command must not wait on retried provider timeouts; past this the deterministic
    # report is sent on its own. A local model on CPU can need far more than the default: see
    # `docs/operations.md`, where the trade-off is spelled out rather than tuned here.
    explanation_budget_seconds: float = Field(default=20.0, gt=0, le=600)

    market_data_enabled: bool = False
    twelve_data_api_key: SecretStr | None = None
    twelve_data_base_url: str = "https://api.twelvedata.com"

    market_data_ingestion_enabled: bool = False
    market_data_ingestion_interval_minutes: int = Field(default=15, ge=1, le=1440)
    market_data_ingestion_lookback_candles: int = Field(default=48, ge=1, le=500)

    calendar_enabled: bool = False
    fmp_api_key: SecretStr | None = None
    fmp_base_url: str = "https://financialmodelingprep.com"

    calendar_ingestion_enabled: bool = False
    calendar_ingestion_interval_minutes: int = Field(default=60, ge=1, le=1440)
    calendar_ingestion_lookback_hours: int = Field(default=24, ge=1, le=168)
    calendar_ingestion_horizon_hours: int = Field(default=72, ge=1, le=336)

    # The forward outcome ledger (Phase 9C-1). Off by default like every integration before it, and
    # useless without market data: it records windows built from stored candles, so enabling it
    # without ingestion running produces nothing rather than something wrong.
    forward_outcome_recording_enabled: bool = False
    forward_outcome_record_interval_minutes: int = Field(default=15, ge=1, le=1440)
    forward_outcome_resolve_interval_minutes: int = Field(default=15, ge=1, le=1440)
    forward_outcome_window_candles: int = Field(default=12, ge=2, le=500)
    forward_outcome_horizon_candles: int = Field(default=24, ge=1, le=500)
    forward_outcome_resolve_batch_size: int = Field(default=500, ge=1, le=10_000)

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
        if self.openai_enabled is not None:
            errors.append(
                "OPENAI_ENABLED was replaced in Phase 8D; "
                "set EXPLANATION_PROVIDER=disabled|openai|local and remove it"
            )
        if self.explanation_provider is ExplanationProviderKind.OPENAI and not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required when EXPLANATION_PROVIDER=openai")
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

    def explanation_provider_configured(self) -> bool:
        """Whether an explainer exists at all. Says nothing about whether it may answer a user."""
        return self.explanation_provider is not ExplanationProviderKind.DISABLED

    def enabled_integrations(self) -> dict[str, bool]:
        """Kept keyed on `openai` so `/api/v1/system/status` stays comparable across the change.

        The key now means "a remote model is configured", which is what it always reported: a local
        model is not an integration in the sense this dictionary is asked about, because nothing
        leaves the machine.
        """
        return {
            "telegram": self.telegram_enabled,
            "openai": self.explanation_provider is ExplanationProviderKind.OPENAI,
            "local_llm": self.explanation_provider is ExplanationProviderKind.LOCAL,
            "market_data": self.market_data_enabled,
            "calendar": self.calendar_enabled,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
