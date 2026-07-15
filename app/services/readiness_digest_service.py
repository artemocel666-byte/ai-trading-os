from collections.abc import Sequence
from datetime import datetime

from app.core import constants
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)
from app.domain.readiness_engine import SnapshotDigestBuilder, SnapshotReadinessPlanner
from app.services.analysis_service import AnalysisService


class ReadinessDigestService:
    def __init__(
        self,
        analysis_service: AnalysisService,
        *,
        planner: SnapshotReadinessPlanner | None = None,
        digest_builder: SnapshotDigestBuilder | None = None,
    ) -> None:
        self._analysis_service = analysis_service
        self._planner = planner or SnapshotReadinessPlanner()
        self._digest_builder = digest_builder or SnapshotDigestBuilder()

    async def build_digest(
        self,
        *,
        items: Sequence[SnapshotScheduleItem],
        as_of: datetime,
    ) -> SnapshotDigest:
        plan = self._planner.build_plan(items=items, as_of=as_of)
        snapshots = []
        for window in plan.windows:
            snapshots.append(
                await self._analysis_service.build_snapshot(
                    pair=window.pair,
                    timeframe=window.timeframe,
                    window_start=window.window_start,
                    window_end=window.window_end,
                    as_of=window.as_of,
                    currencies=window.currencies or None,
                    provider=window.provider,
                )
            )
        return self._digest_builder.build_digest(
            snapshots=snapshots,
            generated_at=plan.as_of,
            as_of=plan.as_of,
        )

    async def build_payload(
        self,
        *,
        items: Sequence[SnapshotScheduleItem],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        digest = await self.build_digest(items=items, as_of=as_of)
        return SnapshotNotificationPayload(
            project_phase=constants.PROJECT_PHASE,
            dedup_key=digest.dedup_key,
            digest=digest,
            text=readiness_digest_text(digest),
        )


def readiness_digest_text(digest: SnapshotDigest) -> str:
    lines = [
        "Системный отчёт готовности.",
        f"Статус: {digest.readiness_status.value}.",
        "Элементы:",
    ]
    for item in digest.items:
        lines.append(
            f"- {item.pair.value} {item.timeframe.value}: {item.readiness_status.value}, "
            f"свечи {item.used_candle_count}/{item.input_candle_count}, "
            f"проблемы {item.issue_count}"
        )
    lines.append("Решений и указаний нет.")
    return "\n".join(lines)
