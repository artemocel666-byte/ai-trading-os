import hashlib
import json
from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.time import normalize_to_utc
from app.domain.entities.strategy_rules import StrategyRuleSet
from app.domain.entities.strategy_validation import (
    StrategyRuleSetValidationReport,
    StrategyRuleSetValidationStatus,
)


def _normalize_registry_key(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("registry_key must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError("registry_key must be non-empty")
    return normalized


class StrategyRuleSetRegistryItem(BaseModel):
    registry_key: str = Field(pattern=r"^[a-z0-9](?:[a-z0-9_.-]*[a-z0-9])?$")
    ruleset: StrategyRuleSet
    validation_report: StrategyRuleSetValidationReport
    enabled_for_runtime: bool = False
    is_actionable: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("registry_key", mode="before")
    @classmethod
    def normalize_key(cls, value: object) -> str:
        return _normalize_registry_key(value)

    @model_validator(mode="after")
    def require_non_actionable_item(self) -> Self:
        if self.enabled_for_runtime:
            raise ValueError("registry items must remain disabled for runtime use")
        if self.is_actionable:
            raise ValueError("registry items must remain non-actionable")
        return self


class StrategyRuleSetRegistrySnapshot(BaseModel):
    created_at: datetime
    items: tuple[StrategyRuleSetRegistryItem, ...] = ()
    item_count: int = Field(ge=0)
    valid_count: int = Field(ge=0)
    invalid_count: int = Field(ge=0)
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)
    is_actionable: bool = False

    model_config = ConfigDict(frozen=True)

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("items")
    @classmethod
    def normalize_items(
        cls,
        value: tuple[StrategyRuleSetRegistryItem, ...],
    ) -> tuple[StrategyRuleSetRegistryItem, ...]:
        return tuple(sorted(value, key=lambda item: item.registry_key))

    @model_validator(mode="after")
    def validate_counts_and_flags(self) -> Self:
        keys = [item.registry_key for item in self.items]
        if len(keys) != len(set(keys)):
            raise ValueError("registry snapshot item keys must be unique")
        valid_count = sum(
            1
            for item in self.items
            if item.validation_report.status == StrategyRuleSetValidationStatus.VALID
        )
        invalid_count = len(self.items) - valid_count
        if self.item_count != len(self.items):
            raise ValueError("item_count must match registry snapshot item length")
        if self.valid_count != valid_count:
            raise ValueError("valid_count must match VALID registry items")
        if self.invalid_count != invalid_count:
            raise ValueError("invalid_count must match non-VALID registry items")
        if self.is_actionable:
            raise ValueError("registry snapshots must remain non-actionable")
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
