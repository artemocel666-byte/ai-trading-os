import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from app.core.time import normalize_to_utc


class StrategyRuleOperator(StrEnum):
    EXISTS = "EXISTS"
    NOT_EXISTS = "NOT_EXISTS"
    EQ = "EQ"
    NE = "NE"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"
    BETWEEN = "BETWEEN"
    IN = "IN"


class StrategyRuleCategory(StrEnum):
    DATA_QUALITY = "DATA_QUALITY"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    EVENT_CONTEXT = "EVENT_CONTEXT"
    RISK_GUARD = "RISK_GUARD"
    TIME_FILTER = "TIME_FILTER"
    SIGNAL_CONTRACT_GUARD = "SIGNAL_CONTRACT_GUARD"


class StrategyRuleSeverity(StrEnum):
    REQUIRED = "REQUIRED"
    WARNING = "WARNING"
    BLOCKING = "BLOCKING"


_EXISTS_OPERATORS = {StrategyRuleOperator.EXISTS, StrategyRuleOperator.NOT_EXISTS}
_COMPARISON_OPERATORS = {
    StrategyRuleOperator.EQ,
    StrategyRuleOperator.NE,
    StrategyRuleOperator.GT,
    StrategyRuleOperator.GTE,
    StrategyRuleOperator.LT,
    StrategyRuleOperator.LTE,
}
_ORDERED_COMPARISON_OPERATORS = {
    StrategyRuleOperator.GT,
    StrategyRuleOperator.GTE,
    StrategyRuleOperator.LT,
    StrategyRuleOperator.LTE,
}


def _normalize_identifier(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be non-empty")
    return normalized


def _normalize_string_collection(value: object, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raw_items: tuple[object, ...] = (value,)
    elif isinstance(value, list | tuple):
        raw_items = tuple(value)
    else:
        raise ValueError(f"{field_name} must be a string, list, or tuple")
    return tuple(sorted({str(item).strip() for item in raw_items if str(item).strip()}))


def _normalize_decimal_value(value: object) -> Decimal:
    if isinstance(value, float):
        raise ValueError("strategy rule values must use Decimal-compatible inputs, not float")
    if isinstance(value, bool):
        raise ValueError("strategy rule Decimal values must not be boolean")
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("strategy rule Decimal value must be finite")
        return value
    if isinstance(value, int | str):
        try:
            normalized = Decimal(value)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("strategy rule Decimal value is invalid") from exc
        if not normalized.is_finite():
            raise ValueError("strategy rule Decimal value must be finite")
        return normalized
    raise ValueError("unsupported strategy rule Decimal value type")


def _normalize_serialized_rule_value(
    value: dict[str, object],
) -> str | bool | Decimal | tuple[str, ...] | tuple[Decimal, ...]:
    value_type = value.get("type")
    raw_value = value.get("value")
    if value_type == "string":
        if not isinstance(raw_value, str):
            raise ValueError("serialized string rule value must contain a string")
        return _normalize_scalar_value(raw_value)
    if value_type == "bool":
        if not isinstance(raw_value, bool):
            raise ValueError("serialized bool rule value must contain a boolean")
        return raw_value
    if value_type == "decimal":
        return _normalize_decimal_value(raw_value)
    if value_type == "string_list":
        if not isinstance(raw_value, list):
            raise ValueError("serialized string_list rule value must contain a list")
        normalized = _normalize_collection_value(tuple(raw_value))
        if not all(isinstance(item, str) for item in normalized):
            raise ValueError("serialized string_list rule value must contain strings")
        return normalized
    if value_type == "decimal_list":
        if not isinstance(raw_value, list):
            raise ValueError("serialized decimal_list rule value must contain a list")
        normalized = tuple(sorted({_normalize_decimal_value(item) for item in raw_value}))
        if not normalized:
            raise ValueError("serialized decimal_list rule value must be non-empty")
        return normalized
    raise ValueError("serialized rule value type is unsupported")


def _normalize_scalar_value(value: object) -> str | bool | Decimal:
    if isinstance(value, float):
        raise ValueError("strategy rule values must use Decimal-compatible inputs, not float")
    if isinstance(value, bool):
        return value
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("strategy rule Decimal value must be finite")
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            raise ValueError("strategy rule string values must be non-empty")
        return normalized
    raise ValueError("unsupported strategy rule value type")


def _normalize_collection_value(
    value: list[object] | tuple[object, ...],
) -> tuple[str, ...] | tuple[Decimal, ...]:
    if not value:
        raise ValueError("strategy rule collection values must be non-empty")
    normalized_items = tuple(_normalize_scalar_value(item) for item in value)
    string_values = [item for item in normalized_items if isinstance(item, str)]
    if len(string_values) == len(normalized_items):
        return tuple(sorted(set(string_values)))
    decimal_values = [item for item in normalized_items if isinstance(item, Decimal)]
    if len(decimal_values) == len(normalized_items):
        return tuple(sorted(set(decimal_values)))
    raise ValueError("strategy rule collection values must be all strings or all Decimals")


def _normalize_rule_value(
    value: object,
) -> str | bool | Decimal | tuple[str, ...] | tuple[Decimal, ...]:
    if isinstance(value, dict):
        return _normalize_serialized_rule_value(value)
    if isinstance(value, list | tuple):
        return _normalize_collection_value(value)
    return _normalize_scalar_value(value)


class StrategyRuleValue(BaseModel):
    value: Any

    model_config = ConfigDict(frozen=True)

    @field_validator("value", mode="before")
    @classmethod
    def normalize_value(cls, value: object) -> object:
        return _normalize_rule_value(value)

    @property
    def is_collection(self) -> bool:
        return isinstance(self.value, tuple)

    @property
    def is_scalar(self) -> bool:
        return not self.is_collection

    def deterministic_json(self) -> str:
        return json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    @field_serializer("value")
    def serialize_value(self, value: object) -> dict[str, object]:
        if isinstance(value, bool):
            return {"type": "bool", "value": value}
        if isinstance(value, Decimal):
            return {"type": "decimal", "value": str(value)}
        if isinstance(value, str):
            return {"type": "string", "value": value}
        if isinstance(value, tuple) and all(isinstance(item, Decimal) for item in value):
            return {"type": "decimal_list", "value": [str(item) for item in value]}
        if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
            return {"type": "string_list", "value": list(value)}
        raise TypeError("unsupported normalized strategy rule value type")


class StrategyRuleCondition(BaseModel):
    field_ref: str = Field(pattern=r"^[A-Za-z0-9_.:-]+$")
    operator: StrategyRuleOperator
    expected_value: StrategyRuleValue | None = None
    lower_bound: StrategyRuleValue | None = None
    upper_bound: StrategyRuleValue | None = None
    allowed_values: StrategyRuleValue | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("field_ref", mode="before")
    @classmethod
    def normalize_field_ref(cls, value: object) -> str:
        return _normalize_identifier(value, "field_ref")

    @model_validator(mode="after")
    def validate_operator_values(self) -> Self:
        if self.operator in _EXISTS_OPERATORS:
            self._reject_operands_for_exists()
        elif self.operator in _COMPARISON_OPERATORS:
            self._validate_comparison_operator()
        elif self.operator == StrategyRuleOperator.BETWEEN:
            self._validate_between_operator()
        elif self.operator == StrategyRuleOperator.IN:
            self._validate_in_operator()
        return self

    def _reject_operands_for_exists(self) -> None:
        if any(
            value is not None
            for value in (
                self.expected_value,
                self.lower_bound,
                self.upper_bound,
                self.allowed_values,
            )
        ):
            raise ValueError("EXISTS and NOT_EXISTS rules must not define comparison values")

    def _validate_comparison_operator(self) -> None:
        if self.expected_value is None:
            raise ValueError(f"{self.operator} requires expected_value")
        if not self.expected_value.is_scalar:
            raise ValueError(f"{self.operator} expected_value must be scalar")
        if self.operator in _ORDERED_COMPARISON_OPERATORS and isinstance(
            self.expected_value.value, bool
        ):
            raise ValueError(f"{self.operator} expected_value must be ordered")
        if any(
            value is not None for value in (self.lower_bound, self.upper_bound, self.allowed_values)
        ):
            raise ValueError(f"{self.operator} must not define range or allowed values")

    def _validate_between_operator(self) -> None:
        if self.lower_bound is None or self.upper_bound is None:
            raise ValueError("BETWEEN requires lower_bound and upper_bound")
        if self.expected_value is not None or self.allowed_values is not None:
            raise ValueError("BETWEEN must not define expected_value or allowed_values")
        lower = self._ordered_scalar(self.lower_bound, "lower_bound")
        upper = self._ordered_scalar(self.upper_bound, "upper_bound")
        if self._lower_exceeds_upper(lower, upper):
            raise ValueError("BETWEEN lower_bound must be less than or equal to upper_bound")

    def _validate_in_operator(self) -> None:
        if self.allowed_values is None:
            raise ValueError("IN requires allowed_values")
        if not self.allowed_values.is_collection:
            raise ValueError("IN allowed_values must be a collection")
        if any(
            value is not None for value in (self.expected_value, self.lower_bound, self.upper_bound)
        ):
            raise ValueError("IN must not define expected_value or range values")

    @staticmethod
    def _ordered_scalar(value: StrategyRuleValue, field_name: str) -> str | Decimal:
        if not value.is_scalar or isinstance(value.value, bool):
            raise ValueError(f"{field_name} must be an ordered scalar")
        if not isinstance(value.value, str | Decimal):
            raise ValueError(f"{field_name} must be a string or Decimal")
        return value.value

    @staticmethod
    def _lower_exceeds_upper(lower: str | Decimal, upper: str | Decimal) -> bool:
        if isinstance(lower, Decimal):
            if not isinstance(upper, Decimal):
                raise ValueError("BETWEEN lower_bound and upper_bound must use the same value type")
            return lower > upper
        if not isinstance(upper, str):
            raise ValueError("BETWEEN lower_bound and upper_bound must use the same value type")
        return lower > upper


class StrategyRuleSpec(BaseModel):
    rule_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]+$")
    category: StrategyRuleCategory
    severity: StrategyRuleSeverity
    condition: StrategyRuleCondition
    description: str = Field(min_length=1, max_length=1000)
    enabled: bool = False
    warnings: tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True)

    @field_validator("rule_id", mode="before")
    @classmethod
    def normalize_rule_id(cls, value: object) -> str:
        return _normalize_identifier(value, "rule_id")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str:
        return _normalize_identifier(value, "description")

    @field_validator("warnings", mode="before")
    @classmethod
    def normalize_warnings(cls, value: object) -> tuple[str, ...]:
        return _normalize_string_collection(value, "warnings")

    @property
    def is_actionable(self) -> bool:
        return False

    def canonical_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def deterministic_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def fingerprint_sha256(self) -> str:
        return hashlib.sha256(self.deterministic_json().encode("utf-8")).hexdigest()


class StrategyRuleSet(BaseModel):
    ruleset_version: str = Field(min_length=1)
    strategy_version: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    created_at: datetime
    rules: tuple[StrategyRuleSpec, ...] = Field(min_length=1)
    enabled: bool = False
    fingerprint: str | None = Field(default=None, min_length=64, max_length=64)

    model_config = ConfigDict(frozen=True)

    @field_validator("ruleset_version", "strategy_version", "name", mode="before")
    @classmethod
    def normalize_required_strings(cls, value: object) -> str:
        return _normalize_identifier(value, "strategy rule set string")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_optional_description(cls, value: object) -> str | None:
        if value is None:
            return None
        return _normalize_identifier(value, "description")

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_utc(cls, value: datetime) -> datetime:
        return normalize_to_utc(value)

    @field_validator("rules")
    @classmethod
    def normalize_rules(cls, value: tuple[StrategyRuleSpec, ...]) -> tuple[StrategyRuleSpec, ...]:
        return tuple(sorted(value, key=lambda rule: rule.rule_id))

    @model_validator(mode="after")
    def rule_ids_must_be_unique(self) -> Self:
        rule_ids = [rule.rule_id for rule in self.rules]
        if len(rule_ids) != len(set(rule_ids)):
            raise ValueError("StrategyRuleSet rule_id values must be unique")
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
