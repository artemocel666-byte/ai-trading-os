from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.time import normalize_to_utc
from app.domain.entities.context import MarketContextSnapshot
from app.domain.entities.features import MarketFeatureSnapshot
from app.domain.entities.market_data import Timeframe
from app.domain.value_objects import CurrencyPair


class AnalysisReadinessStatus(StrEnum):
    READY = "READY"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"


class AnalysisIssueCode(StrEnum):
    INVALID_WINDOW = "INVALID_WINDOW"
    NO_USABLE_CANDLES = "NO_USABLE_CANDLES"
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
    DATA_QUALITY_ISSUE = "DATA_QUALITY_ISSUE"
    SNAPSHOT_WINDOW_MISMATCH = "SNAPSHOT_WINDOW_MISMATCH"


class AnalysisWindow(BaseModel):
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


class AnalysisIssue(BaseModel):
    code: AnalysisIssueCode
    description: str = Field(min_length=1)
    source: str = Field(min_length=1)
    timestamp: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class AnalysisIssueCount(BaseModel):
    source: str = Field(min_length=1)
    code: AnalysisIssueCode
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class AnalysisInputAudit(BaseModel):
    requested_pair: CurrencyPair
    requested_timeframe: Timeframe
    provider: str | None = None
    requested_currencies: tuple[str, ...] = ()
    input_candle_count: int = Field(ge=0)
    used_candle_count: int = Field(ge=0)
    input_event_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    input_candles_after_as_of_count: int = Field(ge=0)
    input_events_after_as_of_count: int = Field(ge=0)
    excluded_issue_counts: tuple[AnalysisIssueCount, ...] = ()
    as_of: datetime
    latest_used_candle_close_time: datetime | None = None
    latest_used_event_time: datetime | None = None
    no_candles_after_as_of_used: bool
    no_events_after_as_of_used: bool

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of", "latest_used_candle_close_time", "latest_used_event_time")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class AnalysisSnapshotMetadata(BaseModel):
    project_phase: str = Field(min_length=1)
    snapshot_id: str = Field(min_length=64, max_length=64)
    feature_snapshot_id: str | None = Field(default=None, min_length=64, max_length=64)
    context_snapshot_id: str | None = Field(default=None, min_length=64, max_length=64)
    built_at: datetime
    source_layer: str = Field(min_length=1)

    model_config = ConfigDict(frozen=True)

    @field_validator("built_at")
    @classmethod
    def built_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class AnalysisSnapshot(BaseModel):
    window: AnalysisWindow
    metadata: AnalysisSnapshotMetadata
    input_audit: AnalysisInputAudit
    readiness_status: AnalysisReadinessStatus
    readiness_issues: tuple[AnalysisIssue, ...] = ()
    feature_snapshot: MarketFeatureSnapshot | None = None
    context_snapshot: MarketContextSnapshot | None = None

    model_config = ConfigDict(frozen=True)


class AnalysisReport(BaseModel):
    snapshot: AnalysisSnapshot
    ready_for_review: bool
    issue_count: int = Field(ge=0)
    used_candle_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    generated_at: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("generated_at")
    @classmethod
    def generated_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class AnalysisNumericSummary(BaseModel):
    value: Decimal | None = None

    model_config = ConfigDict(frozen=True)
