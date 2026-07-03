from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from app.core.time import normalize_to_utc, validate_timezone_aware


def test_naive_datetime_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_timezone_aware(datetime(2026, 7, 3, 12, 0, 0))


def test_utc_datetime_is_preserved() -> None:
    value = datetime(2026, 7, 3, 12, 0, 0, tzinfo=UTC)

    assert normalize_to_utc(value) == value


def test_stockholm_datetime_is_converted_to_utc() -> None:
    value = datetime(2026, 7, 3, 14, 0, 0, tzinfo=ZoneInfo("Europe/Stockholm"))

    assert normalize_to_utc(value) == datetime(2026, 7, 3, 12, 0, 0, tzinfo=UTC)
