from collections.abc import Sequence
from datetime import datetime

from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.rule_evaluation import (
    RuleEvaluationResult,
    RuleEvaluationStatus,
    RuleSetEvaluationReport,
    RuleSetEvaluationStatus,
)
from app.domain.entities.strategy_rules import (
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
)
from app.domain.strategy_field_resolver import FieldResolution, resolve_field

_EXISTS_OPERATORS = {StrategyRuleOperator.EXISTS, StrategyRuleOperator.NOT_EXISTS}
_ORDERED_OPERATORS = {
    StrategyRuleOperator.GT,
    StrategyRuleOperator.GTE,
    StrategyRuleOperator.LT,
    StrategyRuleOperator.LTE,
}


def evaluate_condition(condition: StrategyRuleCondition, resolved: FieldResolution) -> bool:
    if condition.operator == StrategyRuleOperator.EXISTS:
        return resolved is not None
    if condition.operator == StrategyRuleOperator.NOT_EXISTS:
        return resolved is None
    if resolved is None:
        return False
    if condition.expected_value is None and condition.operator in {
        StrategyRuleOperator.EQ,
        StrategyRuleOperator.NE,
        *_ORDERED_OPERATORS,
    }:
        return False
    if condition.operator == StrategyRuleOperator.EQ:
        return bool(resolved == condition.expected_value.value)  # type: ignore[union-attr]
    if condition.operator == StrategyRuleOperator.NE:
        return bool(resolved != condition.expected_value.value)  # type: ignore[union-attr]
    if condition.operator in _ORDERED_OPERATORS:
        return _evaluate_ordered(condition, resolved)
    if condition.operator == StrategyRuleOperator.BETWEEN:
        return _evaluate_between(condition, resolved)
    if condition.operator == StrategyRuleOperator.IN:
        return _evaluate_in(condition, resolved)
    raise ValueError(f"unsupported strategy rule operator: {condition.operator}")


def _evaluate_ordered(condition: StrategyRuleCondition, resolved: FieldResolution) -> bool:
    assert condition.expected_value is not None
    expected = condition.expected_value.value
    try:
        if condition.operator == StrategyRuleOperator.GT:
            return bool(resolved > expected)
        if condition.operator == StrategyRuleOperator.GTE:
            return bool(resolved >= expected)
        if condition.operator == StrategyRuleOperator.LT:
            return bool(resolved < expected)
        return bool(resolved <= expected)
    except TypeError:
        return False


def _evaluate_between(condition: StrategyRuleCondition, resolved: FieldResolution) -> bool:
    if condition.lower_bound is None or condition.upper_bound is None:
        return False
    lower = condition.lower_bound.value
    upper = condition.upper_bound.value
    try:
        return bool(lower <= resolved <= upper)
    except TypeError:
        return False


def _evaluate_in(condition: StrategyRuleCondition, resolved: FieldResolution) -> bool:
    if condition.allowed_values is None:
        return False
    return resolved in condition.allowed_values.value


class StrategyRuleEvaluator:
    def evaluate_rule(
        self,
        rule: StrategyRuleSpec,
        snapshot: AnalysisSnapshot,
    ) -> RuleEvaluationResult:
        resolved = resolve_field(rule.condition.field_ref, snapshot)
        if resolved is None and rule.condition.operator not in _EXISTS_OPERATORS:
            return RuleEvaluationResult(
                rule_id=rule.rule_id,
                category=rule.category,
                severity=rule.severity,
                field_ref=rule.condition.field_ref,
                status=RuleEvaluationStatus.UNAVAILABLE,
                resolved_value_present=False,
            )
        passed = evaluate_condition(rule.condition, resolved)
        return RuleEvaluationResult(
            rule_id=rule.rule_id,
            category=rule.category,
            severity=rule.severity,
            field_ref=rule.condition.field_ref,
            status=RuleEvaluationStatus.PASSED if passed else RuleEvaluationStatus.FAILED,
            resolved_value_present=True,
        )

    def evaluate_ruleset(
        self,
        ruleset: StrategyRuleSet,
        snapshot: AnalysisSnapshot,
        evaluated_at: datetime,
    ) -> RuleSetEvaluationReport:
        results = tuple(self.evaluate_rule(rule, snapshot) for rule in ruleset.rules)
        blocking_failure_count = _failure_count(results, StrategyRuleSeverity.BLOCKING)
        required_failure_count = _failure_count(results, StrategyRuleSeverity.REQUIRED)
        # Warnings count only what was *observed* to be wrong. For the two mandatory tiers an
        # unresolvable field is disqualifying — you must not proceed on an unchecked mandatory
        # condition, so `_failure_count` treats UNAVAILABLE as failure and that is fail-closed.
        # A warning is different: it exists to colour a verdict when something is seen to be off,
        # and "we could not check" is silence rather than a finding. Counting it would make the
        # warning permanent — `event_context.minutes_since_latest_event` is unavailable in 99.6% of
        # windows because the calendar is empty, so every window in the project would be warned and
        # the distinction would carry no information at all.
        warning_failure_count = _observed_failure_count(results, StrategyRuleSeverity.WARNING)
        unavailable_count = sum(
            1 for result in results if result.status == RuleEvaluationStatus.UNAVAILABLE
        )
        return RuleSetEvaluationReport(
            ruleset_version=ruleset.ruleset_version,
            strategy_version=ruleset.strategy_version,
            ruleset_name=ruleset.name,
            status=_status_for(
                blocking_failure_count, required_failure_count, warning_failure_count
            ),
            evaluated_at=normalize_to_utc(evaluated_at),
            source_snapshot_id=snapshot.metadata.snapshot_id,
            results=results,
            blocking_failure_count=blocking_failure_count,
            required_failure_count=required_failure_count,
            warning_failure_count=warning_failure_count,
            unavailable_count=unavailable_count,
            is_actionable=False,
        )


def _failure_count(
    results: Sequence[RuleEvaluationResult],
    severity: StrategyRuleSeverity,
) -> int:
    """Anything that did not pass, including a field that could not be resolved.

    Fail-closed, and used for the two mandatory tiers: a mandatory condition nobody could check has
    not been satisfied.
    """
    return sum(
        1
        for result in results
        if result.severity == severity and result.status != RuleEvaluationStatus.PASSED
    )


def _observed_failure_count(
    results: Sequence[RuleEvaluationResult],
    severity: StrategyRuleSeverity,
) -> int:
    """Only what was checked and found wanting. Unavailable fields are silence, not findings."""
    return sum(
        1
        for result in results
        if result.severity == severity and result.status == RuleEvaluationStatus.FAILED
    )


def _status_for(
    blocking_failure_count: int,
    required_failure_count: int,
    warning_failure_count: int,
) -> RuleSetEvaluationStatus:
    """Worst severity that failed decides the status.

    `warning_failure_count` was previously computed by the caller and never passed here, so warnings
    could not affect anything. That is why a weekend window came out READY_FOR_REVIEW while the rule
    saying the market was shut sat failed in the same report.
    """
    if blocking_failure_count > 0:
        return RuleSetEvaluationStatus.BLOCKED
    if required_failure_count > 0:
        return RuleSetEvaluationStatus.NOT_READY
    if warning_failure_count > 0:
        return RuleSetEvaluationStatus.READY_WITH_WARNINGS
    return RuleSetEvaluationStatus.READY_FOR_REVIEW
