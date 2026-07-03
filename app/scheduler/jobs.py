import logging
from typing import Any

from app.observability.health_checks import run_application_health_check
from app.services.health_service import HealthService
from app.services.system_state_service import SystemStateService

logger = logging.getLogger(__name__)


async def update_worker_heartbeat_job(service: SystemStateService) -> None:
    await service.update_worker_heartbeat()
    logger.info("worker_heartbeat_updated")


async def application_health_check_job(health_service: HealthService) -> None:
    result = await run_application_health_check(health_service)
    logger.info("worker_health_check_completed", extra={"database_status": result["database"]})


def register_jobs(
    scheduler: Any,
    *,
    system_state_service: SystemStateService,
    health_service: HealthService,
) -> None:
    scheduler.add_job(
        update_worker_heartbeat_job,
        "interval",
        seconds=30,
        args=[system_state_service],
        id="worker_heartbeat",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        application_health_check_job,
        "interval",
        seconds=60,
        args=[health_service],
        id="application_health_check",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
