from types import TracebackType
from typing import Protocol, Self

from app.domain.interfaces.repositories import (
    AuditLogRepository,
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
