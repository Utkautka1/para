"""
FastAPI-приложение para-api — фабрика приложения со Swagger UI и OpenAPI.

Зачем существует этот модуль:
Объединяет все 11 подсистем проекта, нативно регистрирует Pydantic-схемы
всех кодов ошибок и схемы аутентификации ApiKeyAuth / BearerAuth.
"""

from typing import Any, Dict
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.handlers import register_exception_handlers
from api.router.attendance import router as attendance_router
from api.router.birthdays import router as birthdays_router
from api.router.classmates import router as classmates_router
from api.router.exams import router as exams_router
from api.router.health import router as health_router
from api.router.miniapp import router as miniapp_router
from api.router.schedule import router as schedule_router
from api.router.solver import router as solver_router
from api.router.subscribers import router as subscribers_router
from api.router.system import router as system_router
from api.router.teachers import router as teachers_router
from api.schemas.errors import COMMON_API_RESPONSES


def _register_routers(app: FastAPI) -> None:
    """Регистрирует все подсистемные роутеры в приложении."""
    app.include_router(health_router)
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


def _configure_openapi_security(schema: Dict[str, Any]) -> None:
    """Настраивает декларации ApiKeyAuth / BearerAuth и публичные пути в схеме."""
    schema.setdefault("components", {})["securitySchemes"] = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key", "description": "API-ключ тестера"},
        "BearerAuth": {"type": "http", "scheme": "bearer", "description": "Bearer токен тестера"},
    }
    public_paths = {"/health", "/miniapp", "/miniapp/auth", "/miniapp/status"}
    for path, methods in schema.get("paths", {}).items():
        for m, op in methods.items():
            if m.lower() in {"get", "post", "put", "delete", "patch"}:
                op["security"] = [] if path in public_paths else [{"ApiKeyAuth": []}, {"BearerAuth": []}]
    schema.pop("security", None)


def _custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Генерирует чистую OpenAPI 3.1 спецификацию приложения с кэшированием."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="para-api",
        version="2.0.0",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        routes=app.routes,
    )
    _configure_openapi_security(schema)
    app.openapi_schema = schema
    return app.openapi_schema


def create_app() -> FastAPI:
    """Фабрика создания экземпляра приложения FastAPI со всеми кодами ошибок."""
    app = FastAPI(
        title="para-api",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        responses=COMMON_API_RESPONSES,
        swagger_ui_parameters={"persistAuthorization": True, "displayRequestDuration": True},
    )
    _register_routers(app)
    register_exception_handlers(app)
    app.openapi = lambda: _custom_openapi_schema(app)
    return app
