import hashlib
import json
from collections.abc import Sequence
from datetime import datetime

from app.core import constants
from app.core.time import normalize_to_utc
from app.domain.entities.analysis import AnalysisSnapshot
from app.domain.entities.data_quality import TIMEFRAME_TO_DELTA
from app.domain.entities.market_data import Timeframe
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotDigestIssueCount,
    SnapshotDigestItem,
    SnapshotDigestStatus,
    SnapshotNotificationDedupKey,
    SnapshotScheduleItem,
    SnapshotSchedulePlan,
    SnapshotWindow,
    digest_status_from_analysis,
)


class SnapshotReadinessPlanner:
    def build_plan(
        self,
        *,
        items: Sequence[SnapshotScheduleItem],
        as_of: datetime,
    ) -> SnapshotSchedulePlan:
        if not items:
            raise ValueError("at least one schedule item is required")
        as_of_utc = normalize_to_utc(as_of)
        windows = tuple(
            _window_for_item(item=item, as_of=as_of_utc)
            for item in sorted(items, key=lambda value: (value.pair.value, value.timeframe.value))
        )
        return SnapshotSchedulePlan(
            project_phase=constants.PROJECT_PHASE,
            as_of=as_of_utc,
            windows=windows,
        )


class SnapshotDigestBuilder:
    def build_digest(
        self,
        *,
        snapshots: Sequence[AnalysisSnapshot],
        generated_at: datetime,
        as_of: datetime,
    ) -> SnapshotDigest:
        if not snapshots:
            raise ValueError("at least one snapshot is required")
        generated_at_utc = normalize_to_utc(generated_at)
        as_of_utc = normalize_to_utc(as_of)
        items = tuple(
            _digest_item(snapshot)
            for snapshot in sorted(
                snapshots,
                key=lambda value: (value.window.pair.value, value.window.timeframe.value),
            )
        )
        ready_count = sum(
            1 for item in items if item.readiness_status == SnapshotDigestStatus.READY
        )
        incomplete_count = sum(
            1 for item in items if item.readiness_status == SnapshotDigestStatus.INCOMPLETE
        )
        blocked_count = sum(
            1 for item in items if item.readiness_status == SnapshotDigestStatus.BLOCKED
        )
        readiness_status = _combined_status(items)
        dedup_key = SnapshotNotificationDedupKey(
            value=_hash_payload(
                {
                    "project_phase": constants.PROJECT_PHASE,
                    "as_of": as_of_utc.isoformat(),
                    "items": [item.dedup_key.value for item in items],
                    "status": readiness_status.value,
                }
            )
        )
        return SnapshotDigest(
            project_phase=constants.PROJECT_PHASE,
            generated_at=generated_at_utc,
            as_of=as_of_utc,
            readiness_status=readiness_status,
            items=items,
            ready_count=ready_count,
            incomplete_count=incomplete_count,
            blocked_count=blocked_count,
            dedup_key=dedup_key,
        )


def latest_closed_boundary(*, timeframe: Timeframe, as_of: datetime) -> datetime:
    as_of_utc = normalize_to_utc(as_of)
    if timeframe == Timeframe.M15:
        minute = (as_of_utc.minute // 15) * 15
        return as_of_utc.replace(minute=minute, second=0, microsecond=0)
    if timeframe == Timeframe.H1:
        return as_of_utc.replace(minute=0, second=0, microsecond=0)
    raise ValueError(f"unsupported timeframe: {timeframe.value}")


def _window_for_item(*, item: SnapshotScheduleItem, as_of: datetime) -> SnapshotWindow:
    if item.lookback_candle_count < 1:
        raise ValueError("lookback_candle_count must be at least 1")
    window_end = latest_closed_boundary(timeframe=item.timeframe, as_of=as_of)
    delta = TIMEFRAME_TO_DELTA[item.timeframe]
    window_start = window_end - (item.lookback_candle_count * delta)
    return SnapshotWindow(
        pair=item.pair,
        timeframe=item.timeframe,
        window_start=window_start,
        window_end=window_end,
        as_of=as_of,
        lookback_candle_count=item.lookback_candle_count,
        provider=item.provider,
        currencies=item.currencies,
    )


def _digest_item(snapshot: AnalysisSnapshot) -> SnapshotDigestItem:
    status = digest_status_from_analysis(snapshot.readiness_status)
    audit = snapshot.input_audit
    issue_counts = tuple(
        SnapshotDigestIssueCount(
            source=item.source,
            code=item.code.value,
            count=item.count,
        )
        for item in audit.excluded_issue_counts
    )
    issue_descriptions = tuple(issue.description for issue in snapshot.readiness_issues[:5])
    dedup_key = SnapshotNotificationDedupKey(
        value=_hash_payload(
            {
                "project_phase": constants.PROJECT_PHASE,
                "pair": snapshot.window.pair.value,
                "timeframe": snapshot.window.timeframe.value,
                "window_start": snapshot.window.window_start.isoformat(),
                "window_end": snapshot.window.window_end.isoformat(),
                "as_of": snapshot.window.as_of.isoformat(),
                "snapshot_id": snapshot.metadata.snapshot_id,
                "status": status.value,
            }
        )
    )
    return SnapshotDigestItem(
        pair=snapshot.window.pair,
        timeframe=snapshot.window.timeframe,
        window_start=snapshot.window.window_start,
        window_end=snapshot.window.window_end,
        as_of=snapshot.window.as_of,
        readiness_status=status,
        input_candle_count=audit.input_candle_count,
        used_candle_count=audit.used_candle_count,
        input_event_count=audit.input_event_count,
        used_event_count=audit.used_event_count,
        issue_count=len(snapshot.readiness_issues),
        issue_counts=issue_counts,
        issue_descriptions=issue_descriptions,
        no_candles_after_as_of_used=audit.no_candles_after_as_of_used,
        no_events_after_as_of_used=audit.no_events_after_as_of_used,
        snapshot_id=snapshot.metadata.snapshot_id,
        dedup_key=dedup_key,
    )


def _combined_status(items: Sequence[SnapshotDigestItem]) -> SnapshotDigestStatus:
    if any(item.readiness_status == SnapshotDigestStatus.BLOCKED for item in items):
        return SnapshotDigestStatus.BLOCKED
    if any(item.readiness_status == SnapshotDigestStatus.INCOMPLETE for item in items):
        return SnapshotDigestStatus.INCOMPLETE
    return SnapshotDigestStatus.READY


def _hash_payload(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
