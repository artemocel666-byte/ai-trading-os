import pytest

from app.core import constants
from app.core.exceptions import ErrorCode, NotImplementedFeatureError
from app.services.analysis_service import AnalysisService
from app.services.system_state_service import SystemStateService
from tests.fakes import FakeUnitOfWorkFactory


@pytest.mark.asyncio
async def test_scanning_defaults_to_false() -> None:
    service = SystemStateService(FakeUnitOfWorkFactory())

    status = await service.get_full_status()

    assert status["scan_enabled"] is False


@pytest.mark.asyncio
async def test_enable_and_disable_scanning_only_changes_state() -> None:
    factory = FakeUnitOfWorkFactory()
    service = SystemStateService(factory)

    enabled = await service.enable_scanning(actor="test")
    disabled = await service.disable_scanning(actor="test")

    assert enabled == {"scan_enabled": True}
    assert disabled == {"scan_enabled": False}
    assert factory.state[constants.SYSTEM_STATE_SCAN_ENABLED] is False
    assert all(instance.committed for instance in factory.instances)


@pytest.mark.asyncio
async def test_worker_heartbeat_is_recorded() -> None:
    factory = FakeUnitOfWorkFactory()
    service = SystemStateService(factory)

    await service.update_worker_heartbeat()

    assert isinstance(factory.state[constants.SYSTEM_STATE_WORKER_HEARTBEAT], str)


@pytest.mark.asyncio
async def test_record_system_error_updates_state_and_error_log() -> None:
    factory = FakeUnitOfWorkFactory()
    service = SystemStateService(factory)
    error = NotImplementedFeatureError("analysis_engine")

    await service.record_system_error(error, component="test")

    assert (
        factory.state[constants.SYSTEM_STATE_LAST_ERROR]["error_code"] == ErrorCode.NOT_IMPLEMENTED
    )
    error_repo = factory.instances[-1].error_events
    assert len(error_repo.events) == 1


@pytest.mark.asyncio
async def test_scan_now_cannot_fabricate_result() -> None:
    with pytest.raises(NotImplementedFeatureError):
        await AnalysisService().scan_now()
