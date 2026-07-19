import hashlib
import json
from collections import Counter
from collections.abc import Sequence
from datetime import datetime

from pydantic import BaseModel

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.context_engine import MarketContextEngine
from app.domain.entities.analysis import (
    AnalysisInputAudit,
    AnalysisIssue,
    AnalysisIssueCode,
    AnalysisIssueCount,
    AnalysisReadinessStatus,
    AnalysisReport,
    AnalysisSnapshot,
    AnalysisSnapshotMetadata,
    AnalysisWindow,
)
from app.domain.entities.context import ContextIssue, MarketContextSnapshot
from app.domain.entities.data_quality import DataQualityIssue
from app.domain.entities.features import FeatureIssue, MarketFeatureSnapshot
from app.domain.entities.market_data import Candle, EconomicEvent, Timeframe
from app.domain.value_objects import CurrencyPair


class AnalysisEngine:
    def __init__(self, *, context_engine: MarketContextEngine | None = None) -> None:
        self._context_engine = context_engine or MarketContextEngine()

    def build_snapshot(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        candles: Sequence[Candle] = (),
        economic_events: Sequence[EconomicEvent] = (),
        currencies: Sequence[str] | None = None,
        provider: str | None = None,
        feature_snapshot: MarketFeatureSnapshot | None = None,
        context_snapshot: MarketContextSnapshot | None = None,
        moving_average_windows: Sequence[int] = (3, 5),
    ) -> AnalysisSnapshot:
        window = AnalysisWindow(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
        )
        requested_currencies = _requested_currencies(pair=pair, currencies=currencies)
        invalid_window_issue = _invalid_window_issue(window)
        if invalid_window_issue is None and context_snapshot is None:
            context_snapshot = self._context_engine.build_snapshot(
                pair=pair,
                timeframe=timeframe,
                window_start=window.window_start,
                window_end=window.window_end,
                as_of=window.as_of,
                candles=candles,
                economic_events=economic_events,
                moving_average_windows=moving_average_windows,
            )
        if context_snapshot is not None and feature_snapshot is None:
            feature_snapshot = context_snapshot.feature_snapshot

        issues = _analysis_issues(
            window=window,
            invalid_window_issue=invalid_window_issue,
            feature_snapshot=feature_snapshot,
            context_snapshot=context_snapshot,
        )
        input_audit = _input_audit(
            window=window,
            provider=provider,
            requested_currencies=requested_currencies,
            candles=candles,
            economic_events=economic_events,
            feature_snapshot=feature_snapshot,
            context_snapshot=context_snapshot,
            issues=issues,
        )
        readiness_status = _readiness_status(issues=issues, input_audit=input_audit)
        metadata = _metadata(
            window=window,
            input_audit=input_audit,
            issues=issues,
            readiness_status=readiness_status,
            feature_snapshot=feature_snapshot,
            context_snapshot=context_snapshot,
        )
        return AnalysisSnapshot(
            window=window,
            metadata=metadata,
            input_audit=input_audit,
            readiness_status=readiness_status,
            readiness_issues=issues,
            feature_snapshot=feature_snapshot,
            context_snapshot=context_snapshot,
        )

    def build_report(
        self,
        *,
        pair: CurrencyPair,
        timeframe: Timeframe,
        window_start: datetime,
        window_end: datetime,
        as_of: datetime,
        candles: Sequence[Candle] = (),
        economic_events: Sequence[EconomicEvent] = (),
        currencies: Sequence[str] | None = None,
        provider: str | None = None,
        feature_snapshot: MarketFeatureSnapshot | None = None,
        context_snapshot: MarketContextSnapshot | None = None,
        moving_average_windows: Sequence[int] = (3, 5),
    ) -> AnalysisReport:
        snapshot = self.build_snapshot(
            pair=pair,
            timeframe=timeframe,
            window_start=window_start,
            window_end=window_end,
            as_of=as_of,
            candles=candles,
            economic_events=economic_events,
            currencies=currencies,
            provider=provider,
            feature_snapshot=feature_snapshot,
            context_snapshot=context_snapshot,
            moving_average_windows=moving_average_windows,
        )
        return AnalysisReport(
            snapshot=snapshot,
            ready_for_review=snapshot.readiness_status == AnalysisReadinessStatus.READY,
            issue_count=len(snapshot.readiness_issues),
            used_candle_count=snapshot.input_audit.used_candle_count,
            used_event_count=snapshot.input_audit.used_event_count,
            generated_at=snapshot.window.as_of,
        )


def _requested_currencies(
    *,
    pair: CurrencyPair,
    currencies: Sequence[str] | None,
) -> tuple[str, ...]:
    if currencies is None:
        return (pair.base_currency, pair.quote_currency)
    return tuple(sorted(set(currencies)))


def _invalid_window_issue(window: AnalysisWindow) -> AnalysisIssue | None:
    if window.window_end > window.window_start:
        return None
    return AnalysisIssue(
        code=AnalysisIssueCode.INVALID_WINDOW,
        description="Analysis window end must be later than analysis window start.",
        source="analysis",
        timestamp=window.window_start,
    )


def _analysis_issues(
    *,
    window: AnalysisWindow,
    invalid_window_issue: AnalysisIssue | None,
    feature_snapshot: MarketFeatureSnapshot | None,
    context_snapshot: MarketContextSnapshot | None,
) -> tuple[AnalysisIssue, ...]:
    issues: list[AnalysisIssue] = []
    if invalid_window_issue is not None:
        issues.append(invalid_window_issue)
    if feature_snapshot is not None:
        issues.extend(_feature_issues(feature_snapshot.quality_issues))
        issues.extend(_data_quality_issues(feature_snapshot.data_quality_issues))
        issues.extend(_feature_window_issues(window=window, snapshot=feature_snapshot))
    if context_snapshot is not None:
        issues.extend(_context_issues(context_snapshot.context_issues))
        issues.extend(_context_window_issues(window=window, snapshot=context_snapshot))
    return tuple(issues)


def _feature_issues(issues: Sequence[FeatureIssue]) -> tuple[AnalysisIssue, ...]:
    return tuple(
        AnalysisIssue(
            code=_analysis_code(issue.code.name),
            description=issue.description,
            source="feature",
            timestamp=issue.timestamp,
        )
        for issue in issues
    )


def _context_issues(issues: Sequence[ContextIssue]) -> tuple[AnalysisIssue, ...]:
    return tuple(
        AnalysisIssue(
            code=_analysis_code(issue.code.name),
            description=issue.description,
            source="context",
            timestamp=issue.timestamp,
        )
        for issue in issues
    )


def _data_quality_issues(issues: Sequence[DataQualityIssue]) -> tuple[AnalysisIssue, ...]:
    return tuple(
        AnalysisIssue(
            code=_analysis_code(issue.code.name),
            description=issue.description,
            source="data_quality",
            timestamp=issue.timestamp,
        )
        for issue in issues
    )


def _feature_window_issues(
    *,
    window: AnalysisWindow,
    snapshot: MarketFeatureSnapshot,
) -> tuple[AnalysisIssue, ...]:
    if (
        snapshot.window.pair == window.pair
        and snapshot.window.timeframe == window.timeframe
        and snapshot.window.window_start == window.window_start
        and snapshot.window.window_end == window.window_end
        and snapshot.window.as_of == window.as_of
    ):
        return ()
    return (
        AnalysisIssue(
            code=AnalysisIssueCode.SNAPSHOT_WINDOW_MISMATCH,
            description="Feature snapshot window does not match the requested analysis window.",
            source="analysis",
        ),
    )


def _context_window_issues(
    *,
    window: AnalysisWindow,
    snapshot: MarketContextSnapshot,
) -> tuple[AnalysisIssue, ...]:
    if (
        snapshot.window.pair == window.pair
        and snapshot.window.timeframe == window.timeframe
        and snapshot.window.window_start == window.window_start
        and snapshot.window.window_end == window.window_end
        and snapshot.window.as_of == window.as_of
    ):
        return ()
    return (
        AnalysisIssue(
            code=AnalysisIssueCode.SNAPSHOT_WINDOW_MISMATCH,
            description="Context snapshot window does not match the requested analysis window.",
            source="analysis",
        ),
    )


def _input_audit(
    *,
    window: AnalysisWindow,
    provider: str | None,
    requested_currencies: tuple[str, ...],
    candles: Sequence[Candle],
    economic_events: Sequence[EconomicEvent],
    feature_snapshot: MarketFeatureSnapshot | None,
    context_snapshot: MarketContextSnapshot | None,
    issues: Sequence[AnalysisIssue],
) -> AnalysisInputAudit:
    used_candle_count = (
        feature_snapshot.candle_summary.used_candle_count if feature_snapshot is not None else 0
    )
    used_event_count = (
        feature_snapshot.economic_event_summary.used_event_count
        if feature_snapshot is not None
        else 0
    )
    latest_used_candle_close_time = (
        feature_snapshot.candle_summary.latest_candle_close_time
        if feature_snapshot is not None
        else None
    )
    latest_used_event_time = (
        context_snapshot.event_context.latest_event_time if context_snapshot is not None else None
    )
    return AnalysisInputAudit(
        requested_pair=window.pair,
        requested_timeframe=window.timeframe,
        provider=provider,
        requested_currencies=requested_currencies,
        input_candle_count=_input_candle_count(candles, feature_snapshot),
        used_candle_count=used_candle_count,
        input_event_count=_input_event_count(economic_events, feature_snapshot),
        used_event_count=used_event_count,
        input_candles_after_as_of_count=sum(
            1 for candle in candles if candle.close_time > window.as_of
        ),
        input_events_after_as_of_count=sum(
            1 for event in economic_events if event.scheduled_at > window.as_of
        ),
        excluded_issue_counts=_issue_counts(issues),
        as_of=window.as_of,
        latest_used_candle_close_time=latest_used_candle_close_time,
        latest_used_event_time=latest_used_event_time,
        no_candles_after_as_of_used=_not_after(latest_used_candle_close_time, window.as_of),
        no_events_after_as_of_used=_not_after(latest_used_event_time, window.as_of),
    )


def _input_candle_count(
    candles: Sequence[Candle],
    feature_snapshot: MarketFeatureSnapshot | None,
) -> int:
    if candles:
        return len(candles)
    if feature_snapshot is not None:
        return feature_snapshot.candle_summary.input_candle_count
    return 0


def _input_event_count(
    economic_events: Sequence[EconomicEvent],
    feature_snapshot: MarketFeatureSnapshot | None,
) -> int:
    if economic_events:
        return len(economic_events)
    if feature_snapshot is not None:
        return feature_snapshot.economic_event_summary.input_event_count
    return 0


def _issue_counts(issues: Sequence[AnalysisIssue]) -> tuple[AnalysisIssueCount, ...]:
    counts = Counter((issue.source, issue.code) for issue in issues)
    return tuple(
        AnalysisIssueCount(source=source, code=code, count=counts[(source, code)])
        for source, code in sorted(counts, key=lambda item: (item[0], item[1].value))
    )


def _not_after(value: datetime | None, as_of: datetime) -> bool:
    return value is None or normalize_to_utc(value) <= normalize_to_utc(as_of)


def _readiness_status(
    *,
    issues: Sequence[AnalysisIssue],
    input_audit: AnalysisInputAudit,
) -> AnalysisReadinessStatus:
    if _has_blocking_issue(issues) or input_audit.used_candle_count == 0:
        return AnalysisReadinessStatus.BLOCKED
    if issues:
        return AnalysisReadinessStatus.INCOMPLETE
    return AnalysisReadinessStatus.READY


def _has_blocking_issue(issues: Sequence[AnalysisIssue]) -> bool:
    blocking_codes = {
        AnalysisIssueCode.INVALID_WINDOW,
        AnalysisIssueCode.NO_USABLE_CANDLES,
        AnalysisIssueCode.NO_CANDLES,
        AnalysisIssueCode.CANDLE_AFTER_AS_OF,
        AnalysisIssueCode.EVENT_AFTER_AS_OF,
        AnalysisIssueCode.CANDLE_PAIR_MISMATCH,
        AnalysisIssueCode.CANDLE_TIMEFRAME_MISMATCH,
        AnalysisIssueCode.DUPLICATE_CANDLE,
        AnalysisIssueCode.SNAPSHOT_WINDOW_MISMATCH,
    }
    return any(issue.code in blocking_codes for issue in issues)


def _metadata(
    *,
    window: AnalysisWindow,
    input_audit: AnalysisInputAudit,
    issues: Sequence[AnalysisIssue],
    readiness_status: AnalysisReadinessStatus,
    feature_snapshot: MarketFeatureSnapshot | None,
    context_snapshot: MarketContextSnapshot | None,
) -> AnalysisSnapshotMetadata:
    feature_snapshot_id = _model_hash(feature_snapshot)
    context_snapshot_id = _model_hash(context_snapshot)
    snapshot_id = _hash_json(
        {
            "window": window.model_dump(mode="json"),
            "input_audit": input_audit.model_dump(mode="json"),
            "issues": [issue.model_dump(mode="json") for issue in issues],
            "readiness_status": readiness_status.value,
            "feature_snapshot_id": feature_snapshot_id,
            "context_snapshot_id": context_snapshot_id,
        }
    )
    return AnalysisSnapshotMetadata(
        schema_version=constants.ANALYSIS_SNAPSHOT_SCHEMA_VERSION,
        project_phase=constants.PROJECT_PHASE,
        snapshot_id=snapshot_id,
        feature_snapshot_id=feature_snapshot_id,
        context_snapshot_id=context_snapshot_id,
        built_at=window.as_of,
        source_layer="phase_3d_analysis_snapshot_foundation",
    )


def _analysis_code(name: str) -> AnalysisIssueCode:
    if name in AnalysisIssueCode.__members__:
        return AnalysisIssueCode[name]
    return AnalysisIssueCode.DATA_QUALITY_ISSUE


def _model_hash(model: BaseModel | None) -> str | None:
    if model is None:
        return None
    return _hash_json(model.model_dump(mode="json"))


def _hash_json(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
