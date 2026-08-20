from collections.abc import Callable
from types import TracebackType
from typing import Protocol, Self

from app.domain.interfaces.notifications import ScheduledDigestDeliveryStore
from app.domain.interfaces.repositories import (
    AuditLogRepository,
    CandleRepository,
    EconomicEventRepository,
    ErrorEventRepository,
    ForwardOutcomeRepository,
    InterestRateRepository,
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

    @property
    def forward_outcomes(self) -> ForwardOutcomeRepository:
        """Repository for pre-registered plans and the outcomes settled onto them."""
        ...

    @property
    def interest_rates(self) -> InterestRateRepository:
        """Repository for short-term interest rates, one row per currency per month.

        Added to the protocol in Phase 10-1. Phase 9D-3 gave the implementation this slot and left
        the interface without it: the only caller was a script, and `mypy` checks `app` alone, so
        nothing said the two had drifted. The first service to need rates found it immediately.
        """
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


#: How a caller obtains a unit of work. Defined here, beside the thing it produces.
#:
#: Phase 10-1 found this alias written out identically in eight service modules. Harmless while all
#: eight agreed, and precisely the shape of every fault this project has had to repair: the delta
#: map that was half-added, the request-range limit that lived in two places, the month arithmetic
#: copied into two scripts before a third needed it. Adding a ninth copy was the alternative.
UnitOfWorkFactory = Callable[[], UnitOfWork]
