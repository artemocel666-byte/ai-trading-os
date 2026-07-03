from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_health_service
from app.schemas.system import HealthResponse, ReadinessResponse
from app.services.health_service import HealthService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="alive", service="api")


@router.get("/ready", response_model=ReadinessResponse)
async def ready(
    health_service: HealthService = Depends(get_health_service),
) -> ReadinessResponse | JSONResponse:
    readiness = await health_service.readiness()
    if readiness["status"] != "ready":
        return JSONResponse(status_code=503, content=readiness)
    return ReadinessResponse(**readiness)
