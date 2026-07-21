import hashlib
from datetime import datetime

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.disabled_pipeline_report_shell import DisabledPipelineReportShell
from app.domain.entities.manual_review import (
    ManualReviewIssue,
    ManualReviewIssueCode,
    ManualReviewIssueSeverity,
    ManualReviewReport,
    ManualReviewSection,
    ManualReviewSectionCode,
    ManualReviewStatus,
    contains_actionable_trading_text,
)
from app.domain.entities.pipeline_decision import PipelineDecisionReport, PipelineDecisionStatus
from app.domain.entities.pipeline_report import DisabledPipelineReport, DisabledPipelineStatus
from app.domain.manual_review_comparison import build_manual_review_quality_summary

MANUAL_REVIEW_REPORT_VERSION = "phase5-manual-review-v1"
_MISSING_SOURCE_FINGERPRINT = hashlib.sha256(b"manual-review:no-source").hexdigest()

ReviewSource = PipelineDecisionReport | DisabledPipelineReport


class ManualReviewReportBuilder:
    def __init__(self, source_report: ReviewSource | None = None) -> None:
        self._source_report = source_report

    def build_report(self, created_at: datetime) -> ManualReviewReport:
        normalized_created_at = normalize_to_utc(created_at)
        source_fingerprint = self._source_fingerprint()
        issues = self._build_issues()
        sections = self._build_sections(source_fingerprint, issues)
        status = _review_status(issues)
        base_report = ManualReviewReport(
            report_version=MANUAL_REVIEW_REPORT_VERSION,
            project_phase=constants.PROJECT_PHASE,
            created_at=normalized_created_at,
            status=status,
            source_fingerprint=source_fingerprint,
            sections=sections,
            issues=issues,
            enabled_for_runtime=False,
            is_actionable=False,
        )
        quality_section = build_manual_review_quality_summary(base_report)
        return ManualReviewReport(
            **base_report.model_dump(exclude={"sections"}),
            sections=(*base_report.sections, quality_section),
        )

    def _source_fingerprint(self) -> str:
        if self._source_report is None:
            return _MISSING_SOURCE_FINGERPRINT
        return self._source_report.fingerprint_sha256()

    def _build_issues(self) -> tuple[ManualReviewIssue, ...]:
        if self._source_report is None:
            return (
                ManualReviewIssue(
                    code=ManualReviewIssueCode.MISSING_AUDIT_EXPORT,
                    message="No existing pipeline report was supplied for manual review.",
                    section_code=ManualReviewSectionCode.AUDIT_EXPORT,
                    severity=ManualReviewIssueSeverity.WARNING,
                ),
                ManualReviewIssue(
                    code=ManualReviewIssueCode.MISSING_SAFETY_CONFIRMATIONS,
                    message="Source safety flags cannot be confirmed without a pipeline report.",
                    section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                    severity=ManualReviewIssueSeverity.WARNING,
                ),
            )

        issues: list[ManualReviewIssue] = []
        source = self._source_report
        if source.fingerprint is not None and source.fingerprint != source.fingerprint_sha256():
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.FINGERPRINT_MISMATCH,
                    message="The supplied source fingerprint does not match the source content.",
                    section_code=ManualReviewSectionCode.AUDIT_EXPORT,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if source.is_actionable:
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.ACTIONABLE_CONTENT_FOUND,
                    message=(
                        "The supplied source is marked actionable and cannot be reviewed safely."
                    ),
                    section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if isinstance(source, DisabledPipelineReport) and source.enabled_for_runtime:
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.RUNTIME_ENABLED_FOUND,
                    message="The supplied source is marked enabled for runtime use.",
                    section_code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if self._unsafe_source_text_found():
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.UNSAFE_TEXT_FOUND,
                    message="Unsafe source text was withheld from the manual review output.",
                    section_code=ManualReviewSectionCode.BLOCKERS,
                    severity=ManualReviewIssueSeverity.BLOCKING,
                )
            )
        if isinstance(source, PipelineDecisionReport) and source.status != (
            PipelineDecisionStatus.READY_FOR_REVIEW
        ):
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.INCOMPLETE_SECTION,
                    message="The Phase 4G source is not ready for complete manual review.",
                    section_code=ManualReviewSectionCode.PIPELINE_STATE,
                    severity=ManualReviewIssueSeverity.WARNING,
                )
            )
        if (
            isinstance(source, DisabledPipelineReport)
            and source.status == DisabledPipelineStatus.BLOCKED
        ):
            issues.append(
                ManualReviewIssue(
                    code=ManualReviewIssueCode.INCOMPLETE_SECTION,
                    message="The disabled pipeline source reports a blocked state.",
                    section_code=ManualReviewSectionCode.PIPELINE_STATE,
                    severity=ManualReviewIssueSeverity.WARNING,
                )
            )
        return tuple(issues)

    def _build_sections(
        self,
        source_fingerprint: str,
        issues: tuple[ManualReviewIssue, ...],
    ) -> tuple[ManualReviewSection, ...]:
        source = self._source_report
        issue_counts = {
            code: sum(1 for issue in issues if issue.section_code == code)
            for code in ManualReviewSectionCode
        }
        source_name = type(source).__name__ if source is not None else "none"
        source_status = source.status.value if source is not None else "MISSING"
        source_phase = self._safe_source_phase()

        sections = [
            ManualReviewSection(
                code=ManualReviewSectionCode.PROJECT_STATE,
                title="Project state",
                summary="Phase 5 manual review is read-only and disabled for runtime action.",
                details=(
                    f"Current project phase: {constants.PROJECT_PHASE}.",
                    f"Source project phase: {source_phase}.",
                    f"Source report type: {source_name}.",
                ),
                issue_count=issue_counts[ManualReviewSectionCode.PROJECT_STATE],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.PIPELINE_STATE,
                title="Pipeline state",
                summary=f"Existing source status: {source_status}.",
                details=self._pipeline_details(),
                issue_count=issue_counts[ManualReviewSectionCode.PIPELINE_STATE],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.REGISTRY_SUMMARY,
                title="Registry summary",
                summary=self._registry_summary(),
                details=self._registry_details(),
                issue_count=issue_counts[ManualReviewSectionCode.REGISTRY_SUMMARY],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.AUDIT_EXPORT,
                title="Audit export",
                summary=(
                    "Source audit metadata is available."
                    if source is not None
                    else "Source audit metadata is unavailable."
                ),
                details=(
                    f"Source fingerprint: {source_fingerprint}.",
                    "Source content was summarized without persistence or external calls.",
                ),
                issue_count=issue_counts[ManualReviewSectionCode.AUDIT_EXPORT],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.SAFETY_CONFIRMATIONS,
                title="Safety confirmations",
                summary="The manual review layer is disabled and non-actionable.",
                details=(
                    "Runtime enabled: false.",
                    "Actionable output: false.",
                    "NO TRADING SIGNAL.",
                    (
                        "No external provider, database, scheduler, or messaging call was made by "
                        "the builder."
                    ),
                ),
                issue_count=issue_counts[ManualReviewSectionCode.SAFETY_CONFIRMATIONS],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.BLOCKERS,
                title="Blockers",
                summary=self._blocker_summary(),
                details=self._blocker_details(),
                issue_count=issue_counts[ManualReviewSectionCode.BLOCKERS],
            ),
            ManualReviewSection(
                code=ManualReviewSectionCode.TELEGRAM_READINESS,
                title="Telegram readiness",
                summary="Manual authorized review delivery is available without automatic alerts.",
                details=(
                    "The review command returns a short read-only summary.",
                    "No scheduled delivery is registered.",
                ),
                issue_count=issue_counts[ManualReviewSectionCode.TELEGRAM_READINESS],
            ),
        ]
        return tuple(sections)

    def _pipeline_details(self) -> tuple[str, ...]:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return (
                f"Reviewed rule-set reports: {source.evaluated_ruleset_count}.",
                f"Blocked rule-set reports: {source.blocked_ruleset_count}.",
                f"Not-ready rule-set reports: {source.not_ready_ruleset_count}.",
                f"Skipped registry items: {len(source.skipped_rulesets)}.",
            )
        if isinstance(source, DisabledPipelineReport):
            return (
                f"Registered items: {source.registry_item_count}.",
                f"Valid items: {source.valid_registry_item_count}.",
                f"Invalid items: {source.invalid_registry_item_count}.",
            )
        return ("No existing pipeline report was supplied.",)

    def _registry_summary(self) -> str:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return "Phase 4G report counts are available for manual inspection."
        if isinstance(source, DisabledPipelineReport):
            return "Phase 4E registry counts are available for manual inspection."
        return "Registry summary is incomplete because no source report was supplied."

    def _registry_details(self) -> tuple[str, ...]:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return (
                f"Reviewed reports: {source.evaluated_ruleset_count}.",
                f"Skipped items: {len(source.skipped_rulesets)}.",
            )
        if isinstance(source, DisabledPipelineReport):
            return (
                f"Total registry items: {source.registry_item_count}.",
                f"Valid registry items: {source.valid_registry_item_count}.",
                f"Invalid registry items: {source.invalid_registry_item_count}.",
                f"Registry snapshot fingerprint: {source.registry_snapshot_fingerprint}.",
            )
        return ("No registry-derived counts are available.",)

    def _blocker_summary(self) -> str:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            blocker_count = source.blocked_ruleset_count + source.not_ready_ruleset_count
            return (
                f"Existing Phase 4G report contains {blocker_count} blocked or incomplete item(s)."
            )
        if isinstance(source, DisabledPipelineReport):
            return f"Existing disabled report contains {len(source.blockers)} blocker(s)."
        return "Source availability blocks a complete review."

    def _blocker_details(self) -> tuple[str, ...]:
        source = self._source_report
        if isinstance(source, PipelineDecisionReport):
            return (
                f"Blocked report count: {source.blocked_ruleset_count}.",
                f"Not-ready report count: {source.not_ready_ruleset_count}.",
            )
        if isinstance(source, DisabledPipelineReport):
            if not source.blockers:
                return ("No source blockers were recorded.",)
            return tuple(
                (
                    f"{blocker.code.value}: Source message withheld by safety validation."
                    if contains_actionable_trading_text(blocker.message)
                    else f"{blocker.code.value}: {blocker.message}"
                )
                for blocker in source.blockers
            )
        return ("MISSING_AUDIT_EXPORT: no source report was supplied.",)

    def _unsafe_source_text_found(self) -> bool:
        source = self._source_report
        if source is None:
            return False
        if contains_actionable_trading_text(source.project_phase):
            return True
        if isinstance(source, DisabledPipelineReport):
            return any(
                contains_actionable_trading_text(blocker.message) for blocker in source.blockers
            )
        return False

    def _safe_source_phase(self) -> str:
        source = self._source_report
        if source is None:
            return "unavailable"
        if contains_actionable_trading_text(source.project_phase):
            return "withheld by safety validation"
        return source.project_phase


def build_local_manual_review_report(created_at: datetime) -> ManualReviewReport:
    normalized_created_at = normalize_to_utc(created_at)
    source_report = DisabledPipelineReportShell().build_report(normalized_created_at)
    return ManualReviewReportBuilder(source_report).build_report(normalized_created_at)


def _review_status(issues: tuple[ManualReviewIssue, ...]) -> ManualReviewStatus:
    if any(issue.severity == ManualReviewIssueSeverity.BLOCKING for issue in issues):
        return ManualReviewStatus.BLOCKED
    if issues:
        return ManualReviewStatus.INCOMPLETE
    return ManualReviewStatus.READ_ONLY
