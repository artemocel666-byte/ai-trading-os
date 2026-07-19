import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.strategy_rules import StrategyRuleSeverity


class DisabledPipelineStatus(StrEnum):
    DISABLED = "DISABLED"
    BLOCKED = "BLOCKED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"


class DisabledPipelineBlockerCode(StrEnum):
    PIPELINE_DISABLED = "PIPELINE_DISABLED"
    REGISTRY_INVALID = "REGISTRY_INVALID"
    REGISTRY_EMPTY = "REGISTRY_EMPTY"
    ACTIONABLE_ITEM_FOUND = "ACTIONABLE_ITEM_FOUND"
    RUNTIME_NOT_ALLOWED = "RUNTIME_NOT_ALLOWED"


def _normalize_required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


def _normalize_optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_required_string(value, field_name)


class DisabledPipelineBlocker(BaseModel):
    code: DisabledPipelineBlockerCode
    message: str = Field(min_length=1, max_length=1000)
    registry_key: str | None = None
    severity: StrategyRuleSeverity

    model_config = ConfigDict(frozen=True)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> str:
        return _normalize_required_string(value, "message")

    @field_validator("registry_key", mode="before")
    @classmethod
    def normalize_registry_key(cls, value: object) -> str | None:
        return _normalize_optional_string(value, "registry_key")

    @property
    def sort_key(self) -> tuple[str, str, str]:
        return (self.code.value, self.registry_key or "", self.message)


class DisabledPipelineReport(BaseModel):
    pipeline_version: str = Field(min_length=1)
    project_phase: str = Field(min_length=1)
    status: DisabledPipelineStatus
    created_at: datetime
    registry_item_count: int = Field(ge=0)
    valid_registry_item_count: int = Field(ge=0)
    invalid_registry_item_count: int = Field(ge=0)
    blockers: tuple[DisabledPipelineBlocker, ...] = ()
    registry_snapshot_fingerprint: str = Field(min_length=64, max_length=64)
    enabled_for_runtime: bool = False
    is_actionable: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("pipeline_version", "project_phase", mode="before")
    @classmethod
    def normalize_required_identifiers(cls, value: object) -> str:
        return _normalize_required_string(value, "disabled pipeline report identifier")

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("blockers")
    @classmethod
    def normalize_blockers(
        cls,
        value: tuple[DisabledPipelineBlocker, ...],
    ) -> tuple[DisabledPipelineBlocker, ...]:
        return tuple(sorted(value, key=lambda blocker: blocker.sort_key))

    @model_validator(mode="after")
    def validate_counts_and_flags(self) -> Self:
        if self.valid_registry_item_count + self.invalid_registry_item_count != (
            self.registry_item_count
        ):
            raise ValueError("registry report counts must add up to registry_item_count")
        if self.enabled_for_runtime:
            raise ValueError("disabled pipeline reports must remain disabled for runtime use")
        if self.is_actionable:
            raise ValueError("disabled pipeline reports must remain non-actionable")
        if self.status == DisabledPipelineStatus.READY_FOR_REVIEW and self.blockers:
            raise ValueError("READY_FOR_REVIEW reports must not contain blockers")
        if self.status != DisabledPipelineStatus.READY_FOR_REVIEW and not self.blockers:
            raise ValueError("disabled or blocked reports must contain blockers")
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
