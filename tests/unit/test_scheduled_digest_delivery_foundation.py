from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, cast

import pytest
from pydantic import ValidationError

from app.core import constants
from app.domain.entities import Candle, Timeframe
from app.domain.entities.readiness import SnapshotNotificationPayload, SnapshotScheduleItem
from app.domain.entities.scheduled_digest import (
    ScheduledDigestConfig,
    ScheduledDigestDecisionReason,
    ScheduledDigestTick,
)
from app.domain.value_objects import CurrencyPair
from app.scheduler.jobs import register_jobs, scheduled_digest_delivery_job
from app.services.analysis_service import AnalysisService
from app.services.health_service import HealthService
from app.services.readiness_digest_service import ReadinessDigestService
from app.services.scheduled_digest_delivery_service import (
    InMemoryScheduledDigestDeliveryStore,
    ScheduledDigestDeliveryService,
    is_scheduled_digest_due,
)
from app.services.system_state_service import SystemStateService
from tests.fakes import FakeUnitOfWorkFactory

PAIR = CurrencyPair(value="EURUSD")
BASE_TIME = datetime(2026, 7, 15, 8, 0, tzinfo=UTC)


class FakeNotificationSender:
    def __init__(self) -> None:
        self.payloads: list[SnapshotNotificationPayload] = []

    async def send(self, payload: SnapshotNotificationPayload) -> None:
        self.payloads.append(payload)


class FailingReadinessDigestService:
    async def build_payload(
        self,
        *,
        items: tuple[SnapshotScheduleItem, ...],
        as_of: datetime,
    ) -> SnapshotNotificationPayload:
        raise RuntimeError("forced digest build failure")


class FakeScheduler:
    def __init__(self) -> None:
        self.job_ids: list[str] = []

    def add_job(self, *args: Any, **kwargs: Any) -> None:
        self.job_ids.append(str(kwargs["id"]))


def _schedule_config(*, enabled: bool = True, interval_minutes: int = 15) -> ScheduledDigestConfig:
    return ScheduledDigestConfig(
        enabled=enabled,
        interval_minutes=interval_minutes,
        items=(
            SnapshotScheduleItem(
                pair=PAIR,
                timeframe=Timeframe.M15,
                lookback_candle_count=3,
            ),
        ),
    )


def _candle(index: int) -> Candle:
    open_time = BASE_TIME + timedelta(minutes=15 * index)
    open_price = Decimal("1.1000") + (Decimal("0.0001") * Decimal(index))
    close_price = open_price + Decimal("0.0001")
    return Candle(
        provider="scheduled-digest-test",
        pair=PAIR,
        timeframe=Timeframe.M15,
        open_time=open_time,
        close_time=open_time + timedelta(minutes=15),
        open=open_price,
        high=close_price + Decimal("0.0002"),
        low=open_price - Decimal("0.0002"),
        close=close_price,
        volume=Decimal("100"),
        is_closed=True,
    )


def _service(
    *,
    config: ScheduledDigestConfig | None = None,
    sender: FakeNotificationSender | None = None,
    store: InMemoryScheduledDigestDeliveryStore | None = None,
) -> tuple[ScheduledDigestDeliveryService, FakeNotificationSender]:
    notification_sender = sender or FakeNotificationSender()
    factory = FakeUnitOfWorkFactory(candles=[_candle(0), _candle(1), _candle(2)])
    readiness_service = ReadinessDigestService(AnalysisService(factory))
    return (
        ScheduledDigestDeliveryService(
            config=config or _schedule_config(),
            readiness_digest_service=readiness_service,
            sender=notification_sender,
            delivery_store=store or InMemoryScheduledDigestDeliveryStore(),
            sender_name="fake_sender",
        ),
        notification_sender,
    )


@pytest.mark.asyncio
async def test_scheduled_digest_disabled_skip() -> None:
    service, sender = _service(config=_schedule_config(enabled=False))

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.delivered is False
    assert result.decision.reason == ScheduledDigestDecisionReason.DISABLED
    assert result.payload is None
    assert sender.payloads == []


@pytest.mark.asyncio
async def test_scheduled_digest_not_due_skip() -> None:
    service, sender = _service(config=_schedule_config(interval_minutes=60))

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.decision.reason == ScheduledDigestDecisionReason.NOT_DUE
    assert result.decision.is_due is False
    assert sender.payloads == []


@pytest.mark.asyncio
async def test_scheduled_digest_due_builds_payload_and_sends_once() -> None:
    service, sender = _service()

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.delivered is True
    assert result.skipped is False
    assert result.decision.reason == ScheduledDigestDecisionReason.DELIVERED
    assert result.payload is not None
    assert result.record is not None
    assert result.dedup_key == result.payload.dedup_key
    assert len(sender.payloads) == 1
    assert sender.payloads[0] == result.payload
    assert "Системный отчёт готовности" in result.payload.text
    assert "Решений и указаний нет." in result.payload.text
    data = result.model_dump(mode="json")
    assert data["project_phase"] == constants.PROJECT_PHASE
    assert data["payload"]["project_phase"] == constants.PROJECT_PHASE
    with pytest.raises(ValidationError):
        result.delivered = False


@pytest.mark.asyncio
async def test_scheduled_digest_duplicate_dedup_key_skip() -> None:
    store = InMemoryScheduledDigestDeliveryStore()
    sender = FakeNotificationSender()
    service, _ = _service(store=store, sender=sender)
    as_of = BASE_TIME + timedelta(minutes=45)

    first = await service.run_tick(as_of=as_of)
    second = await service.run_tick(as_of=as_of)

    assert first.delivered is True
    assert second.skipped is True
    assert second.decision.reason == ScheduledDigestDecisionReason.DUPLICATE
    assert second.dedup_key == first.dedup_key
    assert len(sender.payloads) == 1


@pytest.mark.asyncio
async def test_scheduled_digest_no_items_skip() -> None:
    service, sender = _service(config=ScheduledDigestConfig(enabled=True, items=()))

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.decision.reason == ScheduledDigestDecisionReason.NO_ITEMS
    assert sender.payloads == []


@pytest.mark.asyncio
async def test_scheduled_digest_build_failed_skip() -> None:
    sender = FakeNotificationSender()
    service = ScheduledDigestDeliveryService(
        config=_schedule_config(),
        readiness_digest_service=FailingReadinessDigestService(),
        sender=sender,
        delivery_store=InMemoryScheduledDigestDeliveryStore(),
    )

    result = await service.run_tick(as_of=BASE_TIME + timedelta(minutes=45))

    assert result.skipped is True
    assert result.decision.reason == ScheduledDigestDecisionReason.BUILD_FAILED
    assert result.payload is None
    assert sender.payloads == []


def test_scheduled_digest_tick_is_json_serializable_and_immutable() -> None:
    tick = ScheduledDigestTick(as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC))

    data = tick.model_dump(mode="json")

    assert data["project_phase"] == constants.PROJECT_PHASE
    assert data["as_of"] == "2026-07-15T10:45:00Z"
    with pytest.raises(ValidationError):
        tick.as_of = BASE_TIME


def test_scheduled_digest_tick_normalizes_utc() -> None:
    tick = ScheduledDigestTick(
        as_of=datetime(2026, 7, 15, 12, 45, tzinfo=timezone(timedelta(hours=2)))
    )

    assert tick.as_of == datetime(2026, 7, 15, 10, 45, tzinfo=UTC)


def test_scheduled_digest_due_policy_is_deterministic() -> None:
    assert is_scheduled_digest_due(
        as_of=datetime(2026, 7, 15, 10, 45, tzinfo=UTC),
        interval_minutes=15,
    )
    assert not is_scheduled_digest_due(
        as_of=datetime(2026, 7, 15, 10, 46, tzinfo=UTC),
        interval_minutes=15,
    )
    assert not is_scheduled_digest_due(
        as_of=datetime(2026, 7, 15, 10, 45, 1, tzinfo=UTC),
        interval_minutes=15,
    )


@pytest.mark.asyncio
async def test_worker_callable_can_run_without_auto_registration() -> None:
    service, sender = _service()

    result = await scheduled_digest_delivery_job(
        service,
        as_of=BASE_TIME + timedelta(minutes=45),
    )

    assert result.delivered is True
    assert len(sender.payloads) == 1


def test_register_jobs_does_not_start_scheduled_digest_delivery_loop() -> None:
    scheduler = FakeScheduler()

    register_jobs(
        scheduler,
        system_state_service=cast(SystemStateService, object()),
        health_service=cast(HealthService, object()),
    )

    assert scheduler.job_ids == ["worker_heartbeat", "application_health_check"]
