from datetime import UTC, datetime
from zoneinfo import ZoneInfo


def utc_now() -> datetime:
    return datetime.now(UTC)


def validate_timezone_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    return value


def normalize_to_utc(value: datetime) -> datetime:
    return validate_timezone_aware(value).astimezone(UTC)


def ensure_timezone_aware(value: datetime) -> datetime:
    return validate_timezone_aware(value)


def to_timezone(value: datetime, timezone_name: str) -> datetime:
    return validate_timezone_aware(value).astimezone(ZoneInfo(timezone_name))
