import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.persistence.database import create_engine, create_session_factory
from app.persistence.database_health import SqlAlchemyDatabaseHealth
from app.persistence.session import build_uow_factory
from app.scheduler.jobs import register_jobs, update_worker_heartbeat_job
from app.services.health_service import HealthService
from app.services.system_state_service import SystemStateService

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    settings = get_settings()
    configure_logging("worker", settings.log_level)
    engine: AsyncEngine = create_engine(settings.database_dsn())
    session_factory = create_session_factory(engine)
    uow_factory = build_uow_factory(session_factory)
    system_state_service = SystemStateService(uow_factory)
    health_service = HealthService(
        settings=settings,
        database_health=SqlAlchemyDatabaseHealth(engine),
        system_state_service=system_state_service,
    )

    scheduler = AsyncIOScheduler(timezone=settings.app_timezone)
    register_jobs(
        scheduler,
        system_state_service=system_state_service,
        health_service=health_service,
    )

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    try:
        logger.info("worker_starting")
        await update_worker_heartbeat_job(system_state_service)
        scheduler.start()
        logger.info("worker_started")
        await stop_event.wait()
    finally:
        logger.info("worker_stopping")
        scheduler.shutdown(wait=False)
        await engine.dispose()
        logger.info("worker_stopped")


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
