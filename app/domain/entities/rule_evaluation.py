import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.strategy_rules import StrategyRuleCategory, StrategyRuleSeverity


class RuleEvaluationStatus(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"


class RuleSetEvaluationStatus(StrEnum):
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


def _normalize_required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


class RuleEvaluationResult(BaseModel):
    rule_id: str = Field(min_length=1)
    category: StrategyRuleCategory
    severity: StrategyRuleSeverity
    field_ref: str = Field(min_length=1)
    status: RuleEvaluationStatus
    resolved_value_present: bool

    model_config = ConfigDict(frozen=True)

    @field_validator("rule_id", "field_ref", mode="before")
    @classmethod
    def normalize_identifiers(cls, value: object) -> str:
        return _normalize_required_string(value, "rule evaluation identifier")

    @model_validator(mode="after")
    def resolved_value_presence_must_match_status(self) -> Self:
        if self.status == RuleEvaluationStatus.UNAVAILABLE and self.resolved_value_present:
            raise ValueError("UNAVAILABLE results must not report a resolved value as present")
        if self.status != RuleEvaluationStatus.UNAVAILABLE and not self.resolved_value_present:
            raise ValueError("PASSED and FAILED results must report a resolved value as present")
        return self

    @property
    def sort_key(self) -> tuple[str, str]:
        return (self.rule_id, self.field_ref)


class RuleSetEvaluationReport(BaseModel):
    ruleset_version: str = Field(min_length=1)
    strategy_version: str = Field(min_length=1)
    ruleset_name: str = Field(min_length=1, max_length=120)
    status: RuleSetEvaluationStatus
    evaluated_at: datetime
    source_snapshot_id: str = Field(min_length=64, max_length=64)
    results: tuple[RuleEvaluationResult, ...] = ()
    blocking_failure_count: int = Field(ge=0)
    required_failure_count: int = Field(ge=0)
    warning_failure_count: int = Field(ge=0)
    is_actionable: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("ruleset_version", "strategy_version", "ruleset_name", mode="before")
    @classmethod
    def normalize_required_strings(cls, value: object) -> str:
        return _normalize_required_string(value, "rule set evaluation report string")

    @field_validator("evaluated_at")
    @classmethod
    def evaluated_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("results")
    @classmethod
    def normalize_results(
        cls,
        value: tuple[RuleEvaluationResult, ...],
    ) -> tuple[RuleEvaluationResult, ...]:
        return tuple(sorted(value, key=lambda result: result.sort_key))

    @model_validator(mode="after")
    def validate_counts_and_status(self) -> Self:
        if self.is_actionable:
            raise ValueError("rule set evaluation reports must remain non-actionable")
        if self.blocking_failure_count > 0 and self.status != RuleSetEvaluationStatus.BLOCKED:
            raise ValueError("a blocking failure must produce a BLOCKED status")
        if (
            self.blocking_failure_count == 0
            and self.required_failure_count > 0
            and self.status != RuleSetEvaluationStatus.NOT_READY
        ):
            raise ValueError("a required failure without a blocking failure must be NOT_READY")
        if (
            self.blocking_failure_count == 0
            and self.required_failure_count == 0
            and self.status != RuleSetEvaluationStatus.READY_FOR_REVIEW
        ):
            raise ValueError("no blocking or required failures must be READY_FOR_REVIEW")
        return self

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"fingerprint"})

    def deterministic_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint_sha256(self) -> str:
        canonical = json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
