from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_health_service,
    get_system_state_service,
    require_internal_api_key,
)
from app.schemas.system import ScanningStateResponse, SystemStatusResponse
from app.services.health_service import HealthService
from app.services.system_state_service import SystemStateService

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/status", response_model=SystemStatusResponse)
async def system_status(
    health_service: HealthService = Depends(get_health_service),
) -> SystemStatusResponse:
    status = await health_service.system_status()
    return SystemStatusResponse(**status)


@router.post(
    "/scanning/start",
    response_model=ScanningStateResponse,
    dependencies=[Depends(require_internal_api_key)],
)
async def start_scanning(
    service: SystemStateService = Depends(get_system_state_service),
) -> ScanningStateResponse:
    state = await service.enable_scanning(actor="api")
    return ScanningStateResponse(
        scan_enabled=state["scan_enabled"],
        message_ru="Состояние сканирования включено. Аналитическая стратегия ещё не подключена.",
    )


@router.post(
    "/scanning/stop",
    response_model=ScanningStateResponse,
    dependencies=[Depends(require_internal_api_key)],
)
async def stop_scanning(
    service: SystemStateService = Depends(get_system_state_service),
) -> ScanningStateResponse:
    state = await service.disable_scanning(actor="api")
    return ScanningStateResponse(
        scan_enabled=state["scan_enabled"],
        message_ru="Состояние сканирования выключено.",
    )
