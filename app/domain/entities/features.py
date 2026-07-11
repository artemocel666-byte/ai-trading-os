from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.data_quality import DataQualityIssue
from app.domain.entities.market_data import EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair


class FeatureIssueCode(StrEnum):
    NO_CANDLES = "NO_CANDLES"
    INSUFFICIENT_CANDLES = "INSUFFICIENT_CANDLES"
    WINDOW_NOT_ALIGNED = "WINDOW_NOT_ALIGNED"
    CANDLE_NOT_CLOSED = "CANDLE_NOT_CLOSED"
    CANDLE_AFTER_AS_OF = "CANDLE_AFTER_AS_OF"
    CANDLE_OUT_OF_RANGE = "CANDLE_OUT_OF_RANGE"
    CANDLE_PAIR_MISMATCH = "CANDLE_PAIR_MISMATCH"
    CANDLE_TIMEFRAME_MISMATCH = "CANDLE_TIMEFRAME_MISMATCH"
    DUPLICATE_CANDLE = "DUPLICATE_CANDLE"
    MISSING_CANDLE = "MISSING_CANDLE"
    EVENT_AFTER_AS_OF = "EVENT_AFTER_AS_OF"
    EVENT_OUT_OF_RANGE = "EVENT_OUT_OF_RANGE"


class FeatureIssue(BaseModel):
    code: FeatureIssueCode
    description: str = Field(min_length=1)
    timestamp: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class FeatureWindow(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("feature window_end must be later than window_start")
        return self


class CandleFeatureSummary(BaseModel):
    expected_candle_count: int = Field(ge=0)
    input_candle_count: int = Field(ge=0)
    used_candle_count: int = Field(ge=0)
    latest_close: Decimal | None = None
    first_candle_open_time: datetime | None = None
    latest_candle_close_time: datetime | None = None
    simple_return: Decimal | None = None
    per_candle_returns: tuple[Decimal, ...] = ()
    rolling_close_mean_window: int = Field(ge=1)
    rolling_close_means: tuple[Decimal, ...] = ()
    rolling_high_low_ranges: tuple[Decimal, ...] = ()
    average_candle_range: Decimal | None = None
    average_body_size: Decimal | None = None
    volume_observed_count: int = Field(default=0, ge=0)
    volume_sum: Decimal | None = None
    volume_average: Decimal | None = None
    true_ranges: tuple[Decimal, ...] = ()
    average_true_range: Decimal | None = None
    market_data_complete: bool

    model_config = ConfigDict(frozen=True)

    @field_validator("first_candle_open_time", "latest_candle_close_time")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class EconomicImpactCount(BaseModel):
    impact: EconomicImpact
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class CurrencyEventCount(BaseModel):
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class EconomicEventFeatureSummary(BaseModel):
    input_event_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    counts_by_impact: tuple[EconomicImpactCount, ...] = ()
    counts_by_currency: tuple[CurrencyEventCount, ...] = ()

    model_config = ConfigDict(frozen=True)


class MarketFeatureSnapshot(BaseModel):
    window: FeatureWindow
    candle_summary: CandleFeatureSummary
    economic_event_summary: EconomicEventFeatureSummary
    quality_issues: tuple[FeatureIssue, ...] = ()
    data_quality_issues: tuple[DataQualityIssue, ...] = ()

    model_config = ConfigDict(frozen=True)

    @property
    def quality_ok(self) -> bool:
        return not self.quality_issues and not self.data_quality_issues
