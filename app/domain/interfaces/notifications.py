from typing import Protocol

from app.domain.entities.readiness import SnapshotNotificationDedupKey, SnapshotNotificationPayload
from app.domain.entities.scheduled_digest import ScheduledDigestDeliveryRecord


class NotificationSender(Protocol):
    async def send(self, payload: SnapshotNotificationPayload) -> None:
        """Deliver a neutral readiness notification payload."""


class ScheduledDigestDeliveryStore(Protocol):
    async def exists(self, dedup_key: SnapshotNotificationDedupKey) -> bool:
        """Return whether a scheduled digest deduplication key is already recorded."""

    async def record(self, record: ScheduledDigestDeliveryRecord) -> None:
        """Record a delivered scheduled digest deduplication key."""

    async def get(
        self,
        dedup_key: SnapshotNotificationDedupKey,
    ) -> ScheduledDigestDeliveryRecord | None:
        """Return one neutral scheduled digest delivery audit record when present."""
