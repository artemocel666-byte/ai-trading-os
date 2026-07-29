from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc


class CalendarIngestionDecisionReason(StrEnum):
    DISABLED = "DISABLED"
    NO_CURRENCIES = "NO_CURRENCIES"
    COMPLETED = "COMPLETED"


class CalendarIngestionConfig(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool = False
    interval_minutes: int = Field(default=60, ge=1, le=1440)
    lookback_hours: int = Field(default=24, ge=1, le=168)
    horizon_hours: int = Field(default=72, ge=1, le=336)
    currencies: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("currencies")
    @classmethod
    def currencies_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted({currency.upper() for currency in value}))


class CalendarIngestionTick(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class CalendarIngestionDecision(BaseModel):
    """Whether a tick should fetch.

    Cadence belongs to the scheduler that invokes the tick, not to this decision; only
    configuration gates live here.
    """

    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool
    should_fetch: bool
    reason: CalendarIngestionDecisionReason
    currency_count: int = Field(ge=0)
    tick_as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("tick_as_of")
    @classmethod
    def tick_as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.should_fetch and not self.enabled:
            raise ValueError("calendar ingestion cannot fetch while disabled")
        if self.should_fetch and self.currency_count == 0:
            raise ValueError("calendar ingestion cannot fetch without configured currencies")
        return self


class CalendarIngestionResult(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    tick: CalendarIngestionTick
    decision: CalendarIngestionDecision
    executed: bool
    skipped: bool
    succeeded: bool = False
    failed: bool = False
    window_start: datetime | None = None
    window_end: datetime | None = None
    fetched_count: int = Field(default=0, ge=0)
    inserted_count: int = Field(default=0, ge=0)
    updated_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.executed == self.skipped:
            raise ValueError("calendar ingestion result must be either executed or skipped")
        if self.skipped and (self.succeeded or self.failed):
            raise ValueError("a skipped calendar ingestion result has no outcome")
        if self.executed and self.succeeded == self.failed:
            raise ValueError("an executed calendar ingestion result must succeed or fail")
        if self.failed and (self.fetched_count or self.inserted_count or self.updated_count):
            raise ValueError("a failed calendar ingestion result must not report stored counts")
        if self.inserted_count + self.updated_count > self.fetched_count:
            raise ValueError("stored event counts must not exceed the fetched event count")
        if self.executed and (self.window_start is None or self.window_end is None):
            raise ValueError("an executed calendar ingestion result requires a window")
        if (
            self.window_start is not None
            and self.window_end is not None
            and self.window_end <= self.window_start
        ):
            raise ValueError("calendar ingestion window_end must be later than window_start")
        return self
