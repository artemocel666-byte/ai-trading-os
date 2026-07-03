from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.value_objects import CurrencyPair

MAX_CALENDAR_RAW_LENGTH = 200
MAX_CALENDAR_ABS_VALUE = Decimal("1000000000000000")


class Timeframe(StrEnum):
    M15 = "M15"
    H1 = "H1"


class EconomicImpact(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


def _reject_float(value: object, field_name: str) -> object:
    if isinstance(value, float):
        raise ValueError(f"{field_name} must use Decimal-compatible inputs, not float")
    return value


def _normalize_decimal(value: object, field_name: str) -> tuple[Decimal | None, str | None]:
    if value is None:
        return None, None
    if isinstance(value, float):
        raise ValueError(f"{field_name} must use Decimal-compatible inputs, not float")
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must not be boolean")
    if isinstance(value, Decimal):
        decimal_value = value
    elif isinstance(value, int):
        decimal_value = Decimal(value)
    elif isinstance(value, str):
        text = value.strip()
        if len(text) > MAX_CALENDAR_RAW_LENGTH:
            raise ValueError(f"{field_name} raw value is too large")
        if not text:
            return None, None
        try:
            decimal_value = Decimal(text)
        except InvalidOperation:
            return None, text
    else:
        raise ValueError(f"{field_name} has unsupported value type")
    if not decimal_value.is_finite():
        raise ValueError(f"{field_name} must be finite")
    if abs(decimal_value) > MAX_CALENDAR_ABS_VALUE:
        raise ValueError(f"{field_name} value is unreasonably large")
    return decimal_value, None


class Candle(BaseModel):
    provider: str = Field(min_length=1)
    pair: CurrencyPair
    timeframe: Timeframe
    open_time: datetime
    close_time: datetime
    open: Decimal = Field(gt=Decimal("0"))
    high: Decimal = Field(gt=Decimal("0"))
    low: Decimal = Field(gt=Decimal("0"))
    close: Decimal = Field(gt=Decimal("0"))
    volume: Decimal | None = Field(default=None, ge=Decimal("0"))
    is_closed: bool

    model_config = ConfigDict(frozen=True)

    @field_validator("provider")
    @classmethod
    def provider_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("provider must not be empty")
        return stripped

    @field_validator("open_time", "close_time")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("open", "high", "low", "close", "volume", mode="before")
    @classmethod
    def reject_float_prices(cls, value: object) -> object:
        return _reject_float(value, "candle numeric value")

    @model_validator(mode="after")
    def validate_market_invariants(self) -> Self:
        if self.close_time <= self.open_time:
            raise ValueError("close_time must be later than open_time")
        if not self.is_closed:
            raise ValueError("only closed candles are accepted")
        if self.high < self.open:
            raise ValueError("high must be greater than or equal to open")
        if self.high < self.close:
            raise ValueError("high must be greater than or equal to close")
        if self.high < self.low:
            raise ValueError("high must be greater than or equal to low")
        if self.low > self.open:
            raise ValueError("low must be less than or equal to open")
        if self.low > self.close:
            raise ValueError("low must be less than or equal to close")
        return self


class EconomicEvent(BaseModel):
    provider: str = Field(min_length=1)
    provider_event_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    country: str | None = None
    impact: EconomicImpact
    scheduled_at: datetime
    actual: Decimal | None = None
    forecast: Decimal | None = None
    previous: Decimal | None = None
    actual_raw: str | None = Field(default=None, max_length=MAX_CALENDAR_RAW_LENGTH)
    forecast_raw: str | None = Field(default=None, max_length=MAX_CALENDAR_RAW_LENGTH)
    previous_raw: str | None = Field(default=None, max_length=MAX_CALENDAR_RAW_LENGTH)
    fetched_at: datetime

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_calendar_values(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        normalized = dict(values)
        for field_name in ("actual", "forecast", "previous"):
            decimal_value, raw_value = _normalize_decimal(normalized.get(field_name), field_name)
            normalized[field_name] = decimal_value
            raw_field_name = f"{field_name}_raw"
            if raw_value is not None and not normalized.get(raw_field_name):
                normalized[raw_field_name] = raw_value
        return normalized

    @field_validator("provider", "provider_event_id", "title")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text field must not be empty")
        return stripped

    @field_validator("country")
    @classmethod
    def country_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("currency")
    @classmethod
    def currency_must_be_uppercase(cls, value: str) -> str:
        if value.upper() != value:
            raise ValueError("currency must be uppercase")
        return value

    @field_validator("scheduled_at", "fetched_at")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)
