from datetime import datetime

from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.manual_review import ManualReviewReport
from app.domain.manual_review_report_builder import ManualReviewReportBuilder
from app.domain.strategy_decision_composer import StrategyDecisionComposer


def build_snapshot_backed_manual_review_report(
    snapshot: AnalysisSnapshot,
    created_at: datetime,
) -> ManualReviewReport:
    """Compose a Phase 4G pipeline decision over a real snapshot and wrap it for read-only review.

    This performs no persistence, provider, scheduler, or messaging call. It never builds a tradable
    contract, calculates price levels, or produces an actionable output. The resulting
    ManualReviewReport is read-only and non-actionable.
    """
    normalized_created_at = normalize_to_utc(created_at)
    decision_report = StrategyDecisionComposer().compose(snapshot, normalized_created_at)
    return ManualReviewReportBuilder(decision_report).build_report(normalized_created_at)
