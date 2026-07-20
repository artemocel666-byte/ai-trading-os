import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.rule_evaluation import RuleSetEvaluationReport, RuleSetEvaluationStatus


class PipelineDecisionStatus(StrEnum):
    BLOCKED = "BLOCKED"
    NOT_READY = "NOT_READY"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


class SkippedRulesetReason(StrEnum):
    INVALID_VALIDATION = "INVALID_VALIDATION"


def _normalize_required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


class SkippedRuleset(BaseModel):
    registry_key: str = Field(min_length=1)
    reason: SkippedRulesetReason

    model_config = ConfigDict(frozen=True)

    @field_validator("registry_key", mode="before")
    @classmethod
    def normalize_registry_key(cls, value: object) -> str:
        return _normalize_required_string(value, "registry_key")


class PipelineDecisionReport(BaseModel):
    pipeline_version: str = Field(min_length=1)
    project_phase: str = Field(min_length=1)
    status: PipelineDecisionStatus
    evaluated_at: datetime
    source_snapshot_id: str = Field(min_length=64, max_length=64)
    ruleset_reports: tuple[RuleSetEvaluationReport, ...] = ()
    skipped_rulesets: tuple[SkippedRuleset, ...] = ()
    evaluated_ruleset_count: int = Field(ge=0)
    blocked_ruleset_count: int = Field(ge=0)
    not_ready_ruleset_count: int = Field(ge=0)
    is_actionable: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("pipeline_version", "project_phase", mode="before")
    @classmethod
    def normalize_required_identifiers(cls, value: object) -> str:
        return _normalize_required_string(value, "pipeline decision report identifier")

    @field_validator("evaluated_at")
    @classmethod
    def evaluated_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("ruleset_reports")
    @classmethod
    def normalize_ruleset_reports(
        cls,
        value: tuple[RuleSetEvaluationReport, ...],
    ) -> tuple[RuleSetEvaluationReport, ...]:
        return tuple(sorted(value, key=lambda report: report.ruleset_name))

    @field_validator("skipped_rulesets")
    @classmethod
    def normalize_skipped_rulesets(
        cls,
        value: tuple[SkippedRuleset, ...],
    ) -> tuple[SkippedRuleset, ...]:
        return tuple(sorted(value, key=lambda skipped: skipped.registry_key))

    @model_validator(mode="after")
    def validate_counts_and_status(self) -> Self:
        if self.is_actionable:
            raise ValueError("pipeline decision reports must remain non-actionable")
        if self.evaluated_ruleset_count != len(self.ruleset_reports):
            raise ValueError("evaluated_ruleset_count must match ruleset_reports length")
        blocked_count = sum(
            1 for report in self.ruleset_reports if report.status == RuleSetEvaluationStatus.BLOCKED
        )
        not_ready_count = sum(
            1
            for report in self.ruleset_reports
            if report.status == RuleSetEvaluationStatus.NOT_READY
        )
        if self.blocked_ruleset_count != blocked_count:
            raise ValueError("blocked_ruleset_count must match BLOCKED ruleset_reports")
        if self.not_ready_ruleset_count != not_ready_count:
            raise ValueError("not_ready_ruleset_count must match NOT_READY ruleset_reports")
        if self.blocked_ruleset_count > 0 and self.status != PipelineDecisionStatus.BLOCKED:
            raise ValueError("a blocked ruleset must produce a BLOCKED pipeline status")
        if (
            self.blocked_ruleset_count == 0
            and self.not_ready_ruleset_count > 0
            and self.status != PipelineDecisionStatus.NOT_READY
        ):
            raise ValueError("a not-ready ruleset without a blocked ruleset must be NOT_READY")
        if (
            self.blocked_ruleset_count == 0
            and self.not_ready_ruleset_count == 0
            and self.status != PipelineDecisionStatus.READY_FOR_REVIEW
        ):
            raise ValueError("no blocked or not-ready rulesets must be READY_FOR_REVIEW")
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
