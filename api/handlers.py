"""
Централизованные обработчики исключений (Exception Handlers) для para-api.

Зачем существует этот модуль:
Перехватывает все исключения приложения, обеспечивает единый формат JSON-ответов
(совместимый с Pydantic ErrorDetail) и логирует критические ошибки.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.schemas.errors import ErrorDetail
from core.logger import get_logger

log = get_logger("api_exceptions")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Обрабатывает стандартные HTTPException и возвращает унифицированный JSON."""
    payload = ErrorDetail(detail=str(exc.detail), code=f"HTTP_{exc.status_code}")
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Обрабатывает ошибки валидации параметров Pydantic (HTTP 422)."""
    log.warning(f"⚠️ Ошибка валидации {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "code": "VALIDATION_ERROR"}
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Перехватывает любые непредвиденные сбои, логирует стек и возвращает HTTP 500."""
    log.error(f"❌ Критический сбой при вызове {request.method} {request.url.path}: {exc}", exc_info=True)
    payload = ErrorDetail(detail="Внутренняя ошибка сервера", code="INTERNAL_SERVER_ERROR")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все централизованные обработчики исключений в приложении."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
