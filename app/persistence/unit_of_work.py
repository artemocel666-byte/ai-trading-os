from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.interfaces.repositories import (
    AuditLogRepository,
    CandleRepository,
    EconomicEventRepository,
    ErrorEventRepository,
    SystemStateRepository,
)
from app.persistence.repositories import (
    SqlAlchemyAuditLogRepository,
    SqlAlchemyCandleRepository,
    SqlAlchemyEconomicEventRepository,
    SqlAlchemyErrorEventRepository,
    SqlAlchemySystemStateRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._committed = False
        self._system_state: SystemStateRepository | None = None
        self._audit_logs: AuditLogRepository | None = None
        self._error_events: ErrorEventRepository | None = None
        self._candles: CandleRepository | None = None
        self._economic_events: EconomicEventRepository | None = None

    async def __aenter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("unit of work is already active")
        self._session = self._session_factory()
        self._committed = False
        self._system_state = SqlAlchemySystemStateRepository(self._session)
        self._audit_logs = SqlAlchemyAuditLogRepository(self._session)
        self._error_events = SqlAlchemyErrorEventRepository(self._session)
        self._candles = SqlAlchemyCandleRepository(self._session)
        self._economic_events = SqlAlchemyEconomicEventRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            in_transaction = getattr(self._session, "in_transaction", lambda: False)
            if exc_type is not None or not self._committed or in_transaction():
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
            self._system_state = None
            self._audit_logs = None
            self._error_events = None
            self._candles = None
            self._economic_events = None
            self._committed = False

    @property
    def system_state(self) -> SystemStateRepository:
        if self._session is None or self._system_state is None:
            raise RuntimeError("unit of work has not been entered")
        return self._system_state

    @property
    def audit_logs(self) -> AuditLogRepository:
        if self._session is None or self._audit_logs is None:
            raise RuntimeError("unit of work has not been entered")
        return self._audit_logs

    @property
    def error_events(self) -> ErrorEventRepository:
        if self._session is None or self._error_events is None:
            raise RuntimeError("unit of work has not been entered")
        return self._error_events

    @property
    def candles(self) -> CandleRepository:
        if self._session is None or self._candles is None:
            raise RuntimeError("unit of work has not been entered")
        return self._candles

    @property
    def economic_events(self) -> EconomicEventRepository:
        if self._session is None or self._economic_events is None:
            raise RuntimeError("unit of work has not been entered")
        return self._economic_events

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("unit of work has not been entered")
        await self._session.commit()
        self._committed = True

    async def rollback(self) -> None:
        if self._session is None:
            raise RuntimeError("unit of work has not been entered")
        await self._session.rollback()
        self._committed = False
