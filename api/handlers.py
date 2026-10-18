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
    """
    Обрабатывает стандартные HTTPException и возвращает унифицированный JSON.

    Обеспечивает единую схему ошибки ErrorDetail для клиентских приложений и Swagger.

    Возвращает объект JSONResponse с соответствующим HTTP статус-кодом.
    """
    payload = ErrorDetail(detail=str(exc.detail), code=f"HTTP_{exc.status_code}")

    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Обрабатывает ошибки валидации параметров Pydantic (HTTP 422).

    Логирует детали несоответствия входных типов и структуры запроса.

    Возвращает объект JSONResponse с кодом 422 и списком ошибок валидации.
    """
    log.warning(f"⚠️ Ошибка валидации {request.method} {request.url.path}: {exc.errors()}")
    status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.errors(), "code": "VALIDATION_ERROR"},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Перехватывает любые непредвиденные сбои, логирует стек и возвращает HTTP 500.

    Скрывает внутренние подробности реализации от клиента, фиксируя стек в логах.

    Возвращает JSONResponse со статусом 500 и кодом INTERNAL_SERVER_ERROR.
    """
    log.error(f"❌ Критический сбой при вызове {request.method} {request.url.path}: {exc}", exc_info=exc)
    payload = ErrorDetail(detail="Внутренняя ошибка сервера", code="INTERNAL_SERVER_ERROR")

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """
    Регистрирует все централизованные обработчики исключений в приложении.

    Подключает перехватчики HTTPException, RequestValidationError и базового Exception.

    Ничего не возвращает.
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
