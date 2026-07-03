from collections.abc import Mapping
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import redact_text
from app.core.time import utc_now
from app.persistence.models import AuditLogModel, ErrorEventModel, SystemStateModel


class SqlAlchemySystemStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str) -> Any | None:
        row = await self._session.get(SystemStateModel, key)
        return None if row is None else row.value_json

    async def set(self, key: str, value: Any) -> None:
        row = await self._session.get(SystemStateModel, key)
        if row is None:
            self._session.add(SystemStateModel(key=key, value_json=value))
            return
        row.value_json = value
        row.updated_at = utc_now()

    async def get_all(self) -> dict[str, Any]:
        result = await self._session.execute(select(SystemStateModel))
        rows = result.scalars().all()
        return {row.key: row.value_json for row in rows}


class SqlAlchemyAuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        self._session.add(
            AuditLogModel(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                actor=actor,
                before_json=dict(before_json) if before_json is not None else None,
                after_json=dict(after_json) if after_json is not None else None,
            )
        )


class SqlAlchemyErrorEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        self._session.add(
            ErrorEventModel(
                error_code=error_code,
                severity=severity,
                component=component,
                message_ru=message_ru,
                technical_details=redact_text(technical_details) if technical_details else None,
                context_json=dict(context_json) if context_json is not None else None,
                resolved=resolved,
            )
        )
