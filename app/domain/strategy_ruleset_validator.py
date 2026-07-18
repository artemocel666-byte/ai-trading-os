from datetime import datetime
from decimal import Decimal

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

ALLOWED_FIELD_PREFIXES: tuple[str, ...] = (
    "data_quality.",
    "market_context.",
    "event_context.",
    "risk_guard.",
    "time_filter.",
    "signal_contract_guard.",
)

CATEGORY_FIELD_PREFIXES: dict[StrategyRuleCategory, str] = {
    StrategyRuleCategory.DATA_QUALITY: "data_quality.",
    StrategyRuleCategory.MARKET_CONTEXT: "market_context.",
    StrategyRuleCategory.EVENT_CONTEXT: "event_context.",
    StrategyRuleCategory.RISK_GUARD: "risk_guard.",
    StrategyRuleCategory.TIME_FILTER: "time_filter.",
    StrategyRuleCategory.SIGNAL_CONTRACT_GUARD: "signal_contract_guard.",
}

FORBIDDEN_EXECUTION_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "execute",
    "order",
    "broker",
    "position_size",
    "open_trade",
    "close_trade",
    "take_trade",
    "entry_signal",
    "telegram_signal",
    "_".join(("place", "order")),
    "paper_trade",
    "live_trade",
    "backtest",
    "simulation",
)
FORBIDDEN_SCORING_TERMS: tuple[str, ...] = ("setup_score",)
FORBIDDEN_CONFIDENCE_TERMS: tuple[str, ...] = ("confidence", "openai", "llm")
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


class StrategyRuleSetValidator:
    def validate(
        self,
        ruleset: StrategyRuleSet,
        checked_at: datetime,
    ) -> StrategyRuleSetValidationReport:
        if not isinstance(ruleset, StrategyRuleSet):
            raise TypeError("StrategyRuleSetValidator validates StrategyRuleSet objects only")

        issues: list[StrategyRuleSetValidationIssue] = []
        if not ruleset.rules:
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.EMPTY_RULESET,
                    message="StrategyRuleSet must contain at least one rule.",
                )
            )
        if ruleset.enabled:
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.RULESET_ENABLED,
                    message="StrategyRuleSet must remain disabled in Phase 4C.",
                )
            )

        seen_rule_ids: set[str] = set()
        for rule in ruleset.rules:
            if rule.rule_id in seen_rule_ids:
                issues.append(
                    self._issue(
                        code=StrategyRuleSetValidationIssueCode.DUPLICATE_RULE_ID,
                        message="Duplicate rule_id detected.",
                        rule=rule,
                    )
                )
            seen_rule_ids.add(rule.rule_id)
            issues.extend(self._validate_rule(rule))

        return StrategyRuleSetValidationReport(
            ruleset_version=ruleset.ruleset_version,
            strategy_version=ruleset.strategy_version,
            ruleset_name=ruleset.name,
            status=self._status_for(issues),
            checked_at=checked_at,
            issues=tuple(issues),
            rule_count=len(ruleset.rules),
            enabled_rule_count=sum(1 for rule in ruleset.rules if rule.enabled),
        )

    def _validate_rule(self, rule: StrategyRuleSpec) -> tuple[StrategyRuleSetValidationIssue, ...]:
        issues: list[StrategyRuleSetValidationIssue] = []
        if rule.enabled:
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.RULE_ENABLED,
                    message="StrategyRuleSpec must remain disabled in Phase 4C.",
                    rule=rule,
                )
            )
        if not rule.condition.field_ref.startswith(ALLOWED_FIELD_PREFIXES):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.UNKNOWN_FIELD_REF,
                    message="Rule field_ref is not in the static validation registry.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        expected_prefix = CATEGORY_FIELD_PREFIXES[rule.category]
        if not rule.condition.field_ref.startswith(expected_prefix):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.CATEGORY_FIELD_MISMATCH,
                    message="Rule category does not match the field_ref prefix.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        issues.extend(self._scan_forbidden_language(rule))
        issues.extend(self._validate_condition_operands(rule))
        return tuple(issues)

    def _scan_forbidden_language(
        self,
        rule: StrategyRuleSpec,
    ) -> tuple[StrategyRuleSetValidationIssue, ...]:
        text = " ".join((rule.condition.field_ref, rule.description, *rule.warnings))
        lowered = text.lower()
        issues: list[StrategyRuleSetValidationIssue] = []
        if any(term in lowered for term in FORBIDDEN_EXECUTION_TERMS):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_EXECUTION_LANGUAGE,
                    message="Rule specification contains forbidden execution language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        if any(term in lowered for term in FORBIDDEN_SCORING_TERMS):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_SCORING_LANGUAGE,
                    message="Rule specification contains forbidden scoring language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        if any(term in lowered for term in FORBIDDEN_CONFIDENCE_TERMS):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_CONFIDENCE_LANGUAGE,
                    message="Rule specification contains forbidden confidence or AI language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        if self._field_ref_contains_forbidden_token(rule.condition.field_ref):
            issues.append(
                self._issue(
                    code=StrategyRuleSetValidationIssueCode.FORBIDDEN_FIELD_REF,
                    message="Rule field_ref contains forbidden action-oriented language.",
                    rule=rule,
                    field_ref=rule.condition.field_ref,
                )
            )
        return tuple(issues)

    def _validate_condition_operands(
        self,
        rule: StrategyRuleSpec,
    ) -> tuple[StrategyRuleSetValidationIssue, ...]:
        condition = rule.condition
        if condition.operator in _EXISTS_OPERATORS and self._has_any_operand(condition):
            return (self._invalid_operands_issue(rule),)
        if condition.operator in _COMPARISON_OPERATORS:
            if (
                condition.expected_value is None
                or not condition.expected_value.is_scalar
                or self._has_range_or_allowed_values(condition)
            ):
                return (self._invalid_operands_issue(rule),)
            if condition.operator in _ORDERED_COMPARISON_OPERATORS and isinstance(
                condition.expected_value.value, bool
            ):
                return (self._invalid_operands_issue(rule),)
        if (
            condition.operator == StrategyRuleOperator.BETWEEN
            and self._has_invalid_between_operands(condition)
        ):
            return (self._invalid_operands_issue(rule),)
        if condition.operator == StrategyRuleOperator.IN and self._has_invalid_in_operands(
            condition
        ):
            return (self._invalid_operands_issue(rule),)
        return ()

    @staticmethod
    def _has_any_operand(condition: StrategyRuleCondition) -> bool:
        return any(
            value is not None
            for value in (
                condition.expected_value,
                condition.lower_bound,
                condition.upper_bound,
                condition.allowed_values,
            )
        )

    @staticmethod
    def _has_range_or_allowed_values(condition: StrategyRuleCondition) -> bool:
        return any(
            value is not None
            for value in (condition.lower_bound, condition.upper_bound, condition.allowed_values)
        )

    def _has_invalid_between_operands(self, condition: StrategyRuleCondition) -> bool:
        lower_bound = condition.lower_bound
        upper_bound = condition.upper_bound
        if (
            lower_bound is None
            or upper_bound is None
            or condition.expected_value is not None
            or condition.allowed_values is not None
        ):
            return True
        return self._invalid_between_bounds(lower_bound, upper_bound)

    @staticmethod
    def _has_invalid_in_operands(condition: StrategyRuleCondition) -> bool:
        return (
            condition.allowed_values is None
            or not condition.allowed_values.is_collection
            or condition.expected_value is not None
            or condition.lower_bound is not None
            or condition.upper_bound is not None
        )

    @staticmethod
    def _invalid_between_bounds(
        lower_bound: StrategyRuleValue,
        upper_bound: StrategyRuleValue,
    ) -> bool:
        lower = lower_bound.value
        upper = upper_bound.value
        if not lower_bound.is_scalar or not upper_bound.is_scalar:
            return True
        if isinstance(lower, bool) or isinstance(upper, bool):
            return True
        if isinstance(lower, Decimal) and isinstance(upper, Decimal):
            return lower > upper
        if isinstance(lower, str) and isinstance(upper, str):
            return lower > upper
        return True

    @staticmethod
    def _field_ref_contains_forbidden_token(field_ref: str) -> bool:
        tokens = field_ref.lower().replace("-", "_").replace(".", "_").split("_")
        return any(token in {"buy", "sell", "order", "broker", "execute"} for token in tokens)

    @staticmethod
    def _status_for(
        issues: list[StrategyRuleSetValidationIssue],
    ) -> StrategyRuleSetValidationStatus:
        if not issues:
            return StrategyRuleSetValidationStatus.VALID
        if all(issue.severity == StrategyRuleSeverity.WARNING for issue in issues):
            return StrategyRuleSetValidationStatus.WARNING
        return StrategyRuleSetValidationStatus.INVALID

    def _invalid_operands_issue(self, rule: StrategyRuleSpec) -> StrategyRuleSetValidationIssue:
        return self._issue(
            code=StrategyRuleSetValidationIssueCode.INVALID_OPERATOR_OPERANDS,
            message="Rule operator operands are structurally invalid.",
            rule=rule,
            field_ref=rule.condition.field_ref,
        )

    @staticmethod
    def _issue(
        *,
        code: StrategyRuleSetValidationIssueCode,
        message: str,
        rule: StrategyRuleSpec | None = None,
        field_ref: str | None = None,
    ) -> StrategyRuleSetValidationIssue:
        return StrategyRuleSetValidationIssue(
            code=code,
            message=message,
            rule_id=rule.rule_id if rule is not None else None,
            field_ref=field_ref,
            severity=StrategyRuleSeverity.BLOCKING,
        )
