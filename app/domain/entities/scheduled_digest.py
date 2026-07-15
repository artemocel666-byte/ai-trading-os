from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.readiness import (
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)


class ScheduledDigestDecisionReason(StrEnum):
    DISABLED = "DISABLED"
    NOT_DUE = "NOT_DUE"
    DUE = "DUE"
    DUPLICATE = "DUPLICATE"
    NO_ITEMS = "NO_ITEMS"
    BUILD_FAILED = "BUILD_FAILED"
    DELIVERED = "DELIVERED"


class ScheduledDigestConfig(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool = False
    interval_minutes: int = Field(default=60, ge=1, le=1440)
    items: tuple[SnapshotScheduleItem, ...] = ()

    model_config = ConfigDict(frozen=True)


class ScheduledDigestTick(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class ScheduledDigestDecision(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool
    is_due: bool
    should_build: bool
    reason: ScheduledDigestDecisionReason
    item_count: int = Field(ge=0)
    tick_as_of: datetime
    dedup_key: SnapshotNotificationDedupKey | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("tick_as_of")
    @classmethod
    def tick_as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.should_build and not self.is_due:
            raise ValueError("scheduled digest cannot build when tick is not due")
        if self.should_build and not self.enabled:
            raise ValueError("scheduled digest cannot build while disabled")
        return self


class ScheduledDigestDeliveryRecord(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    dedup_key: SnapshotNotificationDedupKey
    delivered_at: datetime
    sender_name: str = Field(min_length=1)

    model_config = ConfigDict(frozen=True)

    @field_validator("delivered_at")
    @classmethod
    def delivered_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class ScheduledDigestDeliveryResult(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    tick: ScheduledDigestTick
    decision: ScheduledDigestDecision
    delivered: bool
    skipped: bool
    dedup_key: SnapshotNotificationDedupKey | None = None
    payload: SnapshotNotificationPayload | None = None
    record: ScheduledDigestDeliveryRecord | None = None

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.delivered == self.skipped:
            raise ValueError("scheduled digest result must be either delivered or skipped")
        if self.delivered and self.record is None:
            raise ValueError("delivered scheduled digest result requires a record")
        if self.skipped and self.record is not None:
            raise ValueError("skipped scheduled digest result must not include a record")
        return self
