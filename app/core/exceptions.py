from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from app.core.security import redact_secrets, redact_text


class ErrorCode(StrEnum):
    CONFIGURATION_INVALID = "CONFIGURATION_INVALID"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"
    INTEGRATION_DISABLED = "INTEGRATION_DISABLED"
    UNAUTHORIZED = "UNAUTHORIZED"
    MESSAGE_FORMAT_INVALID = "MESSAGE_FORMAT_INVALID"
    RUSSIAN_TEXT_INVALID = "RUSSIAN_TEXT_INVALID"
    AI_OUTPUT_INVALID = "AI_OUTPUT_INVALID"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    PROVIDER_AUTHENTICATION_FAILED = "PROVIDER_AUTHENTICATION_FAILED"
    PROVIDER_RATE_LIMITED = "PROVIDER_RATE_LIMITED"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_MALFORMED_JSON = "PROVIDER_MALFORMED_JSON"
    PROVIDER_INVALID_PAYLOAD = "PROVIDER_INVALID_PAYLOAD"
    PROVIDER_UNSUPPORTED_REQUEST = "PROVIDER_UNSUPPORTED_REQUEST"


class ApplicationError(Exception):
    """Base class for fail-closed application errors."""

    def __init__(
        self,
        code: ErrorCode,
        message_ru: str,
        *,
        status_code: int = 500,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(redact_text(message_ru))
        self.code = code
        self.message_ru = redact_text(message_ru)
        self.status_code = status_code
        self.details = redact_secrets(dict(details or {}))


class ConfigurationInvalidError(ApplicationError):
    def __init__(self, message_ru: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.CONFIGURATION_INVALID,
            message_ru,
            status_code=500,
            details=details,
        )


class DatabaseUnavailableError(ApplicationError):
    def __init__(self, message_ru: str = "База данных недоступна.") -> None:
        super().__init__(ErrorCode.DATABASE_UNAVAILABLE, message_ru, status_code=503)


class IntegrationDisabledError(ApplicationError):
    def __init__(self, integration: str) -> None:
        super().__init__(
            ErrorCode.INTEGRATION_DISABLED,
            "Интеграция отключена настройками.",
            status_code=503,
            details={"integration": integration},
        )


class UnauthorizedError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.UNAUTHORIZED,
            "Доступ запрещён.",
            status_code=401,
        )


class MessageFormatInvalidError(ApplicationError):
    def __init__(self, message_ru: str = "Формат сообщения недействителен.") -> None:
        super().__init__(ErrorCode.MESSAGE_FORMAT_INVALID, message_ru, status_code=500)


class RussianTextInvalidError(ApplicationError):
    def __init__(self, message_ru: str = "Текст сообщения должен быть на русском языке.") -> None:
        super().__init__(ErrorCode.RUSSIAN_TEXT_INVALID, message_ru, status_code=500)


class NotImplementedFeatureError(ApplicationError):
    def __init__(self, feature: str) -> None:
        super().__init__(
            ErrorCode.NOT_IMPLEMENTED,
            "Функция ещё не реализована в foundation-фазе.",
            status_code=501,
            details={"feature": feature},
        )


class ProviderError(ApplicationError):
    def __init__(
        self,
        code: ErrorCode,
        message_ru: str,
        *,
        status_code: int = 502,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(code, message_ru, status_code=status_code, details=details)


class ProviderAuthenticationError(ProviderError):
    def __init__(self, provider: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.PROVIDER_AUTHENTICATION_FAILED,
            "Провайдер отклонил авторизацию.",
            status_code=502,
            details={"provider": provider, **dict(details or {})},
        )


class ProviderRateLimitError(ProviderError):
    def __init__(self, provider: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.PROVIDER_RATE_LIMITED,
            "Провайдер временно ограничил частоту запросов.",
            status_code=503,
            details={"provider": provider, **dict(details or {})},
        )


class ProviderTimeoutError(ProviderError):
    def __init__(self, provider: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.PROVIDER_TIMEOUT,
            "Провайдер не ответил вовремя.",
            status_code=504,
            details={"provider": provider, **dict(details or {})},
        )


class ProviderUnavailableError(ProviderError):
    def __init__(self, provider: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.PROVIDER_UNAVAILABLE,
            "Провайдер временно недоступен.",
            status_code=503,
            details={"provider": provider, **dict(details or {})},
        )


class ProviderMalformedJsonError(ProviderError):
    def __init__(self, provider: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.PROVIDER_MALFORMED_JSON,
            "Провайдер вернул некорректный JSON.",
            status_code=502,
            details={"provider": provider, **dict(details or {})},
        )


class ProviderInvalidPayloadError(ProviderError):
    def __init__(self, provider: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.PROVIDER_INVALID_PAYLOAD,
            "Провайдер вернул структурно некорректные данные.",
            status_code=502,
            details={"provider": provider, **dict(details or {})},
        )


class ProviderUnsupportedRequestError(ProviderError):
    def __init__(self, provider: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(
            ErrorCode.PROVIDER_UNSUPPORTED_REQUEST,
            "Запрос к провайдеру не поддерживается.",
            status_code=400,
            details={"provider": provider, **dict(details or {})},
        )
