from datetime import datetime
from typing import Protocol

from app.core.time import normalize_to_utc
from app.domain.entities.readiness import (
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecision,
    ScheduledDigestDecisionReason,
    ScheduledDigestDeliveryRecord,
    ScheduledDigestDeliveryResult,
    ScheduledDigestTick,
)
from app.domain.interfaces.notifications import NotificationSender, ScheduledDigestDeliveryStore


class ReadinessDigestPayloadBuilder(Protocol):
    async def build_payload(
        self,
        *,
        items: tuple[SnapshotScheduleItem, ...],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        """Build a neutral readiness digest payload for scheduled delivery."""


class InMemoryScheduledDigestDeliveryStore:
    def __init__(self) -> None:
        self._records: dict[str, ScheduledDigestDeliveryRecord] = {}

    async def exists(self, dedup_key: SnapshotNotificationDedupKey) -> bool:
        return dedup_key.value in self._records

    async def record(self, record: ScheduledDigestDeliveryRecord) -> None:
        self._records[record.dedup_key.value] = record


class ScheduledDigestDeliveryService:
    def __init__(
        self,
        *,
        config: ScheduledDigestConfig,
        readiness_digest_service: ReadinessDigestPayloadBuilder,
        sender: NotificationSender,
        delivery_store: ScheduledDigestDeliveryStore,
        sender_name: str = "notification_sender",
    ) -> None:
        self._config = config
        self._readiness_digest_service = readiness_digest_service
        self._sender = sender
        self._delivery_store = delivery_store
        self._sender_name = sender_name

    async def run_tick(self, *, as_of: datetime) -> ScheduledDigestDeliveryResult:
        tick = ScheduledDigestTick(as_of=as_of)
        base_decision = self._decide(tick)
        if not base_decision.should_build:
            return _skipped_result(tick=tick, decision=base_decision)

        try:
            payload = await self._readiness_digest_service.build_payload(
                items=self._config.items,
                as_of=tick.as_of,
            )
        except Exception:
            return _skipped_result(
                tick=tick,
                decision=_decision(
                    config=self._config,
                    tick=tick,
                    reason=ScheduledDigestDecisionReason.BUILD_FAILED,
                    is_due=True,
                    should_build=False,
                ),
            )

        if await self._delivery_store.exists(payload.dedup_key):
            return _skipped_result(
                tick=tick,
                decision=_decision(
                    config=self._config,
                    tick=tick,
                    reason=ScheduledDigestDecisionReason.DUPLICATE,
                    is_due=True,
                    should_build=False,
                    dedup_key=payload.dedup_key,
                ),
                dedup_key=payload.dedup_key,
                payload=payload,
            )

        await self._sender.send(payload)
        record = ScheduledDigestDeliveryRecord(
            dedup_key=payload.dedup_key,
            delivered_at=tick.as_of,
            sender_name=self._sender_name,
        )
        await self._delivery_store.record(record)
        return ScheduledDigestDeliveryResult(
            tick=tick,
            decision=_decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.DELIVERED,
                is_due=True,
                should_build=True,
                dedup_key=payload.dedup_key,
            ),
            delivered=True,
            skipped=False,
            dedup_key=payload.dedup_key,
            payload=payload,
            record=record,
        )

    def _decide(self, tick: ScheduledDigestTick) -> ScheduledDigestDecision:
        if not self._config.enabled:
            return _decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.DISABLED,
                is_due=False,
                should_build=False,
            )
        if not self._config.items:
            return _decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.NO_ITEMS,
                is_due=False,
                should_build=False,
            )
        is_due = is_scheduled_digest_due(
            as_of=tick.as_of,
            interval_minutes=self._config.interval_minutes,
        )
        if not is_due:
            return _decision(
                config=self._config,
                tick=tick,
                reason=ScheduledDigestDecisionReason.NOT_DUE,
                is_due=False,
                should_build=False,
            )
        return _decision(
            config=self._config,
            tick=tick,
            reason=ScheduledDigestDecisionReason.DUE,
            is_due=True,
            should_build=True,
        )


def is_scheduled_digest_due(*, as_of: datetime, interval_minutes: int) -> bool:
    if interval_minutes < 1:
        raise ValueError("scheduled digest interval must be at least one minute")
    as_of_utc = normalize_to_utc(as_of)
    if as_of_utc.second != 0 or as_of_utc.microsecond != 0:
        return False
    minutes_since_midnight = (as_of_utc.hour * 60) + as_of_utc.minute
    return minutes_since_midnight % interval_minutes == 0


def _decision(
    *,
    config: ScheduledDigestConfig,
    tick: ScheduledDigestTick,
    reason: ScheduledDigestDecisionReason,
    is_due: bool,
    should_build: bool,
    dedup_key: SnapshotNotificationDedupKey | None = None,
) -> ScheduledDigestDecision:
    return ScheduledDigestDecision(
        enabled=config.enabled,
        is_due=is_due,
        should_build=should_build,
        reason=reason,
        item_count=len(config.items),
        tick_as_of=tick.as_of,
        dedup_key=dedup_key,
    )


def _skipped_result(
    *,
    tick: ScheduledDigestTick,
    decision: ScheduledDigestDecision,
    dedup_key: SnapshotNotificationDedupKey | None = None,
    payload: SnapshotNotificationPayload | None = None,
) -> ScheduledDigestDeliveryResult:
    return ScheduledDigestDeliveryResult(
        tick=tick,
        decision=decision,
        delivered=False,
        skipped=True,
        dedup_key=dedup_key,
        payload=payload,
        record=None,
    )
