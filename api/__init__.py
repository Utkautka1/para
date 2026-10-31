"""
FastAPI-приложение para-api — фабрика приложения со Swagger UI и OpenAPI.

Зачем существует этот модуль:
Объединяет все 11 подсистем проекта, нативно регистрирует Pydantic-схемы
всех кодов ошибок и схемы аутентификации ApiKeyAuth / BearerAuth.
"""

import time
import uuid
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api.deps import verify_api_or_tester
from api.handlers import register_exception_handlers
from api.router.attendance import router as attendance_router
from api.router.birthdays import router as birthdays_router
from api.router.classmates import router as classmates_router
from api.router.exams import router as exams_router
from api.router.gamification import router as gamification_router
from api.router.health import router as health_router
from api.router.jaeger import router as jaeger_router
from api.router.metrics import router as metrics_router
from api.router.miniapp import router as miniapp_router
from api.router.pulse import router as pulse_router
from api.router.schedule import router as schedule_router
from api.router.solver import router as solver_router
from api.router.subscribers import router as subscribers_router
from api.router.system import router as system_router
from api.router.teachers import router as teachers_router
from api.schemas.errors import COMMON_API_RESPONSES
from config import (
    GZIP_MIN_SIZE_BYTES,
    SWAGGER_SERVERS_DESCRIPTION,
    SWAGGER_SERVERS_URL,
)
from core.logger import set_trace_id
from core.metrics import normalize_http_method, record_http_request
from core.telemetry import format_trace_id, setup_telemetry


def _register_routers(app: FastAPI) -> None:
    """
    Регистрирует все подсистемные роутеры в основном экземпляре приложения FastAPI.

    Подключает эндпоинты расписания, экзаменов, посещаемости, трейсинга, документации.

    Ничего не возвращает.
    """
    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(schedule_router)
    app.include_router(exams_router)
    app.include_router(teachers_router)
    app.include_router(attendance_router)
    app.include_router(classmates_router)
    app.include_router(birthdays_router)
    app.include_router(solver_router)
    app.include_router(subscribers_router)
    app.include_router(system_router)
    app.include_router(miniapp_router)
    app.include_router(pulse_router)
    app.include_router(jaeger_router)
    app.include_router(gamification_router)


def _configure_openapi_servers(schema: dict[str, Any]) -> None:
    """
    Устанавливает относительный URL сервера без публичных IP и абсолютных хостов.

    Защищает от раскрытия внутреннего IP-адреса и обеспечивает работу за реверс-прокси.

    Ничего не возвращает; мутирует переданный словарь схемы.
    """
    schema["servers"] = [{"url": SWAGGER_SERVERS_URL, "description": SWAGGER_SERVERS_DESCRIPTION}]


PUBLIC_API_PATHS = {
    "/health",
    "/metrics",
    "/miniapp",
    "/miniapp/auth",
    "/miniapp/action",
    "/miniapp/status",
    "/gamification/achievements",
    "/gamification/ranks",
}


def _apply_security_to_operations(schema: dict[str, Any]) -> None:
    """Применяет требования безопасности к операциям API, исключая публичные пути."""
    for path, methods in schema.get("paths", {}).items():
        for m, op in methods.items():
            if m.lower() in {"get", "post", "put", "delete", "patch"}:
                op["security"] = [] if path in PUBLIC_API_PATHS else [{"ApiKeyAuth": []}, {"BearerAuth": []}]


def _configure_openapi_security(schema: dict[str, Any]) -> None:
    """Настраивает декларации ApiKeyAuth / BearerAuth и публичные пути в схеме."""
    schema.setdefault("components", {})["securitySchemes"] = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key", "description": "API-ключ тестера"},
        "BearerAuth": {"type": "http", "scheme": "bearer", "description": "Bearer токен тестера"},
    }
    _apply_security_to_operations(schema)
    schema.pop("security", None)


def _custom_openapi_schema(app: FastAPI) -> dict[str, Any]:
    """Генерирует чистую OpenAPI 3.1 спецификацию приложения с кэшированием."""
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="para-api",
        version="2.9.0",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        routes=app.routes,
    )
    _configure_openapi_security(schema)
    _configure_openapi_servers(schema)
    app.openapi_schema = schema
    return app.openapi_schema


def _register_protected_docs(app: FastAPI) -> None:
    """Регистрирует защищенную отдачу спецификации и Swagger UI для тестеров."""

    @app.get("/openapi.json", include_in_schema=False, dependencies=[Depends(verify_api_or_tester)])
    async def get_openapi_spec() -> JSONResponse:
        return JSONResponse(content=_custom_openapi_schema(app))

    @app.get("/docs", include_in_schema=False, dependencies=[Depends(verify_api_or_tester)])
    async def get_docs_swagger() -> Any:
        return get_swagger_ui_html(openapi_url="/openapi.json", title="para-api — Swagger UI Documentation")


def _route_template(request: Request) -> str:
    """
    Возвращает шаблон маршрута ('/attendance/student/{fio}') для лейбла метрик.

    Сырой путь в лейбле — неограниченная кардинальность (каждый случайный URL
    навсегда занимает память) и утечка ФИО/tg_id из путей в /metrics.

    Возвращает шаблон пути или 'unmatched' для запросов мимо роутов.
    """
    route = request.scope.get("route")
    return getattr(route, "path", None) or "unmatched"


def _register_observability_middleware(app: FastAPI) -> None:
    """Регистрирует HTTP middleware для замера времени ответа и внедрения trace_id."""

    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or format_trace_id() or uuid.uuid4().hex[:12]
        set_trace_id(req_id)
        request.state.trace_id = req_id

        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        record_http_request(
            normalize_http_method(request.method), _route_template(request), response.status_code, duration
        )
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Trace-ID"] = format_trace_id() or req_id
        return response


def _init_fastapi_instance() -> FastAPI:
    """Создает базовый экземпляр FastAPI с отключенными публичными эндпоинтами документации."""
    return FastAPI(
        title="para-api",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        version="2.9.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        responses=COMMON_API_RESPONSES,
    )


def create_app() -> FastAPI:
    """Фабрика создания высокоскоростного FastAPI приложения с закрытыми docs-эндпоинтами."""
    setup_telemetry("para-api")
    app = _init_fastapi_instance()
    FastAPIInstrumentor.instrument_app(app)
    _register_observability_middleware(app)
    app.add_middleware(GZipMiddleware, minimum_size=GZIP_MIN_SIZE_BYTES)
    _register_routers(app)
    _register_protected_docs(app)
    register_exception_handlers(app)
    app.openapi = lambda: _custom_openapi_schema(app)
    return app
