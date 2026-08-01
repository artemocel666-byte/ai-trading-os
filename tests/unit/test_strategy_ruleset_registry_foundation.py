from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.strategy_registry import (
    StrategyRuleSetRegistryItem,
    StrategyRuleSetRegistrySnapshot,
)
from app.domain.entities.strategy_rules import StrategyRuleOperator, StrategyRuleSet
from app.domain.entities.strategy_validation import StrategyRuleSetValidationStatus
from app.domain.strategy_ruleset_registry import (
    BUILTIN_STRATEGY_RULESET_FIXTURES,
    StrategyRuleSetRegistry,
)
from app.domain.strategy_ruleset_validator import StrategyRuleSetValidator

CHECKED_AT = datetime(2026, 7, 18, 10, 0, tzinfo=UTC)
EXPECTED_KEYS = (
    "foundation.data_quality.v1",
    "foundation.event_context.v1",
    "foundation.market_context.v1",
    "foundation.time_filter.v1",
)


def _snapshot(
    registry: StrategyRuleSetRegistry | None = None,
    checked_at: datetime = CHECKED_AT,
) -> StrategyRuleSetRegistrySnapshot:
    return (registry or StrategyRuleSetRegistry()).load_builtin_rulesets(checked_at)


def test_every_builtin_ruleset_validates_as_valid() -> None:
    """Guards the analytical rules against the Phase 4C vocabulary bans.

    A banned token anywhere in a field_ref, description, or warning makes the ruleset INVALID,
    and the Phase 4G composer then silently skips it — so this is the check that keeps the
    rules actually running.
    """
    validator = StrategyRuleSetValidator()

    for key, ruleset in BUILTIN_STRATEGY_RULESET_FIXTURES.items():
        report = validator.validate(ruleset, CHECKED_AT)
        assert report.status == StrategyRuleSetValidationStatus.VALID, (
            f"{key} is {report.status.value}: "
            f"{[(issue.code.value, issue.rule_id) for issue in report.issues]}"
        )


def test_builtin_rulesets_cover_the_expected_analytical_surface() -> None:
    rules_by_key = {
        key: {rule.rule_id for rule in ruleset.rules}
        for key, ruleset in BUILTIN_STRATEGY_RULESET_FIXTURES.items()
    }

    assert rules_by_key["foundation.data_quality.v1"] == {
        "data_quality.used_candle_count",
        "data_quality.completeness_ratio",
        "data_quality.market_data_complete",
        "data_quality.latest_candle_age_minutes",
    }
    assert rules_by_key["foundation.market_context.v1"] == {
        "market_context.snapshot_ready",
        "market_context.volatility_ratio",
        "market_context.max_close_drawdown",
    }
    assert rules_by_key["foundation.event_context.v1"] == {
        "event_context.high_impact_event_count",
        "event_context.minutes_since_latest_event",
    }
    assert rules_by_key["foundation.time_filter.v1"] == {
        "time_filter.session_name_allowed",
        "time_filter.utc_weekday",
    }


def test_no_builtin_rule_uses_the_always_passing_exists_operator() -> None:
    """EXISTS only asks whether a value resolved, so it passed even on an empty database.

    That was the Phase 7C defect: the rules validated the machinery, not the market.
    """
    for ruleset in BUILTIN_STRATEGY_RULESET_FIXTURES.values():
        for rule in ruleset.rules:
            assert rule.condition.operator not in (
                StrategyRuleOperator.EXISTS,
                StrategyRuleOperator.NOT_EXISTS,
            ), f"{rule.rule_id} still uses a presence-only operator"


def test_builtin_rules_remain_disabled_and_non_actionable() -> None:
    for ruleset in BUILTIN_STRATEGY_RULESET_FIXTURES.values():
        assert ruleset.enabled is False
        assert ruleset.is_actionable is False
        for rule in ruleset.rules:
            assert rule.enabled is False
            assert rule.is_actionable is False


def _fixture_with_changed_description() -> dict[str, StrategyRuleSet]:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    base_ruleset = fixtures["foundation.data_quality.v1"]
    changed_rule = base_ruleset.rules[0].model_copy(
        update={"description": "Validate an alternate disabled structural fixture."}
    )
    fixtures["foundation.data_quality.v1"] = base_ruleset.model_copy(
        update={"rules": (changed_rule,)}
    )
    return fixtures


def test_project_phase_is_phase4e_disabled_pipeline_report_shell_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_8b_explanation_provider_foundation"


def test_registry_item_and_snapshot_models_are_immutable() -> None:
    snapshot = _snapshot()
    item = snapshot.items[0]

    with pytest.raises(ValidationError):
        item.registry_key = "changed"
    with pytest.raises(ValidationError):
        snapshot.item_count = 0


def test_registry_snapshot_normalizes_created_at_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    snapshot = _snapshot(checked_at=datetime(2026, 7, 18, 12, 0, tzinfo=offset))

    assert snapshot.created_at == CHECKED_AT
    assert {item.validation_report.checked_at for item in snapshot.items} == {CHECKED_AT}


def test_builtin_registry_keys_are_deterministic() -> None:
    registry = StrategyRuleSetRegistry()

    assert registry.list_keys() == EXPECTED_KEYS
    assert (
        StrategyRuleSetRegistry(
            fixtures=dict(reversed(BUILTIN_STRATEGY_RULESET_FIXTURES.items()))
        ).list_keys()
        == EXPECTED_KEYS
    )


def test_load_builtin_rulesets_returns_deterministic_item_ordering() -> None:
    snapshot = _snapshot()

    assert tuple(item.registry_key for item in snapshot.items) == EXPECTED_KEYS


def test_all_builtin_fixtures_and_rules_are_disabled() -> None:
    snapshot = _snapshot()

    assert all(item.enabled_for_runtime is False for item in snapshot.items)
    assert all(item.ruleset.enabled is False for item in snapshot.items)
    assert all(rule.enabled is False for item in snapshot.items for rule in item.ruleset.rules)


def test_all_builtin_fixtures_validate_valid_through_phase4c_validator() -> None:
    snapshot = _snapshot()

    assert snapshot.item_count == 4
    assert snapshot.valid_count == 4
    assert snapshot.invalid_count == 0
    assert {item.validation_report.status for item in snapshot.items} == {
        StrategyRuleSetValidationStatus.VALID
    }


def test_registry_item_and_snapshot_are_not_actionable() -> None:
    snapshot = _snapshot()

    assert snapshot.is_actionable is False
    assert all(item.is_actionable is False for item in snapshot.items)


def test_get_by_key_returns_expected_item() -> None:
    item = StrategyRuleSetRegistry().get_by_key(
        "foundation.time_filter.v1",
        CHECKED_AT,
    )

    assert item is not None
    assert item.registry_key == "foundation.time_filter.v1"
    assert item.ruleset == BUILTIN_STRATEGY_RULESET_FIXTURES["foundation.time_filter.v1"]
    assert item.validation_report.status == StrategyRuleSetValidationStatus.VALID


def test_get_by_key_unknown_key_returns_none() -> None:
    assert StrategyRuleSetRegistry().get_by_key("unknown.key", CHECKED_AT) is None


def test_registry_snapshot_deterministic_json_round_trips() -> None:
    snapshot = _snapshot()
    same_snapshot = _snapshot()

    assert snapshot.deterministic_json() == same_snapshot.deterministic_json()
    assert (
        StrategyRuleSetRegistrySnapshot.model_validate_json(snapshot.deterministic_json())
        == snapshot
    )


def test_registry_snapshot_fingerprint_is_deterministic_for_same_content() -> None:
    snapshot = _snapshot()
    same_snapshot = _snapshot()

    assert snapshot.fingerprint_sha256() == same_snapshot.fingerprint_sha256()
    assert len(snapshot.fingerprint_sha256()) == 64


def test_registry_snapshot_fingerprint_changes_when_fixture_content_changes() -> None:
    snapshot = _snapshot()
    changed_snapshot = _snapshot(
        StrategyRuleSetRegistry(fixtures=_fixture_with_changed_description())
    )

    assert snapshot.fingerprint_sha256() != changed_snapshot.fingerprint_sha256()


def test_registry_does_not_mutate_rulesets() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    before = {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()}

    StrategyRuleSetRegistry(fixtures=fixtures).load_builtin_rulesets(CHECKED_AT)

    assert {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()} == before


def test_invalid_fixture_still_appears_with_invalid_report() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    invalid_ruleset = fixtures["foundation.data_quality.v1"].model_copy(update={"enabled": True})
    fixtures["foundation.data_quality.v1"] = invalid_ruleset

    snapshot = _snapshot(StrategyRuleSetRegistry(fixtures=fixtures))

    invalid_item = snapshot.items[0]
    assert invalid_item.registry_key == "foundation.data_quality.v1"
    assert invalid_item.validation_report.status == StrategyRuleSetValidationStatus.INVALID
    assert snapshot.invalid_count == 1
    assert snapshot.valid_count == 3


def test_registry_rejects_actionable_models() -> None:
    snapshot = _snapshot()
    item = snapshot.items[0]

    with pytest.raises(ValidationError):
        StrategyRuleSetRegistryItem(
            registry_key=item.registry_key,
            ruleset=item.ruleset,
            validation_report=item.validation_report,
            enabled_for_runtime=True,
        )
    with pytest.raises(ValidationError):
        StrategyRuleSetRegistrySnapshot(
            created_at=snapshot.created_at,
            items=snapshot.items,
            item_count=snapshot.item_count,
            valid_count=snapshot.valid_count,
            invalid_count=snapshot.invalid_count,
            is_actionable=True,
        )


def test_registry_uses_strategy_ruleset_validator_without_market_inputs() -> None:
    class RecordingValidator(StrategyRuleSetValidator):
        def __init__(self) -> None:
            self.seen_rulesets: list[StrategyRuleSet] = []

        def validate(
            self,
            ruleset: StrategyRuleSet,
            checked_at: datetime,
        ):
            self.seen_rulesets.append(ruleset)
            return super().validate(ruleset, checked_at)

    validator = RecordingValidator()
    StrategyRuleSetRegistry(validator=validator).load_builtin_rulesets(CHECKED_AT)

    assert len(validator.seen_rulesets) == len(EXPECTED_KEYS)
    assert all(isinstance(ruleset, StrategyRuleSet) for ruleset in validator.seen_rulesets)
