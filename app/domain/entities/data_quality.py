from collections import Counter
from collections.abc import Sequence
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.market_data import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair

TIMEFRAME_TO_DELTA = {Timeframe.M15: timedelta(minutes=15), Timeframe.H1: timedelta(hours=1)}


class DataQualityIssueCode(StrEnum):
    NO_CANDLES = "NO_CANDLES"
    WINDOW_NOT_ALIGNED = "WINDOW_NOT_ALIGNED"
    CANDLE_OUT_OF_RANGE = "CANDLE_OUT_OF_RANGE"
    CANDLE_PAIR_MISMATCH = "CANDLE_PAIR_MISMATCH"
    CANDLE_TIMEFRAME_MISMATCH = "CANDLE_TIMEFRAME_MISMATCH"
    DUPLICATE_CANDLE = "DUPLICATE_CANDLE"
    MISSING_CANDLE = "MISSING_CANDLE"
    EVENT_OUT_OF_RANGE = "EVENT_OUT_OF_RANGE"


class DataQualityIssue(BaseModel):
    code: DataQualityIssueCode
    description: str = Field(min_length=1)
    timestamp: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None


class UpsertResult(BaseModel):
    inserted: int = Field(ge=0)
    updated: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)

    @property
    def total(self) -> int:
        return self.inserted + self.updated


class CandleAvailability(BaseModel):
    expected_count: int = Field(ge=0)
    observed_count: int = Field(ge=0)
    missing_count: int = Field(ge=0)
    first_open_time: datetime | None = None
    last_close_time: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("first_open_time", "last_close_time")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime | None) -> datetime | None:
        return normalize_to_utc(value) if value is not None else None

    @property
    def is_complete(self) -> bool:
        return self.expected_count > 0 and self.observed_count == self.expected_count


class EconomicEventAvailability(BaseModel):
    event_count: int = Field(ge=0)
    currencies: tuple[str, ...] = ()
    high_impact_count: int = Field(default=0, ge=0)

    model_config = ConfigDict(frozen=True)


class FeatureSnapshot(BaseModel):
    pair: CurrencyPair
    timeframe: Timeframe
    window_start: datetime
    window_end: datetime
    candle_availability: CandleAvailability
    economic_event_availability: EconomicEventAvailability
    quality_issues: tuple[DataQualityIssue, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("window_start", "window_end")
    @classmethod
    def timestamps_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.window_end <= self.window_start:
            raise ValueError("snapshot window_end must be later than window_start")
        return self

    @property
    def market_data_complete(self) -> bool:
        blocking_codes = {
            DataQualityIssueCode.NO_CANDLES,
            DataQualityIssueCode.WINDOW_NOT_ALIGNED,
            DataQualityIssueCode.CANDLE_OUT_OF_RANGE,
            DataQualityIssueCode.CANDLE_PAIR_MISMATCH,
            DataQualityIssueCode.CANDLE_TIMEFRAME_MISMATCH,
            DataQualityIssueCode.DUPLICATE_CANDLE,
            DataQualityIssueCode.MISSING_CANDLE,
        }
        return self.candle_availability.is_complete and not any(
            issue.code in blocking_codes for issue in self.quality_issues
        )


def _expected_open_times(
    *,
    timeframe: Timeframe,
    window_start: datetime,
    window_end: datetime,
) -> tuple[datetime, ...]:
    delta = TIMEFRAME_TO_DELTA[timeframe]
    expected: list[datetime] = []
    cursor = window_start
    while cursor + delta <= window_end:
        expected.append(cursor)
        cursor += delta
    return tuple(expected)


def build_feature_snapshot(
    *,
    pair: CurrencyPair,
    timeframe: Timeframe,
    window_start: datetime,
    window_end: datetime,
    candles: Sequence[Candle],
    economic_events: Sequence[EconomicEvent] = (),
) -> FeatureSnapshot:
    start_utc = normalize_to_utc(window_start)
    end_utc = normalize_to_utc(window_end)
    if end_utc <= start_utc:
        raise ValueError("snapshot window_end must be later than window_start")

    expected_times = _expected_open_times(
        timeframe=timeframe,
        window_start=start_utc,
        window_end=end_utc,
    )
    issues: list[DataQualityIssue] = []
    delta = TIMEFRAME_TO_DELTA[timeframe]
    if start_utc + (len(expected_times) * delta) != end_utc:
        issues.append(
            DataQualityIssue(
                code=DataQualityIssueCode.WINDOW_NOT_ALIGNED,
                description="Requested window is not an exact multiple of the timeframe.",
            )
        )

    observed_times: list[datetime] = []
    matching_candles: list[Candle] = []
    for candle in candles:
        if candle.pair != pair:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.CANDLE_PAIR_MISMATCH,
                    description="Candle pair does not match the requested pair.",
                    timestamp=candle.open_time,
                )
            )
            continue
        if candle.timeframe != timeframe:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.CANDLE_TIMEFRAME_MISMATCH,
                    description="Candle timeframe does not match the requested timeframe.",
                    timestamp=candle.open_time,
                )
            )
            continue
        if candle.open_time < start_utc or candle.close_time > end_utc:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.CANDLE_OUT_OF_RANGE,
                    description="Candle is not fully contained in the requested window.",
                    timestamp=candle.open_time,
                )
            )
            continue
        matching_candles.append(candle)
        observed_times.append(candle.open_time)

    duplicates = [open_time for open_time, count in Counter(observed_times).items() if count > 1]
    for open_time in sorted(duplicates):
        issues.append(
            DataQualityIssue(
                code=DataQualityIssueCode.DUPLICATE_CANDLE,
                description="Duplicate candle open time in snapshot window.",
                timestamp=open_time,
            )
        )

    observed_unique = set(observed_times)
    for open_time in expected_times:
        if open_time not in observed_unique:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.MISSING_CANDLE,
                    description="Expected candle is missing from snapshot window.",
                    timestamp=open_time,
                )
            )

    if not matching_candles:
        issues.append(
            DataQualityIssue(
                code=DataQualityIssueCode.NO_CANDLES,
                description="No matching closed candles are available in the requested window.",
            )
        )

    event_currencies: set[str] = set()
    high_impact_count = 0
    event_count = 0
    for event in economic_events:
        if event.scheduled_at < start_utc or event.scheduled_at >= end_utc:
            issues.append(
                DataQualityIssue(
                    code=DataQualityIssueCode.EVENT_OUT_OF_RANGE,
                    description="Economic event is outside the requested window.",
                    timestamp=event.scheduled_at,
                )
            )
            continue
        event_count += 1
        event_currencies.add(event.currency)
        if event.impact == EconomicImpact.HIGH:
            high_impact_count += 1

    return FeatureSnapshot(
        pair=pair,
        timeframe=timeframe,
        window_start=start_utc,
        window_end=end_utc,
        candle_availability=CandleAvailability(
            expected_count=len(expected_times),
            observed_count=len(observed_unique),
            missing_count=max(len(expected_times) - len(observed_unique), 0),
            first_open_time=min(observed_times) if observed_times else None,
            last_close_time=max((candle.close_time for candle in matching_candles), default=None),
        ),
        economic_event_availability=EconomicEventAvailability(
            event_count=event_count,
            currencies=tuple(sorted(event_currencies)),
            high_impact_count=high_impact_count,
        ),
        quality_issues=tuple(issues),
    )
