from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.features import MarketFeatureSnapshot
from app.domain.entities.market_data import EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair


class ContextIssueCode(StrEnum):
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


class ContextIssue(BaseModel):
    code: ContextIssueCode
    description: str = Field(min_length=1)
    timestamp: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class IndicatorWindow(BaseModel):
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
            raise ValueError("context window_end must be later than window_start")
        return self


class ReturnDistributionSummary(BaseModel):
    close_values: tuple[Decimal, ...] = ()
    close_change_values: tuple[Decimal, ...] = ()
    per_candle_returns: tuple[Decimal, ...] = ()
    cumulative_return: Decimal | None = None
    mean_return: Decimal | None = None
    median_return: Decimal | None = None
    min_return: Decimal | None = None
    max_return: Decimal | None = None
    return_standard_deviation: Decimal | None = None
    realized_volatility: Decimal | None = None
    max_close_to_close_drawdown: Decimal | None = None

    model_config = ConfigDict(frozen=True)


class MovingAverageSeries(BaseModel):
    window_size: int = Field(ge=1)
    values: tuple[Decimal, ...] = ()

    model_config = ConfigDict(frozen=True)


class MovingAverageSummary(BaseModel):
    close_mean_series: tuple[MovingAverageSeries, ...] = ()
    return_mean_series: tuple[MovingAverageSeries, ...] = ()

    model_config = ConfigDict(frozen=True)


class RangeContextSummary(BaseModel):
    true_range_values: tuple[Decimal, ...] = ()
    average_true_range: Decimal | None = None
    candle_range_values: tuple[Decimal, ...] = ()
    average_candle_range: Decimal | None = None
    range_change_ratios: tuple[Decimal | None, ...] = ()

    model_config = ConfigDict(frozen=True)


class CandleShapeSummary(BaseModel):
    body_sizes: tuple[Decimal, ...] = ()
    average_body_size: Decimal | None = None
    upper_wick_sizes: tuple[Decimal, ...] = ()
    lower_wick_sizes: tuple[Decimal, ...] = ()
    average_upper_wick_size: Decimal | None = None
    average_lower_wick_size: Decimal | None = None
    body_to_range_ratios: tuple[Decimal | None, ...] = ()
    close_location_in_range_values: tuple[Decimal | None, ...] = ()

    model_config = ConfigDict(frozen=True)


class ContextImpactCount(BaseModel):
    impact: EconomicImpact
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class ContextCurrencyCount(BaseModel):
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class EventContextSummary(BaseModel):
    input_event_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    counts_by_impact: tuple[ContextImpactCount, ...] = ()
    counts_by_currency: tuple[ContextCurrencyCount, ...] = ()
    latest_event_time: datetime | None = None
    minutes_since_latest_event: Decimal | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("latest_event_time")
    @classmethod
    def latest_event_time_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class TimeContextSummary(BaseModel):
    as_of_utc_hour: int = Field(ge=0, le=23)
    as_of_utc_weekday: int = Field(ge=0, le=6)
    window_minutes: Decimal = Field(ge=Decimal("0"))
    candle_count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class MarketContextSnapshot(BaseModel):
    window: IndicatorWindow
    feature_snapshot: MarketFeatureSnapshot
    return_distribution: ReturnDistributionSummary
    moving_average_summary: MovingAverageSummary
    range_context: RangeContextSummary
    candle_shape: CandleShapeSummary
    event_context: EventContextSummary
    time_context: TimeContextSummary
    context_issues: tuple[ContextIssue, ...] = ()

    model_config = ConfigDict(frozen=True)

    @property
    def quality_ok(self) -> bool:
        return (
            not self.context_issues
            and not self.feature_snapshot.quality_issues
            and not self.feature_snapshot.data_quality_issues
        )
