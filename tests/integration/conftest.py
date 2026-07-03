import asyncio
import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import Settings, get_settings
from app.core.security import redact_text
from app.persistence.database import create_engine


async def _can_connect(database_url: str) -> bool:
    engine = create_engine(database_url)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return False
    finally:
        await engine.dispose()
    return True


@pytest.fixture(scope="session")
def postgres_database_url() -> str:
    settings = Settings(_env_file=None)
    database_url = os.getenv("TEST_DATABASE_URL") or settings.test_database_dsn()
    if database_url is None:
        if settings.require_integration_tests:
            pytest.fail("TEST_DATABASE_URL is required when REQUIRE_INTEGRATION_TESTS=true")
        pytest.skip("TEST_DATABASE_URL is not configured")
    if not asyncio.run(_can_connect(database_url)):
        if settings.require_integration_tests:
            pytest.fail(f"PostgreSQL test database is unavailable: {redact_text(database_url)}")
        pytest.skip(f"PostgreSQL test database is unavailable: {redact_text(database_url)}")
    return database_url


@pytest.fixture(scope="session", autouse=True)
def migrated_database(postgres_database_url: str) -> Iterator[None]:
    os.environ["DATABASE_URL"] = postgres_database_url
    get_settings.cache_clear()
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    yield
    get_settings.cache_clear()
