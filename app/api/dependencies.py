from collections.abc import Callable
from typing import cast

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError
from app.core.security import constant_time_equals
from app.services.health_service import HealthService
from app.services.system_state_service import SystemStateService


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_engine(request: Request) -> AsyncEngine:
    return cast(AsyncEngine, request.app.state.engine)


def get_system_state_service(request: Request) -> SystemStateService:
    return cast(SystemStateService, request.app.state.system_state_service)


def get_health_service(request: Request) -> HealthService:
    return cast(HealthService, request.app.state.health_service)


def get_uow_factory(request: Request) -> Callable[[], object]:
    return cast(Callable[[], object], request.app.state.uow_factory)


async def require_internal_api_key(
    settings: Settings = Depends(get_settings),
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
) -> None:
    expected = settings.internal_api_key.get_secret_value()
    if not x_internal_api_key or not constant_time_equals(x_internal_api_key, expected):
        raise UnauthorizedError()
