from app.core import constants
from app.core.config import Settings
from app.core.time import utc_now
from app.domain.interfaces.health import DatabaseHealthPort
from app.services.system_state_service import SystemStateService


class HealthService:
    def __init__(
        self,
        *,
        settings: Settings,
        database_health: DatabaseHealthPort,
        system_state_service: SystemStateService,
    ) -> None:
        self._settings = settings
        self._database_health = database_health
        self._system_state_service = system_state_service

    async def readiness(self) -> dict[str, str]:
        database_ok = await self._database_health.is_connected()
        schema_ok = await self._database_health.has_schema() if database_ok else False
        status = "ready" if database_ok and schema_ok else "not_ready"
        return {
            "status": status,
            "service": "api",
            "database": "ok" if database_ok else "unavailable",
            "schema": "ok" if schema_ok else "unavailable",
            "configuration": "ok",
        }

    async def system_status(self) -> dict[str, object]:
        database_ok = await self._database_health.is_connected()
        if database_ok:
            state = await self._system_state_service.get_full_status()
        else:
            state = {
                "scan_enabled": False,
                "worker_heartbeat": None,
                "last_successful_market_fetch": None,
                "last_successful_calendar_fetch": None,
                "last_error": None,
            }
        return {
            "app_environment": self._settings.app_env,
            "current_utc_time": utc_now().isoformat(),
            "user_timezone": self._settings.app_timezone,
            "scan_enabled": state["scan_enabled"],
            "worker_heartbeat": state["worker_heartbeat"],
            "last_successful_market_fetch": state["last_successful_market_fetch"],
            "last_successful_calendar_fetch": state["last_successful_calendar_fetch"],
            "last_error": state["last_error"],
            "enabled_integrations": self._settings.enabled_integrations(),
            "database_status": "ok" if database_ok else "unavailable",
            "project_phase": constants.PROJECT_PHASE,
            "strategy_implementation_status": "not_implemented",
            "trading_strategy_implemented": constants.STRATEGY_IMPLEMENTED,
            "real_trading_enabled": constants.REAL_TRADING_ENABLED,
        }
