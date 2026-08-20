from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Timeframe
from app.domain.entities.readiness import SnapshotScheduleItem
from app.domain.value_objects import CurrencyPair


class MarketDataIngestionDecisionReason(StrEnum):
    DISABLED = "DISABLED"
    NO_ITEMS = "NO_ITEMS"
    COMPLETED = "COMPLETED"


class MarketDataIngestionConfig(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool = False
    interval_minutes: int = Field(default=15, ge=1, le=1440)
    lookback_candles: int = Field(default=48, ge=1, le=500)
    items: tuple[SnapshotScheduleItem, ...] = ()

    model_config = ConfigDict(frozen=True)


class MarketDataIngestionTick(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("as_of")
    @classmethod
    def as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class MarketDataIngestionDecision(BaseModel):
    """Whether a tick should fetch.

    Cadence is owned by the scheduler that invokes the tick, not by this decision: the
    ingestion windows deliberately overlap, so the exact firing moment does not matter.
    Only configuration gates live here.
    """

    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    enabled: bool
    should_fetch: bool
    reason: MarketDataIngestionDecisionReason
    item_count: int = Field(ge=0)
    tick_as_of: datetime

    model_config = ConfigDict(frozen=True)

    @field_validator("tick_as_of")
    @classmethod
    def tick_as_of_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.should_fetch and not self.enabled:
            raise ValueError("market data ingestion cannot fetch while disabled")
        if self.should_fetch and self.item_count == 0:
            raise ValueError("market data ingestion cannot fetch without configured items")
        return self


class MarketDataIngestionItemResult(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    fetched_count: int = Field(default=0, ge=0)
    inserted_count: int = Field(default=0, ge=0)
    updated_count: int = Field(default=0, ge=0)
    failed: bool = False
    #: The exception's **type name** when this item failed, never its message. Phase 9D-1 gave the
    #: backfill result the same field and it separated two causes that had looked identical; a
    #: provider message can quote a URL carrying the API key, so only the type travels.
    failure_reason: str | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_item_result(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("ingestion window_end must be later than window_start")
        if self.failed and (self.fetched_count or self.inserted_count or self.updated_count):
            raise ValueError("a failed ingestion item must not report stored candle counts")
        if not self.failed and self.failure_reason is not None:
            raise ValueError("an item that did not fail cannot carry a failure reason")
        if self.inserted_count + self.updated_count > self.fetched_count:
            raise ValueError("stored candle counts must not exceed the fetched candle count")
        return self

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.pair.value, self.timeframe.value)


class MarketDataIngestionResult(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    tick: MarketDataIngestionTick
    decision: MarketDataIngestionDecision
    executed: bool
    skipped: bool
    succeeded: bool = False
    item_results: tuple[MarketDataIngestionItemResult, ...] = ()
    total_fetched: int = Field(default=0, ge=0)
    total_inserted: int = Field(default=0, ge=0)
    total_updated: int = Field(default=0, ge=0)
    failed_item_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)

    @field_validator("item_results")
    @classmethod
    def normalize_item_results(
        cls,
        value: tuple[MarketDataIngestionItemResult, ...],
    ) -> tuple[MarketDataIngestionItemResult, ...]:
        return tuple(sorted(value, key=lambda item: item.sort_key))

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.executed == self.skipped:
            raise ValueError("ingestion result must be either executed or skipped")
        if self.skipped and self.item_results:
            raise ValueError("a skipped ingestion result must not include item results")
        if self.skipped and self.succeeded:
            raise ValueError("a skipped ingestion result cannot be marked successful")
        if self.total_fetched != sum(item.fetched_count for item in self.item_results):
            raise ValueError("total_fetched must match the sum of item results")
        if self.total_inserted != sum(item.inserted_count for item in self.item_results):
            raise ValueError("total_inserted must match the sum of item results")
        if self.total_updated != sum(item.updated_count for item in self.item_results):
            raise ValueError("total_updated must match the sum of item results")
        if self.failed_item_count != sum(1 for item in self.item_results if item.failed):
            raise ValueError("failed_item_count must match the failed item results")
        if self.executed and self.succeeded and self.failed_item_count == len(self.item_results):
            raise ValueError("a successful ingestion result requires at least one succeeded item")
        return self
