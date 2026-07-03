from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.persistence.database import create_engine, create_session_factory
from app.persistence.session import build_uow_factory
from app.services.system_state_service import SystemStateService


@pytest.mark.integration
@pytest.mark.asyncio
async def test_system_state_persists_in_postgresql(postgres_database_url: str) -> None:
    engine = create_engine(postgres_database_url)
    try:
        service = SystemStateService(build_uow_factory(create_session_factory(engine)))

        await service.enable_scanning(actor="integration-test")
        status = await service.get_full_status()

        assert status["scan_enabled"] is True
    finally:
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_uncommitted_failure(postgres_database_url: str) -> None:
    engine = create_engine(postgres_database_url)
    key = f"rollback_{uuid4().hex}"
    try:
        uow_factory = build_uow_factory(create_session_factory(engine))

        async def fail_inside_unit_of_work() -> None:
            async with uow_factory() as uow:
                await uow.system_state.set(key, {"value": "should_not_persist"})
                raise RuntimeError("force rollback")

        with pytest.raises(RuntimeError):
            await fail_inside_unit_of_work()

        async with uow_factory() as uow:
            value = await uow.system_state.get(key)

        assert value is None
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_api_health_readiness_status_and_scan_state(postgres_database_url: str) -> None:
    settings = Settings(_env_file=None, database_url=postgres_database_url)
    app = create_app(settings)

    with TestClient(app) as client:
        health = client.get("/health")
        ready = client.get("/ready")
        status = client.get("/api/v1/system/status")
        start = client.post(
            "/api/v1/system/scanning/start",
            headers={"X-Internal-API-Key": settings.internal_api_key.get_secret_value()},
        )
        stop = client.post(
            "/api/v1/system/scanning/stop",
            headers={"X-Internal-API-Key": settings.internal_api_key.get_secret_value()},
        )

    assert health.status_code == 200
    assert health.json() == {"status": "alive", "service": "api"}
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert status.status_code == 200
    assert status.json()["project_phase"] == "phase_2_data_adapters"
    assert status.json()["trading_strategy_implemented"] is False
    assert status.json()["real_trading_enabled"] is False
    assert start.status_code == 200
    assert start.json()["scan_enabled"] is True
    assert stop.status_code == 200
    assert stop.json()["scan_enabled"] is False


@pytest.mark.integration
def test_state_changing_endpoint_requires_internal_api_key(postgres_database_url: str) -> None:
    settings = Settings(_env_file=None, database_url=postgres_database_url)
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.post("/api/v1/system/scanning/start")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
