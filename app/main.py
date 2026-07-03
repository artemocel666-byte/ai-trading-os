from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.adapters.factories import (
    create_economic_calendar_provider,
    create_market_data_provider,
    create_provider_clients,
)
from app.api.error_handlers import register_error_handlers
from app.api.routes.health import router as health_router
from app.api.routes.system import router as system_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.persistence.database import create_engine, create_session_factory
from app.persistence.database_health import SqlAlchemyDatabaseHealth
from app.persistence.session import build_uow_factory
from app.services.health_service import HealthService
from app.services.system_state_service import SystemStateService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging("api", settings.log_level)
    engine: AsyncEngine = create_engine(settings.database_dsn())
    session_factory = create_session_factory(engine)
    uow_factory = build_uow_factory(session_factory)
    system_state_service = SystemStateService(uow_factory)
    provider_clients = create_provider_clients(settings)
    try:
        app.state.engine = engine
        app.state.uow_factory = uow_factory
        app.state.system_state_service = system_state_service
        app.state.provider_clients = provider_clients
        app.state.market_data_provider = create_market_data_provider(
            settings,
            client=provider_clients.market_data,
        )
        app.state.economic_calendar_provider = create_economic_calendar_provider(
            settings,
            client=provider_clients.economic_calendar,
        )
        app.state.health_service = HealthService(
            settings=settings,
            database_health=SqlAlchemyDatabaseHealth(engine),
            system_state_service=system_state_service,
        )
        yield
    finally:
        await provider_clients.aclose()
        await engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(title=app_settings.app_name, lifespan=lifespan)
    app.state.settings = app_settings

    @app.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(system_router)
    return app


app = create_app()
