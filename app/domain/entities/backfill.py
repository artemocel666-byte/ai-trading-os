from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Timeframe
from app.domain.value_objects import CurrencyPair


class BackfillChunkResult(BaseModel):
    """One provider request inside a backfill run.

    `possibly_truncated` marks a chunk whose oldest returned candle sits far later than the
    requested start. A provider result cap drops the oldest bars, so that leading gap is the
    signal — the returned count alone is not, because a quiet weekend legitimately returns few
    candles without anything being dropped.
    """

    chunk_start: datetime
    chunk_end: datetime
    fetched_count: int = Field(default=0, ge=0)
    inserted_count: int = Field(default=0, ge=0)
    updated_count: int = Field(default=0, ge=0)
    first_candle_open_time: datetime | None = None
    last_candle_open_time: datetime | None = None
    failed: bool = False
    #: Why the chunk failed, as the exception's type name. Added in Phase 9D-1, where a universe
    #: fill left five-year holes in most pairs and the result recorded only `failed=True` — so the
    #: run could say *that* something went wrong and never *what*, and the cause had to be guessed
    #: from the shape of the gaps. Deliberately the type name and not the message: a message can
    #: carry a request URL, and a request URL carries the API key.
    failure_reason: str | None = None
    possibly_truncated: bool = False

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def only_a_failure_explains_itself(self) -> Self:
        if self.failure_reason is not None and not self.failed:
            raise ValueError("a chunk that did not fail cannot carry a failure reason")
        return self

    @field_validator(
        "chunk_start",
        "chunk_end",
        "first_candle_open_time",
        "last_candle_open_time",
    )
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None

    @model_validator(mode="after")
    def validate_chunk(self) -> Self:
        if self.chunk_end <= self.chunk_start:
            raise ValueError("backfill chunk_end must be later than chunk_start")
        if self.failed and (self.fetched_count or self.inserted_count or self.updated_count):
            raise ValueError("a failed backfill chunk must not report stored candle counts")
        if self.failed and self.possibly_truncated:
            raise ValueError("a failed backfill chunk cannot also be reported as truncated")
        if self.inserted_count + self.updated_count > self.fetched_count:
            raise ValueError("stored candle counts must not exceed the fetched candle count")
        if self.fetched_count == 0 and self.possibly_truncated:
            raise ValueError("an empty backfill chunk must not be reported as truncated")
        return self


class BackfillResult(BaseModel):
    project_phase: str = Field(default_factory=lambda: constants.PROJECT_PHASE, min_length=1)
    pair: CurrencyPair
    timeframe: Timeframe
    requested_start: datetime
    requested_end: datetime
    chunk_results: tuple[BackfillChunkResult, ...] = ()
    total_fetched: int = Field(default=0, ge=0)
    total_inserted: int = Field(default=0, ge=0)
    total_updated: int = Field(default=0, ge=0)
    failed_chunk_count: int = Field(default=0, ge=0)
    truncated_chunk_count: int = Field(default=0, ge=0)
    succeeded: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("requested_start", "requested_end")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_totals(self) -> Self:
        if self.requested_end <= self.requested_start:
            raise ValueError("backfill requested_end must be later than requested_start")
        if self.total_fetched != sum(chunk.fetched_count for chunk in self.chunk_results):
            raise ValueError("total_fetched must match the sum of chunk results")
        if self.total_inserted != sum(chunk.inserted_count for chunk in self.chunk_results):
            raise ValueError("total_inserted must match the sum of chunk results")
        if self.total_updated != sum(chunk.updated_count for chunk in self.chunk_results):
            raise ValueError("total_updated must match the sum of chunk results")
        if self.failed_chunk_count != sum(1 for chunk in self.chunk_results if chunk.failed):
            raise ValueError("failed_chunk_count must match the failed chunk results")
        if self.truncated_chunk_count != sum(
            1 for chunk in self.chunk_results if chunk.possibly_truncated
        ):
            raise ValueError("truncated_chunk_count must match the truncated chunk results")
        # A run only counts as successful when nothing failed and nothing looked truncated:
        # partially filled history would silently corrupt any later calibration.
        expected_success = (
            bool(self.chunk_results)
            and self.failed_chunk_count == 0
            and self.truncated_chunk_count == 0
        )
        if self.succeeded != expected_success:
            raise ValueError("succeeded must mean every chunk completed without truncation")
        return self
