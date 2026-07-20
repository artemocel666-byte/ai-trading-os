from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
    StrategyRuleValue,
)

CREATED_AT = datetime(2026, 7, 18, 9, 0, tzinfo=UTC)


def _condition(**overrides: object) -> StrategyRuleCondition:
    values: dict[str, object] = {
        "field_ref": "data_quality.market_data_complete",
        "operator": StrategyRuleOperator.EQ,
        "expected_value": StrategyRuleValue(value=True),
    }
    values.update(overrides)
    return StrategyRuleCondition(**values)


def _rule(rule_id: str = "data_quality.complete", **overrides: object) -> StrategyRuleSpec:
    values: dict[str, object] = {
        "rule_id": rule_id,
        "category": StrategyRuleCategory.DATA_QUALITY,
        "severity": StrategyRuleSeverity.REQUIRED,
        "condition": _condition(),
        "description": "Require a complete deterministic data-quality snapshot.",
        "warnings": ("contract only",),
    }
    values.update(overrides)
    return StrategyRuleSpec(**values)


def _ruleset(**overrides: object) -> StrategyRuleSet:
    values: dict[str, object] = {
        "ruleset_version": "phase4b-ruleset-v1",
        "strategy_version": "future-strategy-spec-v1",
        "name": "Future strategy rule specification",
        "description": "Specification-only rule set for future deterministic checks.",
        "created_at": CREATED_AT,
        "rules": (
            _rule("time.session"),
            _rule("data_quality.complete"),
        ),
    }
    values.update(overrides)
    return StrategyRuleSet(**values)


def test_project_phase_has_advanced_to_phase4e_disabled_pipeline_report_shell_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4g_strategy_decision_composition_foundation"


def test_strategy_rule_models_are_immutable() -> None:
    rule_set = _ruleset()

    with pytest.raises(ValidationError):
        rule_set.enabled = True
    with pytest.raises(ValidationError):
        rule_set.rules[0].condition.field_ref = "changed"


def test_strategy_rule_set_normalizes_created_at_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    rule_set = _ruleset(created_at=datetime(2026, 7, 18, 11, 0, tzinfo=offset))

    assert rule_set.created_at == CREATED_AT


def test_strategy_rule_set_rejects_duplicate_rule_id() -> None:
    with pytest.raises(ValidationError):
        _ruleset(rules=(_rule("duplicate.rule"), _rule("duplicate.rule")))


def test_strategy_rule_identifiers_must_be_non_empty_and_deterministic() -> None:
    with pytest.raises(ValidationError):
        _rule(" ")
    with pytest.raises(ValidationError):
        _rule("bad rule id")
    with pytest.raises(ValidationError):
        _condition(field_ref=" ")
    with pytest.raises(ValidationError):
        _condition(field_ref="market context.value")


def test_strategy_rules_default_to_disabled_and_not_actionable() -> None:
    rule = _rule()
    rule_set = _ruleset(rules=(rule,))

    assert rule.enabled is False
    assert rule_set.enabled is False
    assert rule.is_actionable is False
    assert rule_set.is_actionable is False


def test_between_operator_requires_ordered_bounds() -> None:
    condition = _condition(
        operator=StrategyRuleOperator.BETWEEN,
        expected_value=None,
        lower_bound=StrategyRuleValue(value=Decimal("0.10")),
        upper_bound=StrategyRuleValue(value=Decimal("0.25")),
    )

    assert condition.lower_bound == StrategyRuleValue(value=Decimal("0.10"))

    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.BETWEEN, expected_value=None)
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.BETWEEN,
            expected_value=None,
            lower_bound=StrategyRuleValue(value=Decimal("0.25")),
            upper_bound=StrategyRuleValue(value=Decimal("0.10")),
        )
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.BETWEEN,
            expected_value=StrategyRuleValue(value=Decimal("0.10")),
            lower_bound=StrategyRuleValue(value=Decimal("0.10")),
            upper_bound=StrategyRuleValue(value=Decimal("0.25")),
        )


def test_in_operator_requires_allowed_values_collection() -> None:
    condition = _condition(
        operator=StrategyRuleOperator.IN,
        expected_value=None,
        allowed_values=StrategyRuleValue(value=("LOW", "HIGH", "HIGH")),
    )

    assert condition.allowed_values == StrategyRuleValue(value=("HIGH", "LOW"))

    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.IN, expected_value=None)
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.IN,
            expected_value=None,
            allowed_values=StrategyRuleValue(value="HIGH"),
        )
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.IN,
            expected_value=StrategyRuleValue(value="HIGH"),
            allowed_values=StrategyRuleValue(value=("HIGH", "LOW")),
        )


def test_exists_operators_do_not_accept_comparison_values() -> None:
    assert _condition(operator=StrategyRuleOperator.EXISTS, expected_value=None).operator == (
        StrategyRuleOperator.EXISTS
    )
    assert _condition(operator=StrategyRuleOperator.NOT_EXISTS, expected_value=None).operator == (
        StrategyRuleOperator.NOT_EXISTS
    )

    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.EXISTS)
    with pytest.raises(ValidationError):
        _condition(
            operator=StrategyRuleOperator.NOT_EXISTS,
            expected_value=None,
            allowed_values=StrategyRuleValue(value=("a", "b")),
        )


@pytest.mark.parametrize(
    "operator",
    [
        StrategyRuleOperator.EQ,
        StrategyRuleOperator.NE,
        StrategyRuleOperator.GT,
        StrategyRuleOperator.GTE,
        StrategyRuleOperator.LT,
        StrategyRuleOperator.LTE,
    ],
)
def test_comparison_operators_require_expected_value(operator: StrategyRuleOperator) -> None:
    expected_value = (
        StrategyRuleValue(value=Decimal("1.0"))
        if operator
        in {
            StrategyRuleOperator.GT,
            StrategyRuleOperator.GTE,
            StrategyRuleOperator.LT,
            StrategyRuleOperator.LTE,
        }
        else StrategyRuleValue(value=True)
    )

    assert _condition(operator=operator, expected_value=expected_value).operator == operator

    with pytest.raises(ValidationError):
        _condition(operator=operator, expected_value=None)
    with pytest.raises(ValidationError):
        _condition(
            operator=operator,
            expected_value=StrategyRuleValue(value=("a", "b")),
        )


def test_ordered_comparison_operators_reject_boolean_expected_values() -> None:
    with pytest.raises(ValidationError):
        _condition(operator=StrategyRuleOperator.GT, expected_value=StrategyRuleValue(value=True))


def test_strategy_rule_value_rejects_floats() -> None:
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=1.2)
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=(Decimal("1.0"), 2.0))


def test_strategy_rule_value_decimal_json_round_trips_exactly() -> None:
    value = StrategyRuleValue(value=Decimal("1.20"))
    values = StrategyRuleValue(value=(Decimal("1.20"), Decimal("1.10"), Decimal("1.10")))

    assert StrategyRuleValue.model_validate_json(value.model_dump_json()) == value
    assert StrategyRuleValue.model_validate_json(values.model_dump_json()) == StrategyRuleValue(
        value=(Decimal("1.10"), Decimal("1.20"))
    )


def test_strategy_rule_value_rejects_invalid_collection_values() -> None:
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=())
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=(Decimal("1.0"), "mixed"))
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=(True, False))
    with pytest.raises(ValidationError):
        StrategyRuleValue(value=Decimal("NaN"))


def test_warnings_are_normalized_deterministically() -> None:
    rule = _rule(warnings=("beta", "alpha", "alpha", " "))

    assert rule.warnings == ("alpha", "beta")


def test_rules_are_normalized_deterministically_by_rule_id() -> None:
    rule_set = _ruleset(rules=(_rule("z.rule"), _rule("a.rule")))

    assert tuple(rule.rule_id for rule in rule_set.rules) == ("a.rule", "z.rule")


def test_strategy_rule_set_serializes_deterministically_and_round_trips() -> None:
    rule_set = _ruleset()
    same_rule_set = _ruleset(rules=tuple(reversed(rule_set.rules)))

    assert rule_set.deterministic_json() == same_rule_set.deterministic_json()
    assert StrategyRuleSet.model_validate_json(rule_set.deterministic_json()) == rule_set


def test_strategy_rule_fingerprints_are_deterministic() -> None:
    rule = _rule(warnings=("beta", "alpha"))
    same_rule = _rule(warnings=("alpha", "beta"))
    rule_set = _ruleset()
    same_rule_set = _ruleset(rules=tuple(reversed(rule_set.rules)))

    assert rule.fingerprint_sha256() == same_rule.fingerprint_sha256()
    assert rule_set.fingerprint_sha256() == same_rule_set.fingerprint_sha256()
    assert len(rule_set.fingerprint_sha256()) == 64


def test_strategy_rule_fingerprint_changes_when_key_fields_change() -> None:
    rule_set = _ruleset()
    changed = _ruleset(strategy_version="future-strategy-spec-v2")

    assert rule_set.fingerprint_sha256() != changed.fingerprint_sha256()


def test_strategy_rule_specs_do_not_define_scoring_confidence_or_executable_fields() -> None:
    forbidden_fragments = (
        "score",
        "weight",
        "confidence",
        "action",
        "execution",
        "broker",
        "order",
        "position",
    )
    field_names = set(StrategyRuleSpec.model_fields) | set(StrategyRuleSet.model_fields)
    condition_field_names = set(StrategyRuleCondition.model_fields)
    all_field_names = field_names | condition_field_names

    offenders = [
        field_name
        for field_name in all_field_names
        for fragment in forbidden_fragments
        if fragment in field_name.lower()
    ]

    assert offenders == []
