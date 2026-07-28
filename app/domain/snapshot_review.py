from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.manual_review import ManualReviewReport
from app.domain.entities.pipeline_decision import PipelineDecisionReport
from app.domain.manual_review_report_builder import ManualReviewReportBuilder
from app.domain.strategy_decision_composer import StrategyDecisionComposer


class SnapshotBackedReview(BaseModel):
    """A read-only review together with the pipeline decision it summarizes.

    The decision is carried alongside so presentation layers can show which rules ran and what
    they measured, instead of only the aggregate counts kept on the review report.
    """

    snapshot: AnalysisSnapshot
    decision: PipelineDecisionReport
    review: ManualReviewReport

    model_config = ConfigDict(frozen=True)


def build_snapshot_backed_review(
    snapshot: AnalysisSnapshot,
    created_at: datetime,
) -> SnapshotBackedReview:
    """Compose a Phase 4G pipeline decision over a real snapshot and wrap it for read-only review.

    This performs no persistence, provider, scheduler, or messaging call. It never builds a tradable
    contract, calculates price levels, or produces an actionable output. The result is read-only and
    non-actionable.
    """
    normalized_created_at = normalize_to_utc(created_at)
    decision_report = StrategyDecisionComposer().compose(snapshot, normalized_created_at)
    review = ManualReviewReportBuilder(decision_report).build_report(normalized_created_at)
    return SnapshotBackedReview(snapshot=snapshot, decision=decision_report, review=review)


def build_snapshot_backed_manual_review_report(
    snapshot: AnalysisSnapshot,
    created_at: datetime,
) -> ManualReviewReport:
    """Return only the review report; kept for callers that do not need the decision detail."""
    return build_snapshot_backed_review(snapshot, created_at).review
