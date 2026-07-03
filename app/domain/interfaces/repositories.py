from collections.abc import Mapping
from typing import Any, Protocol


class SystemStateRepository(Protocol):
    async def get(self, key: str) -> Any | None:
        """Return one state value by key."""

    async def set(self, key: str, value: Any) -> None:
        """Persist one state value by key."""

    async def get_all(self) -> dict[str, Any]:
        """Return all persisted system state values."""


class AuditLogRepository(Protocol):
    async def add(
        self,
        *,
        event_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        actor: str | None = None,
        before_json: Mapping[str, Any] | None = None,
        after_json: Mapping[str, Any] | None = None,
    ) -> None:
        """Append an audit log event."""


class ErrorEventRepository(Protocol):
    async def add(
        self,
        *,
        error_code: str,
        severity: str,
        component: str,
        message_ru: str,
        technical_details: str | None = None,
        context_json: Mapping[str, Any] | None = None,
        resolved: bool = False,
    ) -> None:
        """Append a structured error event."""
