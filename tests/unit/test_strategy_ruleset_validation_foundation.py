from datetime import UTC, datetime, timedelta, timezone

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
from app.domain.entities.strategy_validation import (
    StrategyRuleSetValidationIssue,
    StrategyRuleSetValidationIssueCode,
    StrategyRuleSetValidationReport,
    StrategyRuleSetValidationStatus,
)
from app.domain.strategy_ruleset_validator import StrategyRuleSetValidator

CREATED_AT = datetime(2026, 7, 18, 9, 0, tzinfo=UTC)
CHECKED_AT = datetime(2026, 7, 18, 10, 0, tzinfo=UTC)


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
        "description": "Require deterministic data-quality structure.",
    }
    values.update(overrides)
    return StrategyRuleSpec(**values)


def _ruleset(**overrides: object) -> StrategyRuleSet:
    values: dict[str, object] = {
        "ruleset_version": "phase4c-ruleset-v1",
        "strategy_version": "future-strategy-validation-v1",
        "name": "Future strategy ruleset validation",
        "description": "Validation-only ruleset.",
        "created_at": CREATED_AT,
        "rules": (
            _rule("data_quality.complete"),
            _rule(
                "time_filter.session_exists",
                category=StrategyRuleCategory.TIME_FILTER,
                condition=_condition(
                    field_ref="time_filter.session",
                    operator=StrategyRuleOperator.EXISTS,
                    expected_value=None,
                ),
            ),
        ),
    }
    values.update(overrides)
    return StrategyRuleSet(**values)


def _validate(ruleset: StrategyRuleSet) -> StrategyRuleSetValidationReport:
    return StrategyRuleSetValidator().validate(ruleset, CHECKED_AT)


def _codes(
    report: StrategyRuleSetValidationReport,
) -> tuple[StrategyRuleSetValidationIssueCode, ...]:
    return tuple(issue.code for issue in report.issues)


def test_project_phase_is_phase4d_strategy_ruleset_registry_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_4d_strategy_ruleset_registry_foundation"


def test_validation_issue_and_report_models_are_immutable() -> None:
    report = _validate(_ruleset())

    with pytest.raises(ValidationError):
        report.status = StrategyRuleSetValidationStatus.INVALID
    with pytest.raises(ValidationError):
        StrategyRuleSetValidationIssue(
            code=StrategyRuleSetValidationIssueCode.RULE_ENABLED,
            message="message",
            severity=StrategyRuleSeverity.BLOCKING,
        ).message = "changed"


def test_validation_report_normalizes_checked_at_to_utc() -> None:
    checked_at = datetime(2026, 7, 18, 12, 0, tzinfo=timezone(timedelta(hours=2)))
    report = StrategyRuleSetValidator().validate(_ruleset(), checked_at)

    assert report.checked_at == CHECKED_AT


def test_clean_disabled_ruleset_validates_as_valid() -> None:
    report = _validate(_ruleset())

    assert report.status == StrategyRuleSetValidationStatus.VALID
    assert report.issues == ()
    assert report.rule_count == 2
    assert report.enabled_rule_count == 0


def test_enabled_ruleset_validates_as_invalid() -> None:
    report = _validate(_ruleset(enabled=True))

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.RULESET_ENABLED in _codes(report)


def test_enabled_rule_validates_as_invalid() -> None:
    report = _validate(_ruleset(rules=(_rule(enabled=True),)))

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert report.enabled_rule_count == 1
    assert StrategyRuleSetValidationIssueCode.RULE_ENABLED in _codes(report)


def test_unknown_field_ref_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(
            rules=(
                _rule(
                    condition=_condition(field_ref="unknown_context.value"),
                ),
            )
        )
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.UNKNOWN_FIELD_REF in _codes(report)


def test_category_field_ref_mismatch_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(
            rules=(
                _rule(
                    category=StrategyRuleCategory.DATA_QUALITY,
                    condition=_condition(field_ref="market_context.regime"),
                ),
            )
        )
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH in _codes(report)


def test_forbidden_execution_language_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(rules=(_rule(description="Never buy or sell from a rule specification."),))
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_EXECUTION_LANGUAGE in _codes(report)


def test_forbidden_scoring_language_validates_as_invalid() -> None:
    report = _validate(_ruleset(rules=(_rule(warnings=("setup_score is not allowed here",)),)))

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_SCORING_LANGUAGE in _codes(report)


def test_forbidden_confidence_language_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(rules=(_rule(description="confidence and OpenAI language are forbidden."),))
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_CONFIDENCE_LANGUAGE in _codes(report)


def test_forbidden_field_ref_validates_as_invalid() -> None:
    report = _validate(
        _ruleset(
            rules=(
                _rule(
                    category=StrategyRuleCategory.RISK_GUARD,
                    condition=_condition(field_ref="risk_guard.broker_state"),
                ),
            )
        )
    )

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.FORBIDDEN_FIELD_REF in _codes(report)


def test_invalid_operator_operands_validate_as_invalid_when_constructed_unsafely() -> None:
    unsafe_condition = StrategyRuleCondition.model_construct(
        field_ref="data_quality.market_data_complete",
        operator=StrategyRuleOperator.EXISTS,
        expected_value=StrategyRuleValue(value=True),
        lower_bound=None,
        upper_bound=None,
        allowed_values=None,
    )
    unsafe_rule = StrategyRuleSpec.model_construct(
        rule_id="unsafe.operands",
        category=StrategyRuleCategory.DATA_QUALITY,
        severity=StrategyRuleSeverity.REQUIRED,
        condition=unsafe_condition,
        description="Unsafe constructed rule.",
        enabled=False,
        warnings=(),
    )
    unsafe_ruleset = StrategyRuleSet.model_construct(
        ruleset_version="phase4c-ruleset-v1",
        strategy_version="future-strategy-validation-v1",
        name="Unsafe constructed ruleset",
        description=None,
        created_at=CREATED_AT,
        rules=(unsafe_rule,),
        enabled=False,
        fingerprint=None,
    )

    report = _validate(unsafe_ruleset)

    assert report.status == StrategyRuleSetValidationStatus.INVALID
    assert StrategyRuleSetValidationIssueCode.INVALID_OPERATOR_OPERANDS in _codes(report)


def test_empty_ruleset_and_duplicate_rule_ids_remain_model_level_rejections() -> None:
    with pytest.raises(ValidationError):
        _ruleset(rules=())
    with pytest.raises(ValidationError):
        _ruleset(rules=(_rule("duplicate.rule"), _rule("duplicate.rule")))


def test_validation_report_is_not_actionable() -> None:
    assert _validate(_ruleset()).is_actionable is False


def test_validation_report_serializes_deterministically_and_round_trips() -> None:
    report = _validate(_ruleset())
    same_report = _validate(_ruleset(rules=tuple(reversed(_ruleset().rules))))

    assert report.deterministic_json() == same_report.deterministic_json()
    assert (
        StrategyRuleSetValidationReport.model_validate_json(report.deterministic_json()) == report
    )


def test_validation_report_fingerprint_is_deterministic() -> None:
    report = _validate(_ruleset())
    same_report = _validate(_ruleset(rules=tuple(reversed(_ruleset().rules))))

    assert report.fingerprint_sha256() == same_report.fingerprint_sha256()
    assert len(report.fingerprint_sha256()) == 64


def test_validation_report_fingerprint_changes_when_issue_content_changes() -> None:
    report = _validate(_ruleset(rules=(_rule(description="buy is forbidden"),)))
    changed = _validate(_ruleset(rules=(_rule(warnings=("setup_score is forbidden",)),)))

    assert report.fingerprint_sha256() != changed.fingerprint_sha256()


def test_validation_issue_ordering_is_deterministic() -> None:
    issues = (
        StrategyRuleSetValidationIssue(
            code=StrategyRuleSetValidationIssueCode.RULE_ENABLED,
            message="b",
            rule_id="b.rule",
            field_ref="data_quality.b",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
        StrategyRuleSetValidationIssue(
            code=StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH,
            message="a",
            rule_id="a.rule",
            field_ref="market_context.a",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
    )
    report = StrategyRuleSetValidationReport(
        ruleset_version="phase4c-ruleset-v1",
        strategy_version="future-strategy-validation-v1",
        ruleset_name="Ordered report",
        status=StrategyRuleSetValidationStatus.INVALID,
        checked_at=CHECKED_AT,
        issues=issues,
        rule_count=2,
        enabled_rule_count=1,
    )

    assert _codes(report) == (
        StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH,
        StrategyRuleSetValidationIssueCode.RULE_ENABLED,
    )


def test_validator_does_not_mutate_input_ruleset() -> None:
    ruleset = _ruleset()
    before = ruleset.deterministic_json()

    _validate(ruleset)

    assert ruleset.deterministic_json() == before


def test_validator_accepts_only_strategy_ruleset_objects() -> None:
    with pytest.raises(TypeError):
        StrategyRuleSetValidator().validate(object(), CHECKED_AT)  # type: ignore[arg-type]
