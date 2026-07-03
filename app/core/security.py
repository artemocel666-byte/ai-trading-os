import re
import secrets
from collections.abc import Mapping
from typing import Any

from pydantic import SecretStr

SECRET_FIELD_MARKERS = (
    "api_key",
    "apikey",
    "token",
    "password",
    "passwd",
    "secret",
    "authorization",
    "auth",
    "database_url",
    "dsn",
)

SECRET_REPLACEMENT = "***REDACTED***"

AUTHORIZATION_RE = re.compile(r"(?i)(authorization\s*[:=]\s*)(?:bearer\s+|basic\s+)?[^\s,;]+")
QUERY_SECRET_RE = re.compile(
    r"(?i)([?&](?:api[_-]?key|apikey|token|password|passwd|secret|authorization|auth|key)=)"
    r"([^&\s]+)"
)
ASSIGNMENT_SECRET_RE = re.compile(
    r"(?i)\b((?:api[_-]?key|apikey|token|password|passwd|secret|authorization|auth|key)"
    r"\s*[:=]\s*)([^\s,;&]+)"
)
DSN_PASSWORD_RE = re.compile(r"([a-z][a-z0-9+.-]*://[^:\s/@]+:)([^@\s/]+)(@)", re.IGNORECASE)


def secret_is_set(value: SecretStr | str | None) -> bool:
    if value is None:
        return False
    raw = value.get_secret_value() if isinstance(value, SecretStr) else value
    return bool(raw.strip())


def redact_secret_value(value: str) -> str:
    if not value:
        return ""
    return SECRET_REPLACEMENT


def redact_text(value: str) -> str:
    """Redact secret-like substrings embedded in ordinary text."""

    redacted = DSN_PASSWORD_RE.sub(rf"\1{SECRET_REPLACEMENT}\3", value)
    redacted = AUTHORIZATION_RE.sub(rf"\1{SECRET_REPLACEMENT}", redacted)
    redacted = QUERY_SECRET_RE.sub(rf"\1{SECRET_REPLACEMENT}", redacted)
    return ASSIGNMENT_SECRET_RE.sub(rf"\1{SECRET_REPLACEMENT}", redacted)


def redact_secrets(payload: Any) -> Any:
    if isinstance(payload, Mapping):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in SECRET_FIELD_MARKERS):
                redacted[str(key)] = redact_secret_value(str(value))
            else:
                redacted[str(key)] = redact_secrets(value)
        return redacted
    if isinstance(payload, str):
        return redact_text(payload)
    if isinstance(payload, list):
        return [redact_secrets(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(redact_secrets(item) for item in payload)
    return payload


def constant_time_equals(left: str, right: str) -> bool:
    return secrets.compare_digest(left.encode("utf-8"), right.encode("utf-8"))
