from types import TracebackType
from typing import Protocol, Self

from app.domain.interfaces.notifications import ScheduledDigestDeliveryStore
from app.domain.interfaces.repositories import (
    AuditLogRepository,
    CandleRepository,
    EconomicEventRepository,
    ErrorEventRepository,
    SystemStateRepository,
)


class UnitOfWork(Protocol):
    @property
    def system_state(self) -> SystemStateRepository:
        """Repository for persisted system state."""
        ...

    @property
    def audit_logs(self) -> AuditLogRepository:
        """Repository for audit events."""
        ...

    @property
    def error_events(self) -> ErrorEventRepository:
        """Repository for structured error events."""
        ...

    @property
    def candles(self) -> CandleRepository:
        """Repository for normalized closed candles."""
        ...

    @property
    def economic_events(self) -> EconomicEventRepository:
        """Repository for normalized economic events."""
        ...

    @property
    def scheduled_digest_deliveries(self) -> ScheduledDigestDeliveryStore:
        """Store for neutral scheduled digest delivery audit records."""
        ...

    async def __aenter__(self) -> Self:
        """Open one asynchronous persistence boundary."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback uncommitted work and close resources."""

    async def commit(self) -> None:
        """Commit the current unit of work explicitly."""

    async def rollback(self) -> None:
        """Rollback the current unit of work."""
