from collections.abc import Callable
from typing import Any

from app.core import constants
from app.core.exceptions import ApplicationError
from app.core.security import redact_text
from app.core.time import utc_now
from app.domain.interfaces.unit_of_work import UnitOfWork

UnitOfWorkFactory = Callable[[], UnitOfWork]


class SystemStateService:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def get_full_status(self) -> dict[str, Any]:
        async with self._uow_factory() as uow:
            state = await uow.system_state.get_all()
        return {
            "scan_enabled": bool(state.get(constants.SYSTEM_STATE_SCAN_ENABLED, False)),
            "worker_heartbeat": state.get(constants.SYSTEM_STATE_WORKER_HEARTBEAT),
            "last_successful_market_fetch": state.get(
                constants.SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH
            ),
            "last_successful_calendar_fetch": state.get(
                constants.SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH
            ),
            "last_error": state.get(constants.SYSTEM_STATE_LAST_ERROR),
        }

    async def enable_scanning(self, *, actor: str) -> dict[str, bool]:
        async with self._uow_factory() as uow:
            before = await uow.system_state.get(constants.SYSTEM_STATE_SCAN_ENABLED)
            await uow.system_state.set(constants.SYSTEM_STATE_SCAN_ENABLED, True)
            await uow.audit_logs.add(
                event_type="scan_state_enabled",
                entity_type="system_state",
                entity_id=constants.SYSTEM_STATE_SCAN_ENABLED,
                actor=actor,
                before_json={"scan_enabled": bool(before) if before is not None else False},
                after_json={"scan_enabled": True},
            )
            await uow.commit()
        return {"scan_enabled": True}

    async def disable_scanning(self, *, actor: str) -> dict[str, bool]:
        async with self._uow_factory() as uow:
            before = await uow.system_state.get(constants.SYSTEM_STATE_SCAN_ENABLED)
            await uow.system_state.set(constants.SYSTEM_STATE_SCAN_ENABLED, False)
            await uow.audit_logs.add(
                event_type="scan_state_disabled",
                entity_type="system_state",
                entity_id=constants.SYSTEM_STATE_SCAN_ENABLED,
                actor=actor,
                before_json={"scan_enabled": bool(before) if before is not None else False},
                after_json={"scan_enabled": False},
            )
            await uow.commit()
        return {"scan_enabled": False}

    async def update_worker_heartbeat(self) -> None:
        async with self._uow_factory() as uow:
            await uow.system_state.set(
                constants.SYSTEM_STATE_WORKER_HEARTBEAT,
                utc_now().isoformat(),
            )
            await uow.commit()

    async def record_integration_health(self, integration: str) -> None:
        key_by_integration = {
            "market_data": constants.SYSTEM_STATE_LAST_SUCCESSFUL_MARKET_FETCH,
            "calendar": constants.SYSTEM_STATE_LAST_SUCCESSFUL_CALENDAR_FETCH,
        }
        key = key_by_integration.get(integration)
        if key is None:
            raise ValueError(f"unsupported integration health key: {integration}")
        async with self._uow_factory() as uow:
            await uow.system_state.set(key, utc_now().isoformat())
            await uow.commit()

    async def record_system_error(
        self,
        error: ApplicationError,
        *,
        component: str,
        technical_details: str | None = None,
    ) -> None:
        error_payload = {
            "error_code": error.code.value,
            "message_ru": error.message_ru,
            "recorded_at": utc_now().isoformat(),
            "component": component,
        }
        async with self._uow_factory() as uow:
            await uow.system_state.set(constants.SYSTEM_STATE_LAST_ERROR, error_payload)
            await uow.error_events.add(
                error_code=error.code.value,
                severity="ERROR",
                component=component,
                message_ru=error.message_ru,
                technical_details=redact_text(technical_details) if technical_details else None,
                context_json=error.details,
            )
            await uow.commit()

    async def record_unauthorized_telegram_access(
        self,
        *,
        user_id: int | None,
        chat_id: int | None,
        command: str,
    ) -> None:
        async with self._uow_factory() as uow:
            await uow.audit_logs.add(
                event_type="telegram_unauthorized_access",
                entity_type="telegram_command",
                entity_id=command,
                actor="telegram",
                after_json={"user_id": user_id, "chat_id": chat_id},
            )
            await uow.commit()
