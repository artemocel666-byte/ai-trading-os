from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import AgentVerdict, ConfidenceLevel, Direction
from app.core.time import normalize_to_utc
from app.domain.value_objects import CurrencyPair


class EvidenceReference(BaseModel):
    evidence_type: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    candle_timestamp: datetime
    metric_name: str = Field(min_length=1)
    metric_value: Decimal
    source: str = Field(min_length=1)

    model_config = ConfigDict(frozen=True)

    @field_validator("candle_timestamp")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("metric_value", mode="before")
    @classmethod
    def reject_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("metric_value must use Decimal-compatible inputs, not float")
        return value


class AgentReport(BaseModel):
    report_id: UUID = Field(default_factory=uuid4)
    scan_id: UUID
    agent_name: str = Field(min_length=1)
    pair: CurrencyPair
    direction: Direction
    verdict: AgentVerdict
    score: int = Field(ge=0, le=100)
    confidence: ConfidenceLevel
    summary_ru: str = Field(min_length=1)
    reasons_for_ru: list[str] = Field(min_length=1)
    reasons_against_ru: list[str] = Field(min_length=1)
    invalid_if_ru: list[str] = Field(min_length=1)
    evidence: list[EvidenceReference] = Field(min_length=1)
    data_timestamp: datetime
    rule_version: str = Field(min_length=1)
    model_version: str | None = None
    created_at: datetime

    @field_validator("summary_ru")
    @classmethod
    def summary_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("summary_ru must not be blank")
        return value

    @field_validator("reasons_for_ru", "reasons_against_ru", "invalid_if_ru")
    @classmethod
    def list_items_must_not_be_blank(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            raise ValueError("explanation list items must not be blank")
        return value

    @field_validator("data_timestamp", "created_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)


class ChiefAIRequest(BaseModel):
    """Future Chief AI input contract with deterministic fields locked by callers."""

    deterministic_decision: str
    setup_score: int = Field(ge=0, le=100)
    risk_percent: Decimal = Field(ge=Decimal("0"))
    agent_reports: list[AgentReport] = Field(min_length=1)
    deterministic_context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("risk_percent", mode="before")
    @classmethod
    def reject_float(cls, value: object) -> object:
        if isinstance(value, float):
            raise ValueError("risk_percent must use Decimal-compatible inputs, not float")
        return value
