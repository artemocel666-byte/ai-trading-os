from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import constants
from app.core.config import Settings
from app.domain.entities import Candle, EconomicEvent, EconomicImpact, Timeframe
from app.domain.entities.readiness import (
    SnapshotDigest,
    SnapshotDigestItem,
    SnapshotDigestStatus,
    SnapshotNotificationDedupKey,
    SnapshotNotificationPayload,
    SnapshotScheduleItem,
)
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecisionReason,
    ScheduledDigestDeliveryRecord,
)
from app.domain.value_objects import CurrencyPair
from app.main import create_app
from app.persistence.database import create_engine, create_session_factory
from app.persistence.models import CandleModel, EconomicEventModel, ScheduledDigestDeliveryModel
from app.persistence.session import build_uow_factory
from app.services.scheduled_digest_delivery_service import ScheduledDigestDeliveryService
from app.services.system_state_service import SystemStateService

_MARKET_CALENDAR_TEST_PROVIDER = "integration-phase3a-repository-test"
_SCHEDULED_DIGEST_TEST_SENDER = "integration-phase3i-sender"


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


async def _delete_scheduled_digest_test_rows(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        await session.execute(
            delete(ScheduledDigestDeliveryModel).where(
                ScheduledDigestDeliveryModel.sender_name == _SCHEDULED_DIGEST_TEST_SENDER
            )
        )
        await session.commit()


class FakeNotificationSender:
    def __init__(self) -> None:
        self.payloads: list[SnapshotNotificationPayload] = []

    async def send(self, payload: SnapshotNotificationPayload) -> None:
        self.payloads.append(payload)


class StaticReadinessDigestPayloadBuilder:
    def __init__(self, payload: SnapshotNotificationPayload) -> None:
        self._payload = payload

    async def build_payload(
        self,
        *,
        items: tuple[SnapshotScheduleItem, ...],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        return self._payload


def _dedup_key(seed: str) -> SnapshotNotificationDedupKey:
    return SnapshotNotificationDedupKey(value=(seed * 64)[:64])


def _scheduled_digest_payload(
    dedup_key: SnapshotNotificationDedupKey,
) -> SnapshotNotificationPayload:
    as_of = datetime(2026, 7, 15, 10, 45, tzinfo=UTC)
    item = SnapshotDigestItem(
        pair=CurrencyPair(value="EURUSD"),
        timeframe=Timeframe.M15,
        window_start=datetime(2026, 7, 15, 10, 0, tzinfo=UTC),
        window_end=as_of,
        as_of=as_of,
        readiness_status=SnapshotDigestStatus.READY,
        input_candle_count=3,
        used_candle_count=3,
        input_event_count=0,
        used_event_count=0,
        issue_count=0,
        no_candles_after_as_of_used=True,
        no_events_after_as_of_used=True,
        snapshot_id="b" * 64,
        dedup_key=dedup_key,
    )
    digest = SnapshotDigest(
        project_phase=constants.PROJECT_PHASE,
        generated_at=as_of,
        as_of=as_of,
        readiness_status=SnapshotDigestStatus.READY,
        items=(item,),
        ready_count=1,
        incomplete_count=0,
        blocked_count=0,
        dedup_key=dedup_key,
    )
    return SnapshotNotificationPayload(
        project_phase=constants.PROJECT_PHASE,
        dedup_key=dedup_key,
        digest=digest,
        text="Системный отчёт готовности. Решений и указаний нет.",
    )


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
    assert status.json()["project_phase"] == constants.PROJECT_PHASE
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scheduled_digest_delivery_store_persists_and_deduplicates(
    postgres_database_url: str,
) -> None:
    engine = create_engine(postgres_database_url)
    session_factory = create_session_factory(engine)
    dedup_key = _dedup_key("c")
    record = ScheduledDigestDeliveryRecord(
        dedup_key=dedup_key,
        delivered_at=datetime(2026, 7, 15, 12, 45, tzinfo=UTC),
        sender_name=_SCHEDULED_DIGEST_TEST_SENDER,
        readiness_status=SnapshotDigestStatus.READY,
        item_count=1,
        ready_count=1,
        incomplete_count=0,
        blocked_count=0,
        items_summary="EURUSD:M15",
        payload_preview="Системный отчёт готовности. Решений и указаний нет.",
    )
    try:
        await _delete_scheduled_digest_test_rows(session_factory)
        uow_factory = build_uow_factory(session_factory)

        async with uow_factory() as uow:
            assert await uow.scheduled_digest_deliveries.exists(dedup_key) is False
            await uow.scheduled_digest_deliveries.record(record)
            await uow.scheduled_digest_deliveries.record(record)
            await uow.commit()

        duplicate_record = record.model_copy(
            update={
                "readiness_status": SnapshotDigestStatus.INCOMPLETE,
                "item_count": 2,
                "ready_count": 0,
                "incomplete_count": 2,
                "items_summary": "EURUSD:M15,GBPUSD:M15",
                "payload_preview": "Повторная запись не должна менять первый аудит.",
            }
        )
        async with uow_factory() as uow:
            await uow.scheduled_digest_deliveries.record(duplicate_record)
            await uow.commit()

        async with uow_factory() as uow:
            assert await uow.scheduled_digest_deliveries.exists(dedup_key) is True
            stored = await uow.scheduled_digest_deliveries.get(dedup_key)

        assert stored is not None
        assert stored.project_phase == constants.PROJECT_PHASE
        assert stored.delivered_at == datetime(2026, 7, 15, 12, 45, tzinfo=UTC)
        assert stored.sender_name == _SCHEDULED_DIGEST_TEST_SENDER
        assert stored.readiness_status == SnapshotDigestStatus.READY
        assert stored.item_count == 1
        assert stored.ready_count == 1
        assert stored.incomplete_count == 0
        assert stored.items_summary == "EURUSD:M15"
        assert "Решений и указаний нет" in (stored.payload_preview or "")

    finally:
        await _delete_scheduled_digest_test_rows(session_factory)
        await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scheduled_digest_delivery_service_skips_persisted_duplicate(
    postgres_database_url: str,
) -> None:
    engine = create_engine(postgres_database_url)
    session_factory = create_session_factory(engine)
    dedup_key = _dedup_key("d")
    payload = _scheduled_digest_payload(dedup_key)
    config = ScheduledDigestConfig(
        enabled=True,
        interval_minutes=15,
        items=(
            SnapshotScheduleItem(
                pair=CurrencyPair(value="EURUSD"),
                timeframe=Timeframe.M15,
                lookback_candle_count=3,
            ),
        ),
    )
    try:
        await _delete_scheduled_digest_test_rows(session_factory)
        uow_factory = build_uow_factory(session_factory)

        first_sender = FakeNotificationSender()
        async with uow_factory() as uow:
            service = ScheduledDigestDeliveryService(
                config=config,
                readiness_digest_service=StaticReadinessDigestPayloadBuilder(payload),
                sender=first_sender,
                delivery_store=uow.scheduled_digest_deliveries,
                sender_name=_SCHEDULED_DIGEST_TEST_SENDER,
            )
            first = await service.run_tick(as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC))
            await uow.commit()

        second_sender = FakeNotificationSender()
        async with uow_factory() as uow:
            service = ScheduledDigestDeliveryService(
                config=config,
                readiness_digest_service=StaticReadinessDigestPayloadBuilder(payload),
                sender=second_sender,
                delivery_store=uow.scheduled_digest_deliveries,
                sender_name=_SCHEDULED_DIGEST_TEST_SENDER,
            )
            second = await service.run_tick(as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC))

        assert first.delivered is True
        assert len(first_sender.payloads) == 1
        assert second.skipped is True
        assert second.decision.reason == ScheduledDigestDecisionReason.DUPLICATE
        assert second.dedup_key == first.dedup_key
        assert second_sender.payloads == []

    finally:
        await _delete_scheduled_digest_test_rows(session_factory)
        await engine.dispose()
