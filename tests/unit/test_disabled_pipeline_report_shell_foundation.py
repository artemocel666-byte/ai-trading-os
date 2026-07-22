from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.disabled_pipeline_report_shell import DisabledPipelineReportShell
from app.domain.entities.pipeline_report import (
    DisabledPipelineBlocker,
    DisabledPipelineBlockerCode,
    DisabledPipelineReport,
    DisabledPipelineStatus,
)
from app.domain.entities.strategy_registry import (
    StrategyRuleSetRegistryItem,
    StrategyRuleSetRegistrySnapshot,
)
from app.domain.entities.strategy_rules import StrategyRuleSet, StrategyRuleSeverity
from app.domain.strategy_ruleset_registry import (
    BUILTIN_STRATEGY_RULESET_FIXTURES,
    StrategyRuleSetRegistry,
)

CREATED_AT = datetime(2026, 7, 18, 11, 0, tzinfo=UTC)


class StaticSnapshotRegistry(StrategyRuleSetRegistry):
    def __init__(self, snapshot: StrategyRuleSetRegistrySnapshot) -> None:
        self.snapshot = snapshot

    def load_builtin_rulesets(self, _checked_at: datetime) -> StrategyRuleSetRegistrySnapshot:
        return self.snapshot


def _report(
    shell: DisabledPipelineReportShell | None = None,
    created_at: datetime = CREATED_AT,
) -> DisabledPipelineReport:
    return (shell or DisabledPipelineReportShell()).build_report(created_at)


def _blocker_codes(report: DisabledPipelineReport) -> tuple[DisabledPipelineBlockerCode, ...]:
    return tuple(blocker.code for blocker in report.blockers)


def _fixture_with_changed_description() -> dict[str, StrategyRuleSet]:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    base_ruleset = fixtures["foundation.data_quality.minimum"]
    changed_rule = base_ruleset.rules[0].model_copy(
        update={"description": "Validate a changed disabled report-shell fixture."}
    )
    fixtures["foundation.data_quality.minimum"] = base_ruleset.model_copy(
        update={"rules": (changed_rule,)}
    )
    return fixtures


def _snapshot_from_registry(
    registry: StrategyRuleSetRegistry | None = None,
) -> StrategyRuleSetRegistrySnapshot:
    return (registry or StrategyRuleSetRegistry()).load_builtin_rulesets(CREATED_AT)


def test_project_phase_is_phase4e_disabled_pipeline_report_shell_foundation() -> None:
    assert constants.PROJECT_PHASE == "phase_6_snapshot_backed_review_foundation"


def test_blocker_and_report_models_are_immutable() -> None:
    report = _report()

    with pytest.raises(ValidationError):
        report.status = DisabledPipelineStatus.READY_FOR_REVIEW
    with pytest.raises(ValidationError):
        report.blockers[0].message = "changed"


def test_report_normalizes_created_at_to_utc() -> None:
    offset = timezone(timedelta(hours=2))
    report = _report(created_at=datetime(2026, 7, 18, 13, 0, tzinfo=offset))

    assert report.created_at == CREATED_AT


def test_default_shell_is_disabled_and_contains_disabled_blocker() -> None:
    report = _report()

    assert report.status == DisabledPipelineStatus.DISABLED
    assert DisabledPipelineBlockerCode.PIPELINE_DISABLED in _blocker_codes(report)
    assert report.enabled_for_runtime is False
    assert report.is_actionable is False


def test_enabled_shell_request_still_blocks_runtime_behavior() -> None:
    report = _report(DisabledPipelineReportShell(enabled=True))

    assert report.status == DisabledPipelineStatus.BLOCKED
    assert DisabledPipelineBlockerCode.RUNTIME_NOT_ALLOWED in _blocker_codes(report)
    assert DisabledPipelineBlockerCode.PIPELINE_DISABLED not in _blocker_codes(report)
    assert report.enabled_for_runtime is False
    assert report.is_actionable is False


def test_report_includes_registry_counts_and_snapshot_fingerprint() -> None:
    registry = StrategyRuleSetRegistry()
    snapshot = _snapshot_from_registry(registry)
    report = _report(DisabledPipelineReportShell(registry=registry))

    assert report.registry_item_count == snapshot.item_count
    assert report.valid_registry_item_count == snapshot.valid_count
    assert report.invalid_registry_item_count == snapshot.invalid_count
    assert report.registry_snapshot_fingerprint == snapshot.fingerprint_sha256()


def test_empty_registry_snapshot_adds_empty_blocker() -> None:
    empty_snapshot = StrategyRuleSetRegistrySnapshot(
        created_at=CREATED_AT,
        items=(),
        item_count=0,
        valid_count=0,
        invalid_count=0,
    )
    report = _report(DisabledPipelineReportShell(registry=StaticSnapshotRegistry(empty_snapshot)))

    assert DisabledPipelineBlockerCode.REGISTRY_EMPTY in _blocker_codes(report)


def test_invalid_registry_snapshot_adds_invalid_blocker() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    fixtures["foundation.data_quality.minimum"] = fixtures[
        "foundation.data_quality.minimum"
    ].model_copy(update={"enabled": True})
    snapshot = _snapshot_from_registry(StrategyRuleSetRegistry(fixtures=fixtures))

    report = _report(DisabledPipelineReportShell(registry=StaticSnapshotRegistry(snapshot)))

    assert DisabledPipelineBlockerCode.REGISTRY_INVALID in _blocker_codes(report)
    assert any(
        blocker.registry_key == "foundation.data_quality.minimum"
        for blocker in report.blockers
        if blocker.code == DisabledPipelineBlockerCode.REGISTRY_INVALID
    )


def test_actionable_registry_item_adds_actionable_blocker() -> None:
    snapshot = _snapshot_from_registry()
    item = snapshot.items[0]
    actionable_item = StrategyRuleSetRegistryItem.model_construct(
        registry_key=item.registry_key,
        ruleset=item.ruleset,
        validation_report=item.validation_report,
        enabled_for_runtime=True,
        is_actionable=False,
    )
    unsafe_snapshot = StrategyRuleSetRegistrySnapshot.model_construct(
        created_at=snapshot.created_at,
        items=(actionable_item, *snapshot.items[1:]),
        item_count=snapshot.item_count,
        valid_count=snapshot.valid_count,
        invalid_count=snapshot.invalid_count,
        fingerprint=snapshot.fingerprint,
        is_actionable=False,
    )

    report = _report(DisabledPipelineReportShell(registry=StaticSnapshotRegistry(unsafe_snapshot)))

    assert DisabledPipelineBlockerCode.ACTIONABLE_ITEM_FOUND in _blocker_codes(report)
    assert any(
        blocker.registry_key == item.registry_key
        for blocker in report.blockers
        if blocker.code == DisabledPipelineBlockerCode.ACTIONABLE_ITEM_FOUND
    )


def test_report_deterministic_json_round_trips() -> None:
    report = _report()
    same_report = _report()

    assert report.deterministic_json() == same_report.deterministic_json()
    assert DisabledPipelineReport.model_validate_json(report.deterministic_json()) == report


def test_report_fingerprint_is_deterministic_for_same_content() -> None:
    report = _report()
    same_report = _report()

    assert report.fingerprint_sha256() == same_report.fingerprint_sha256()
    assert len(report.fingerprint_sha256()) == 64


def test_report_fingerprint_changes_when_registry_snapshot_content_changes() -> None:
    report = _report()
    changed_registry = StrategyRuleSetRegistry(fixtures=_fixture_with_changed_description())
    changed_report = _report(DisabledPipelineReportShell(registry=changed_registry))

    assert report.fingerprint_sha256() != changed_report.fingerprint_sha256()


def test_blocker_ordering_is_deterministic() -> None:
    blockers = (
        DisabledPipelineBlocker(
            code=DisabledPipelineBlockerCode.RUNTIME_NOT_ALLOWED,
            message="b",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
        DisabledPipelineBlocker(
            code=DisabledPipelineBlockerCode.REGISTRY_EMPTY,
            message="a",
            severity=StrategyRuleSeverity.BLOCKING,
        ),
    )
    report = DisabledPipelineReport(
        pipeline_version="phase4e-test",
        project_phase=constants.PROJECT_PHASE,
        status=DisabledPipelineStatus.BLOCKED,
        created_at=CREATED_AT,
        registry_item_count=0,
        valid_registry_item_count=0,
        invalid_registry_item_count=0,
        blockers=blockers,
        registry_snapshot_fingerprint="a" * 64,
    )

    assert _blocker_codes(report) == (
        DisabledPipelineBlockerCode.REGISTRY_EMPTY,
        DisabledPipelineBlockerCode.RUNTIME_NOT_ALLOWED,
    )


def test_shell_does_not_mutate_registry_fixtures() -> None:
    fixtures = dict(BUILTIN_STRATEGY_RULESET_FIXTURES)
    before = {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()}

    DisabledPipelineReportShell(registry=StrategyRuleSetRegistry(fixtures=fixtures)).build_report(
        CREATED_AT
    )

    assert {key: ruleset.deterministic_json() for key, ruleset in fixtures.items()} == before


def test_shell_does_not_mutate_registry_snapshot() -> None:
    snapshot = _snapshot_from_registry()
    before = snapshot.deterministic_json()

    DisabledPipelineReportShell(registry=StaticSnapshotRegistry(snapshot)).build_report(CREATED_AT)

    assert snapshot.deterministic_json() == before


def test_report_model_has_no_decision_signal_price_or_scoring_fields() -> None:
    fields = set(DisabledPipelineReport.model_fields)

    assert fields.isdisjoint(
        {
            "decision",
            "recommendation",
            "signal_direction",
            "direction",
            "entry",
            "entry_price",
            "stop_loss",
            "take_profit",
            "target",
            "position_size",
            "setup_score",
            "confidence",
            "confidence_score",
            "broker",
            "paper_trade",
            "live_trade",
        }
    )


def test_report_rejects_runtime_enabled_or_actionable_flags() -> None:
    report = _report()
    enabled_values = report.model_dump()
    enabled_values["enabled_for_runtime"] = True
    actionable_values = report.model_dump()
    actionable_values["is_actionable"] = True

    with pytest.raises(ValidationError):
        DisabledPipelineReport(**enabled_values)
    with pytest.raises(ValidationError):
        DisabledPipelineReport(**actionable_values)
