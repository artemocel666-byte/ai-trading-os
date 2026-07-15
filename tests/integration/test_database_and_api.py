from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.value_objects import CurrencyPair
from app.main import create_app
from app.persistence.database import create_engine, create_session_factory
from app.persistence.models import CandleModel, EconomicEventModel
from app.persistence.session import build_uow_factory
from app.services.system_state_service import SystemStateService

_MARKET_CALENDAR_TEST_PROVIDER = "integration-phase3a-repository-test"


async def _delete_market_calendar_test_rows(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        await session.execute(
            delete(CandleModel).where(CandleModel.provider == _MARKET_CALENDAR_TEST_PROVIDER)
        )
        await session.execute(
            delete(EconomicEventModel).where(
                EconomicEventModel.provider == _MARKET_CALENDAR_TEST_PROVIDER
            )
        )
        await session.commit()


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
    assert status.json()["project_phase"] == "phase_3h_scheduled_digest_delivery_foundation"
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_market_and_calendar_repositories_upsert_and_query(
    postgres_database_url: str,
) -> None:
    engine = create_engine(postgres_database_url)
    session_factory = create_session_factory(engine)
    try:
        await _delete_market_calendar_test_rows(session_factory)
        uow_factory = build_uow_factory(session_factory)
        pair = CurrencyPair(value="EURUSD")
        candle = Candle(
            provider=_MARKET_CALENDAR_TEST_PROVIDER,
            pair=pair,
            timeframe=Timeframe.M15,
            open_time=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
            close_time=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
            open=Decimal("1.1000"),
            high=Decimal("1.1050"),
            low=Decimal("1.0950"),
            close=Decimal("1.1020"),
            volume=Decimal("100"),
            is_closed=True,
        )
        updated_candle = candle.model_copy(update={"close": Decimal("1.1030")})
        event = EconomicEvent(
            provider=_MARKET_CALENDAR_TEST_PROVIDER,
            provider_event_id="phase3a-cpi-event",
            title="Consumer Price Index",
            currency="EUR",
            country="Eurozone",
            impact=EconomicImpact.HIGH,
            scheduled_at=datetime(2026, 7, 8, 8, 5, tzinfo=UTC),
            actual=Decimal("2.2"),
            forecast=Decimal("2.1"),
            previous=Decimal("2.0"),
            fetched_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
        )
        updated_event = event.model_copy(update={"actual": Decimal("2.3")})

        async with uow_factory() as uow:
            candle_insert = await uow.candles.upsert_many([candle])
            candle_update = await uow.candles.upsert_many([updated_candle])
            event_insert = await uow.economic_events.upsert_many([event])
            event_update = await uow.economic_events.upsert_many([updated_event])
            await uow.commit()

        async with uow_factory() as uow:
            candles = await uow.candles.list_range(
                pair=pair,
                timeframe=Timeframe.M15,
                start_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
                end_at=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
                provider=_MARKET_CALENDAR_TEST_PROVIDER,
            )
            events = await uow.economic_events.list_window(
                start_at=datetime(2026, 7, 8, 8, 0, tzinfo=UTC),
                end_at=datetime(2026, 7, 8, 8, 15, tzinfo=UTC),
                currencies=["EUR"],
                provider=_MARKET_CALENDAR_TEST_PROVIDER,
            )

        assert candle_insert.inserted == 1
        assert candle_update.updated == 1
        assert event_insert.inserted == 1
        assert event_update.updated == 1
        assert [stored.close for stored in candles] == [Decimal("1.1030000000")]
        assert [stored.actual for stored in events] == [Decimal("2.300000")]
    finally:
        await _delete_market_calendar_test_rows(session_factory)
        await engine.dispose()
