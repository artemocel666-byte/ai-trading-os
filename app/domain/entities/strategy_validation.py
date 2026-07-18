import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.strategy_rules import StrategyRuleSeverity


class StrategyRuleSetValidationStatus(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    WARNING = "WARNING"


class StrategyRuleSetValidationIssueCode(StrEnum):
    EMPTY_RULESET = "EMPTY_RULESET"
    DUPLICATE_RULE_ID = "DUPLICATE_RULE_ID"
    RULESET_ENABLED = "RULESET_ENABLED"
    RULE_ENABLED = "RULE_ENABLED"
    UNKNOWN_FIELD_REF = "UNKNOWN_FIELD_REF"
    CATEGORY_FIELD_MISMATCH = "CATEGORY_FIELD_MISMATCH"
    FORBIDDEN_FIELD_REF = "FORBIDDEN_FIELD_REF"
    FORBIDDEN_EXECUTION_LANGUAGE = "FORBIDDEN_EXECUTION_LANGUAGE"
    FORBIDDEN_SCORING_LANGUAGE = "FORBIDDEN_SCORING_LANGUAGE"
    FORBIDDEN_CONFIDENCE_LANGUAGE = "FORBIDDEN_CONFIDENCE_LANGUAGE"
    INVALID_OPERATOR_OPERANDS = "INVALID_OPERATOR_OPERANDS"


def _normalize_optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


def _normalize_required_string(value: object, field_name: str) -> str:
    normalized = _normalize_optional_string(value, field_name)
    if normalized is None:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


class StrategyRuleSetValidationIssue(BaseModel):
    code: StrategyRuleSetValidationIssueCode
    message: str = Field(min_length=1, max_length=1000)
    rule_id: str | None = None
    field_ref: str | None = None
    severity: StrategyRuleSeverity

    model_config = ConfigDict(frozen=True)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return _normalize_required_string(value, "message")

    @field_validator("rule_id", "field_ref", mode="before")
    @classmethod
    def normalize_optional_identifiers(cls, value: object) -> str | None:
        return _normalize_optional_string(value, "validation issue identifier")

    @property
    def sort_key(self) -> tuple[str, str, str, str]:
        return (
            self.code.value,
            self.rule_id or "",
            self.field_ref or "",
            self.message,
        )


class StrategyRuleSetValidationReport(BaseModel):
    ruleset_version: str = Field(min_length=1)
    strategy_version: str = Field(min_length=1)
    ruleset_name: str = Field(min_length=1, max_length=120)
    status: StrategyRuleSetValidationStatus
    checked_at: datetime
    issues: tuple[StrategyRuleSetValidationIssue, ...] = ()
    rule_count: int = Field(ge=0)
    enabled_rule_count: int = Field(ge=0)
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("ruleset_version", "strategy_version", "ruleset_name", mode="before")
    @classmethod
    def normalize_required_strings(cls, value: object) -> str:
        return _normalize_required_string(value, "validation report string")

    @field_validator("checked_at")
    @classmethod
    def checked_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("issues")
    @classmethod
    def normalize_issues(
        cls,
        value: tuple[StrategyRuleSetValidationIssue, ...],
    ) -> tuple[StrategyRuleSetValidationIssue, ...]:
        return tuple(sorted(value, key=lambda issue: issue.sort_key))

    @model_validator(mode="after")
    def validate_counts_and_status(self) -> Self:
        if self.enabled_rule_count > self.rule_count:
            raise ValueError("enabled_rule_count must not exceed rule_count")
        if self.status == StrategyRuleSetValidationStatus.VALID and self.issues:
            raise ValueError("VALID validation reports must not contain issues")
        if self.status != StrategyRuleSetValidationStatus.VALID and not self.issues:
            raise ValueError("non-VALID validation reports must contain issues")
        return self

    @property
    def is_actionable(self) -> bool:
        return False

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
