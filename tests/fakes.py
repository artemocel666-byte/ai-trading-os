from types import TracebackType
from typing import Any, Self

from app.domain.interfaces.repositories import (
    AuditLogRepository,
    ErrorEventRepository,
    SystemStateRepository,
)


class FakeSystemStateRepository:
    def __init__(self, state: dict[str, Any]) -> None:
        self._state = state

    async def get(self, key: str) -> Any | None:
        return self._state.get(key)

    async def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    async def get_all(self) -> dict[str, Any]:
        return dict(self._state)


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: dict[str, Any] | None = None,
        after_json: dict[str, Any] | None = None,
    ) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "actor": actor,
                "before_json": before_json,
                "after_json": after_json,
            }
        )


class FakeErrorEventRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: dict[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        self.events.append(
            {
                "error_code": error_code,
                "severity": severity,
                "component": component,
                "message_ru": message_ru,
                "technical_details": technical_details,
                "context_json": context_json,
                "resolved": resolved,
            }
        )


class FakeUnitOfWork:
    def __init__(self, state: dict[str, Any]) -> None:
        self.system_state: SystemStateRepository = FakeSystemStateRepository(state)
        self.audit_logs: AuditLogRepository = FakeAuditLogRepository()
        self.error_events: ErrorEventRepository = FakeErrorEventRepository()
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self.committed:
            self.rolled_back = True

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeUnitOfWorkFactory:
    def __init__(self, state: dict[str, Any] | None = None) -> None:
        self.state = state or {}
        self.instances: list[FakeUnitOfWork] = []

    def __call__(self) -> FakeUnitOfWork:
        uow = FakeUnitOfWork(self.state)
        self.instances.append(uow)
        return uow
