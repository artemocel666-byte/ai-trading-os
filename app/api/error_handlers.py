import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import ApplicationError, ErrorCode
from app.core.security import redact_secrets

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    value = getattr(request.state, "request_id", None)
    return str(value) if value else "unknown"


def error_content(
    *,
    code: str,
    message_ru: str,
    request_id: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message_ru": message_ru,
            "request_id": request_id,
            "details": redact_secrets(details or {}),
        }
    }


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        logger.warning(
            "application_error",
            extra={"request_id": _request_id(request), "error_code": exc.code.value},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_content(
                code=exc.code.value,
                message_ru=exc.message_ru,
                request_id=_request_id(request),
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_content(
                code=ErrorCode.CONFIGURATION_INVALID.value,
                message_ru="Запрос содержит недопустимые данные.",
                request_id=_request_id(request),
                details={"validation": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_error",
            extra={
                "request_id": _request_id(request),
                "error_code": ErrorCode.INTERNAL_ERROR.value,
            },
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content=error_content(
                code=ErrorCode.INTERNAL_ERROR.value,
                message_ru="Внутренняя ошибка приложения.",
                request_id=_request_id(request),
            ),
        )
