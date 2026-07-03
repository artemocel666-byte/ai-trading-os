from app.services.health_service import HealthService


async def run_application_health_check(health_service: HealthService) -> dict[str, str]:
    """Run the foundation health check without touching market or broker providers."""

    return await health_service.readiness()
