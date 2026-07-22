import json
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities.manual_review import (
    ManualReviewIssue,
    ManualReviewIssueCode,
    ManualReviewIssueSeverity,
    ManualReviewReport,
    ManualReviewSection,
    ManualReviewSectionCode,
    ManualReviewStatus,
)
from app.domain.entities.pipeline_decision import PipelineDecisionReport, PipelineDecisionStatus
from app.domain.entities.pipeline_report import (
    DisabledPipelineBlocker,
    DisabledPipelineBlockerCode,
    DisabledPipelineReport,
    DisabledPipelineStatus,
)
from app.domain.entities.strategy_rules import StrategyRuleSeverity
from app.domain.manual_review_comparison import (
    ManualReviewComparison,
    ManualReviewComparisonStatus,
    build_manual_review_quality_summary,
    compare_manual_review_reports,
)
from app.domain.manual_review_report_builder import ManualReviewReportBuilder

CREATED_AT = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def _disabled_source(
    *,
    fingerprint: str | None = None,
    blocker_message: str = "The source pipeline remains disabled.",
) -> DisabledPipelineReport:
    return DisabledPipelineReport(
        pipeline_version="phase4e-test-v1",
        project_phase="phase_4g_strategy_decision_composition_foundation",
        status=DisabledPipelineStatus.DISABLED,
        created_at=CREATED_AT,
        registry_item_count=1,
        valid_registry_item_count=1,
        invalid_registry_item_count=0,
        blockers=(
            DisabledPipelineBlocker(
                code=DisabledPipelineBlockerCode.PIPELINE_DISABLED,
                message=blocker_message,
                severity=StrategyRuleSeverity.BLOCKING,
            ),
        ),
        registry_snapshot_fingerprint="a" * 64,
        enabled_for_runtime=False,
        is_actionable=False,
        fingerprint=fingerprint,
    )


def _phase4g_source() -> PipelineDecisionReport:
    return PipelineDecisionReport(
        pipeline_version="phase4g-test-v1",
        project_phase="phase_4g_strategy_decision_composition_foundation",
        status=PipelineDecisionStatus.READY_FOR_REVIEW,
        evaluated_at=CREATED_AT,
        source_snapshot_id="b" * 64,
        ruleset_reports=(),
        skipped_rulesets=(),
        evaluated_ruleset_count=0,
        blocked_ruleset_count=0,
        not_ready_ruleset_count=0,
        is_actionable=False,
    )


def _report() -> ManualReviewReport:
    return ManualReviewReportBuilder(_disabled_source()).build_report(CREATED_AT)


def test_phase5_project_state_remains_safe() -> None:
    assert constants.PROJECT_PHASE == "phase_6_snapshot_backed_review_foundation"
    assert constants.STRATEGY_IMPLEMENTED is False
    assert constants.REAL_TRADING_ENABLED is False


def test_manual_review_models_are_immutable_and_normalize_created_at_to_utc() -> None:
    local_created_at = datetime(2026, 7, 20, 14, 0, tzinfo=timezone(timedelta(hours=2)))
    report = ManualReviewReportBuilder(_disabled_source()).build_report(local_created_at)

    assert report.created_at == CREATED_AT
    assert report.created_at.tzinfo == UTC
    with pytest.raises(ValidationError):
        report.status = ManualReviewStatus.BLOCKED
    with pytest.raises(ValidationError):
        report.sections[0].summary = "Changed summary."


def test_duplicate_section_codes_are_rejected() -> None:
    section = ManualReviewSection(
        code=ManualReviewSectionCode.PROJECT_STATE,
        title="Project state",
        summary="Read-only project state.",
    )

    with pytest.raises(ValidationError, match="section codes must be unique"):
        ManualReviewReport(
            report_version="v1",
            project_phase=constants.PROJECT_PHASE,
            created_at=CREATED_AT,
            status=ManualReviewStatus.READ_ONLY,
            source_fingerprint="a" * 64,
            sections=(section, section),
        )


def test_duplicate_issues_are_deduplicated_and_sorted_deterministically() -> None:
    audit_issue = ManualReviewIssue(
        code=ManualReviewIssueCode.MISSING_AUDIT_EXPORT,
        message="Audit metadata is unavailable.",
        section_code=ManualReviewSectionCode.AUDIT_EXPORT,
        severity=ManualReviewIssueSeverity.WARNING,
    )
    safety_issue = ManualReviewIssue(
        code=ManualReviewIssueCode.MISSING_SAFETY_CONFIRMATIONS,
        message="Safety flags are unavailable.",
        section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
        severity=ManualReviewIssueSeverity.WARNING,
    )
    report = ManualReviewReport(
        report_version="v1",
        project_phase=constants.PROJECT_PHASE,
        created_at=CREATED_AT,
        status=ManualReviewStatus.INCOMPLETE,
        source_fingerprint="a" * 64,
        sections=(
            ManualReviewSection(
                code=ManualReviewSectionCode.AUDIT_EXPORT,
                title="Audit export",
                summary="Audit metadata is unavailable.",
                issue_count=1,
            ),
        ),
        issues=(safety_issue, audit_issue, audit_issue),
    )

    assert report.issues == (audit_issue, safety_issue)


@pytest.mark.parametrize("field_name", ["enabled_for_runtime", "is_actionable"])
def test_manual_review_report_rejects_enabled_or_actionable_flags(field_name: str) -> None:
    payload = _report().model_dump()
    payload[field_name] = True

    with pytest.raises(ValidationError):
        ManualReviewReport.model_validate(payload)


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "Buy EURUSD now.",
        "Sell EURUSD now.",
        "Go long now.",
        "Short recommendation.",
        "Trading signal available.",
        "Entry at the latest value.",
        "Set a stop loss.",
        "Set a take profit.",
        "Use this target.",
        "Calculate position size.",
        "Use setup score.",
        "Use confidence score.",
        "Contact a broker.",
        "Place an order.",
        "Execute immediately.",
        "Enable paper trading.",
        "Enable live trading.",
        "Enable real trading.",
    ],
)
def test_manual_review_section_rejects_actionable_text(unsafe_text: str) -> None:
    with pytest.raises(ValidationError, match="actionable trading text"):
        ManualReviewSection(
            code=ManualReviewSectionCode.PIPELINE_STATE,
            title="Pipeline state",
            summary=unsafe_text,
        )


def test_manual_review_section_rejects_actionable_flag() -> None:
    with pytest.raises(ValidationError, match="must remain non-actionable"):
        ManualReviewSection(
            code=ManualReviewSectionCode.PIPELINE_STATE,
            title="Pipeline state",
            summary="Read-only source summary.",
            is_actionable=True,
        )


def test_manual_review_serialization_and_fingerprint_are_stable() -> None:
    first = _report()
    second = _report()

    assert first.deterministic_json() == second.deterministic_json()
    assert first.fingerprint_sha256() == second.fingerprint_sha256()
    assert json.loads(first.deterministic_json())["is_actionable"] is False
    assert tuple(section.code.value for section in first.sections) == tuple(
        sorted(section.code.value for section in first.sections)
    )


def test_manual_review_fingerprint_changes_when_content_changes() -> None:
    first = _report()
    changed_sections = tuple(
        section.model_copy(update={"summary": "Updated read-only project state."})
        if section.code == ManualReviewSectionCode.PROJECT_STATE
        else section
        for section in first.sections
    )
    second = ManualReviewReport(
        **first.model_dump(exclude={"sections", "fingerprint"}),
        sections=changed_sections,
    )

    assert first.fingerprint_sha256() != second.fingerprint_sha256()


def test_text_summary_is_deterministic_and_contains_required_safety_messages() -> None:
    report = _report()

    assert report.render_text_summary() == _report().render_text_summary()
    assert "READ-ONLY MANUAL REVIEW" in report.render_text_summary()
    assert "NO TRADING SIGNAL" in report.render_text_summary()
    assert "NO BUY/SELL RECOMMENDATION" in report.render_text_summary()
    assert "NON-ACTIONABLE" in report.render_text_summary()
    assert "Buy EURUSD" not in report.render_text_summary()
    assert "Sell EURUSD" not in report.render_text_summary()
    assert "go long" not in report.render_text_summary().lower()
    assert "go short" not in report.render_text_summary().lower()


def test_manual_review_report_has_no_trading_output_fields() -> None:
    forbidden_fields = {
        "decision",
        "recommendation",
        "signal",
        "signal_direction",
        "direction",
        "price",
        "entry",
        "entry_price",
        "stop_loss",
        "take_profit",
        "target",
        "position_size",
        "setup_score",
        "confidence",
        "confidence_score",
    }

    assert set(ManualReviewReport.model_fields).isdisjoint(forbidden_fields)
    assert set(ManualReviewSection.model_fields).isdisjoint(forbidden_fields)
    assert set(ManualReviewIssue.model_fields).isdisjoint(forbidden_fields)


def test_builder_consumes_phase4g_report_without_recomputing_pipeline() -> None:
    source = _phase4g_source()
    report = ManualReviewReportBuilder(source).build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.READ_ONLY
    assert report.source_fingerprint == source.fingerprint_sha256()
    assert report.enabled_for_runtime is False
    assert report.is_actionable is False
    assert len(report.sections) == len(ManualReviewSectionCode)
    assert {section.code for section in report.sections} == set(ManualReviewSectionCode)


def test_builder_reports_missing_source_as_incomplete_instead_of_crashing() -> None:
    report = ManualReviewReportBuilder().build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.INCOMPLETE
    assert {issue.code for issue in report.issues} == {
        ManualReviewIssueCode.MISSING_AUDIT_EXPORT,
        ManualReviewIssueCode.MISSING_SAFETY_CONFIRMATIONS,
    }


def test_builder_blocks_a_mismatched_source_fingerprint() -> None:
    report = ManualReviewReportBuilder(_disabled_source(fingerprint="f" * 64)).build_report(
        CREATED_AT
    )

    assert report.status == ManualReviewStatus.BLOCKED
    assert report.issues[0].code == ManualReviewIssueCode.FINGERPRINT_MISMATCH


def test_builder_redacts_unsafe_source_text_and_records_blocking_issue() -> None:
    source = _disabled_source(blocker_message="Buy EURUSD now.")

    report = ManualReviewReportBuilder(source).build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.BLOCKED
    assert ManualReviewIssueCode.UNSAFE_TEXT_FOUND in {issue.code for issue in report.issues}
    assert "Buy EURUSD" not in report.render_text_summary()
    assert "withheld by safety validation" in report.render_text_summary()


@pytest.mark.parametrize("flag_name", ["enabled_for_runtime", "is_actionable"])
def test_builder_blocks_unsafe_source_flags_defensively(flag_name: str) -> None:
    source = _disabled_source().model_copy(update={flag_name: True})

    report = ManualReviewReportBuilder(source).build_report(CREATED_AT)

    assert report.status == ManualReviewStatus.BLOCKED
    assert any(issue.severity == ManualReviewIssueSeverity.BLOCKING for issue in report.issues)


def test_quality_summary_is_deterministic_and_non_actionable() -> None:
    report = _report()
    first = build_manual_review_quality_summary(report)
    second = build_manual_review_quality_summary(report)

    assert first == second
    assert first.code == ManualReviewSectionCode.QUALITY_SUMMARY
    assert first.is_actionable is False


def test_compare_same_report_is_deterministic_and_non_actionable() -> None:
    report = _report()
    first = compare_manual_review_reports(report, report, CREATED_AT)
    second = compare_manual_review_reports(report, report, CREATED_AT)

    assert first.status == ManualReviewComparisonStatus.SAME
    assert first.changed_sections == ()
    assert first.is_actionable is False
    assert first.deterministic_json() == second.deterministic_json()
    assert first.fingerprint_sha256() == second.fingerprint_sha256()


def test_compare_changed_report_identifies_changed_section() -> None:
    left = _report()
    changed_sections = tuple(
        section.model_copy(update={"summary": "Updated read-only project state."})
        if section.code == ManualReviewSectionCode.PROJECT_STATE
        else section
        for section in left.sections
    )
    right = ManualReviewReport(
        **left.model_dump(exclude={"sections", "fingerprint"}),
        sections=changed_sections,
    )

    comparison = compare_manual_review_reports(left, right, CREATED_AT)

    assert comparison.status == ManualReviewComparisonStatus.CHANGED
    assert comparison.changed_sections == (ManualReviewSectionCode.PROJECT_STATE,)


def test_compare_incomplete_report_is_incomplete() -> None:
    incomplete = ManualReviewReportBuilder().build_report(CREATED_AT)

    comparison = compare_manual_review_reports(incomplete, _report(), CREATED_AT)

    assert comparison.status == ManualReviewComparisonStatus.INCOMPLETE


def test_comparison_has_no_trading_output_fields_and_rejects_actionable_flag() -> None:
    forbidden_fields = {
        "decision",
        "recommendation",
        "signal",
        "price",
        "entry",
        "stop_loss",
        "take_profit",
        "position_size",
        "setup_score",
        "confidence_score",
    }
    assert set(ManualReviewComparison.model_fields).isdisjoint(forbidden_fields)

    with pytest.raises(ValidationError, match="must remain non-actionable"):
        ManualReviewComparison(
            created_at=CREATED_AT,
            left_fingerprint="a" * 64,
            right_fingerprint="a" * 64,
            status=ManualReviewComparisonStatus.SAME,
            issue_delta=0,
            is_actionable=True,
        )
