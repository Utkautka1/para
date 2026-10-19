"""
FastAPI-приложение para-api — фабрика приложения со Swagger UI и OpenAPI.

Зачем существует этот модуль:
Объединяет все 11 подсистем проекта, нативно регистрирует Pydantic-схемы
всех кодов ошибок и схемы аутентификации ApiKeyAuth / BearerAuth.
"""

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse

from api.deps import verify_api_or_tester
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
from config import (
    GZIP_MIN_SIZE_BYTES,
    SWAGGER_SERVERS_DESCRIPTION,
    SWAGGER_SERVERS_URL,
)


def _register_routers(app: FastAPI) -> None:
    """
    Регистрирует все подсистемные роутеры в основном экземпляре приложения FastAPI.

    Подключает эндпоинты расписания, экзаменов, посещаемости, одногруппников, дней рождения.

    Ничего не возвращает.
    """
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


def _configure_openapi_servers(schema: dict[str, Any]) -> None:
    """
    Устанавливает относительный URL сервера без публичных IP и абсолютных хостов.

    Защищает от раскрытия внутреннего IP-адреса и обеспечивает работу за реверс-прокси.

    Ничего не возвращает; мутирует переданный словарь схемы.
    """
    schema["servers"] = [{"url": SWAGGER_SERVERS_URL, "description": SWAGGER_SERVERS_DESCRIPTION}]


def _configure_openapi_security(schema: dict[str, Any]) -> None:
    """
    Настраивает декларации ApiKeyAuth / BearerAuth и публичные пути в схеме.

    Исключает публичные пути здоровья и авторизации из требований токенов.

    Ничего не возвращает; мутирует переданный словарь схемы.
    """
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


def _custom_openapi_schema(app: FastAPI) -> dict[str, Any]:
    """
    Генерирует чистую OpenAPI 3.1 спецификацию приложения с кэшированием.

    Создает схему один раз и сохраняет в атрибут app.openapi_schema.

    Возвращает словарь схемы OpenAPI.
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="para-api",
        version="2.0.0",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        routes=app.routes,
    )

    _configure_openapi_security(schema)
    _configure_openapi_servers(schema)
    app.openapi_schema = schema

    return app.openapi_schema


def _register_protected_docs(app: FastAPI) -> None:
    """
    Регистрирует защищенную отдачу спецификации и редирект на Mini App.

    Закрывает доступ к схеме от неавторизованных пользователей через зависимость.

    Ничего не возвращает.
    """

    @app.get("/openapi.json", include_in_schema=False, dependencies=[Depends(verify_api_or_tester)])
    async def get_openapi_spec() -> JSONResponse:
        """Отдает схему OpenAPI только авторизованным тестировщикам."""
        return JSONResponse(content=_custom_openapi_schema(app))

    @app.get("/docs", include_in_schema=False)
    async def get_docs_portal() -> RedirectResponse:
        """Перенаправляет пользователя в защищенный Mini App портал."""
        return RedirectResponse(url="/miniapp")


def create_app() -> FastAPI:
    """
    Фабрика создания высокоскоростного FastAPI приложения с закрытыми docs-эндпоинтами.

    Настраивает сжатие GZip, маршрутизацию, обработчики ошибок и схему OpenAPI.

    Возвращает сконфигурированный экземпляр FastAPI.
    """
    app = FastAPI(
        title="para-api",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        version="2.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        responses=COMMON_API_RESPONSES,
    )

    app.add_middleware(GZipMiddleware, minimum_size=GZIP_MIN_SIZE_BYTES)
    _register_routers(app)
    _register_protected_docs(app)
    register_exception_handlers(app)
    app.openapi = lambda: _custom_openapi_schema(app)

    return app
