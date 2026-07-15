from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisReadinessStatus
from app.domain.entities.market_data import Timeframe
from app.domain.value_objects import CurrencyPair


class SnapshotDigestStatus(StrEnum):
    READY = "READY"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"


class SnapshotNotificationDedupKey(BaseModel):
    value: str = Field(min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)


class SnapshotScheduleItem(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    lookback_candle_count: int = Field(ge=1)
    provider: str | None = None
    currencies: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("currencies")
    @classmethod
    def currencies_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class SnapshotWindow(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    as_of: datetime
    lookback_candle_count: int = Field(ge=1)
    provider: str | None = None
    currencies: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("snapshot window_end must be later than window_start")
        if self.window_end > self.as_of:
            raise ValueError("snapshot window_end must not be later than as_of")
        return self


class SnapshotSchedulePlan(BaseModel):
    project_phase: str = Field(min_length=1)
    as_of: datetime
    windows: tuple[SnapshotWindow, ...]

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class SnapshotDigestIssueCount(BaseModel):
    source: str = Field(min_length=1)
    code: str = Field(min_length=1)
    count: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)


class SnapshotDigestItem(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    as_of: datetime
    readiness_status: SnapshotDigestStatus
    input_candle_count: int = Field(ge=0)
    used_candle_count: int = Field(ge=0)
    input_event_count: int = Field(ge=0)
    used_event_count: int = Field(ge=0)
    issue_count: int = Field(ge=0)
    issue_counts: tuple[SnapshotDigestIssueCount, ...] = ()
    issue_descriptions: tuple[str, ...] = ()
    no_candles_after_as_of_used: bool
    no_events_after_as_of_used: bool
    snapshot_id: str = Field(min_length=64, max_length=64)
    dedup_key: SnapshotNotificationDedupKey

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class SnapshotDigest(BaseModel):
    project_phase: str = Field(min_length=1)
    generated_at: datetime
    as_of: datetime
    readiness_status: SnapshotDigestStatus
    items: tuple[SnapshotDigestItem, ...]
    ready_count: int = Field(ge=0)
    incomplete_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    dedup_key: SnapshotNotificationDedupKey

    model_config = ConfigDict(frozen=True)

    @field_validator("generated_at", "as_of")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class SnapshotNotificationPayload(BaseModel):
    project_phase: str = Field(min_length=1)
    dedup_key: SnapshotNotificationDedupKey
    digest: SnapshotDigest
    text: str = Field(min_length=1)

    model_config = ConfigDict(frozen=True)


def digest_status_from_analysis(status: AnalysisReadinessStatus) -> SnapshotDigestStatus:
    return SnapshotDigestStatus(status.value)
