import pytest
from pydantic import ValidationError

from app.api.dependencies import require_internal_api_key
from app.core.config import Settings
from app.core.exceptions import UnauthorizedError


@pytest.mark.asyncio
async def test_missing_internal_api_key_is_rejected() -> None:
    settings = Settings(_env_file=None)

    with pytest.raises(UnauthorizedError):
        await require_internal_api_key(settings=settings, x_internal_api_key=None)


@pytest.mark.asyncio
async def test_invalid_internal_api_key_is_rejected() -> None:
    settings = Settings(_env_file=None)

    with pytest.raises(UnauthorizedError):
        await require_internal_api_key(settings=settings, x_internal_api_key="wrong")


@pytest.mark.asyncio
async def test_valid_internal_api_key_is_accepted() -> None:
    settings = Settings(_env_file=None, internal_api_key="safe-development-key")

    await require_internal_api_key(
        settings=settings,
        x_internal_api_key="safe-development-key",
    )


def test_default_internal_api_key_rejected_outside_development() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production")
