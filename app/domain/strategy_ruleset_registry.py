from collections.abc import Mapping
from datetime import UTC, datetime
from types import MappingProxyType

from app.core.constants import DEFAULT_STRATEGY_VERSION
from app.core.time import normalize_to_utc
from app.domain.entities.strategy_registry import (
    StrategyRuleSetRegistryItem,
    StrategyRuleSetRegistrySnapshot,
)
from app.domain.entities.strategy_rules import (
    StrategyRuleCategory,
    StrategyRuleCondition,
    StrategyRuleOperator,
    StrategyRuleSet,
    StrategyRuleSeverity,
    StrategyRuleSpec,
    StrategyRuleValue,
)
from app.domain.entities.strategy_validation import StrategyRuleSetValidationStatus
from app.domain.strategy_ruleset_validator import StrategyRuleSetValidator

BUILTIN_RULESET_CREATED_AT = datetime(2026, 7, 18, 0, 0, tzinfo=UTC)


def _foundation_rule(
    *,
    rule_id: str,
    category: StrategyRuleCategory,
    severity: StrategyRuleSeverity,
    field_ref: str,
    operator: StrategyRuleOperator,
    description: str,
    allowed_values: tuple[str, ...] | None = None,
) -> StrategyRuleSpec:
    return StrategyRuleSpec(
        rule_id=rule_id,
        category=category,
        severity=severity,
        condition=StrategyRuleCondition(
            field_ref=field_ref,
            operator=operator,
            allowed_values=(
                StrategyRuleValue(value=allowed_values) if allowed_values is not None else None
            ),
        ),
        description=description,
        enabled=False,
    )


BUILTIN_STRATEGY_RULESET_FIXTURES: Mapping[str, StrategyRuleSet] = MappingProxyType(
    {
        "foundation.data_quality.minimum": StrategyRuleSet(
            ruleset_version="foundation-data-quality-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation data-quality minimum",
            description="Disabled structural fixture for data-quality references.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="data_quality.closed_candles_available",
                    category=StrategyRuleCategory.DATA_QUALITY,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="data_quality.closed_candles_available",
                    operator=StrategyRuleOperator.EXISTS,
                    description=(
                        "Validate that closed-candle availability can be referenced by a "
                        "disabled rule specification."
                    ),
                ),
            ),
            enabled=False,
        ),
        "foundation.market_context.minimum": StrategyRuleSet(
            ruleset_version="foundation-market-context-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation market-context minimum",
            description="Disabled structural fixture for market-context references.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="market_context.snapshot_ready",
                    category=StrategyRuleCategory.MARKET_CONTEXT,
                    severity=StrategyRuleSeverity.REQUIRED,
                    field_ref="market_context.snapshot_ready",
                    operator=StrategyRuleOperator.EXISTS,
                    description=(
                        "Validate that market-context readiness can be referenced by a "
                        "disabled rule specification."
                    ),
                ),
            ),
            enabled=False,
        ),
        "foundation.time_filter.session": StrategyRuleSet(
            ruleset_version="foundation-time-filter-v1",
            strategy_version=DEFAULT_STRATEGY_VERSION,
            name="Foundation time-filter session",
            description="Disabled structural fixture for session label references.",
            created_at=BUILTIN_RULESET_CREATED_AT,
            rules=(
                _foundation_rule(
                    rule_id="time_filter.session_name_allowed",
                    category=StrategyRuleCategory.TIME_FILTER,
                    severity=StrategyRuleSeverity.WARNING,
                    field_ref="time_filter.session_name",
                    operator=StrategyRuleOperator.IN,
                    allowed_values=("london", "new_york"),
                    description=(
                        "Validate that allowed session labels can be referenced by a "
                        "disabled rule specification."
                    ),
                ),
            ),
            enabled=False,
        ),
    }
)


class StrategyRuleSetRegistry:
    def __init__(
        self,
        fixtures: Mapping[str, StrategyRuleSet] | None = None,
        validator: StrategyRuleSetValidator | None = None,
    ) -> None:
        fixture_source = fixtures if fixtures is not None else BUILTIN_STRATEGY_RULESET_FIXTURES
        self._fixtures = MappingProxyType(dict(fixture_source))
        self._validator = validator or StrategyRuleSetValidator()

    def list_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._fixtures))

    def get_by_key(
        self,
        key: str,
        checked_at: datetime,
    ) -> StrategyRuleSetRegistryItem | None:
        ruleset = self._fixtures.get(key.strip())
        if ruleset is None:
            return None
        return self._build_item(key.strip(), ruleset, checked_at)

    def load_builtin_rulesets(self, checked_at: datetime) -> StrategyRuleSetRegistrySnapshot:
        normalized_checked_at = normalize_to_utc(checked_at)
        items = tuple(
            self._build_item(key, self._fixtures[key], normalized_checked_at)
            for key in self.list_keys()
        )
        valid_count = sum(
            1
            for item in items
            if item.validation_report.status == StrategyRuleSetValidationStatus.VALID
        )
        return StrategyRuleSetRegistrySnapshot(
            created_at=normalized_checked_at,
            items=items,
            item_count=len(items),
            valid_count=valid_count,
            invalid_count=len(items) - valid_count,
        )

    def _build_item(
        self,
        key: str,
        ruleset: StrategyRuleSet,
        checked_at: datetime,
    ) -> StrategyRuleSetRegistryItem:
        validation_report = self._validator.validate(ruleset, checked_at)
        return StrategyRuleSetRegistryItem(
            registry_key=key,
            ruleset=ruleset,
            validation_report=validation_report,
            enabled_for_runtime=False,
        )
