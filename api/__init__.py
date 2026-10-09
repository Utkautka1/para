"""
FastAPI-приложение para-api — фабрика приложения со Swagger UI и OpenAPI.

Объединяет все 11 подсистем проекта (расписание, экзамены, преподаватели,
посещаемость, одногруппники, дни рождения, AI solver, подписчики, система, miniapp).
"""

from typing import Any, Dict
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

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


_HTTP_ERROR_RESPONSES: Dict[str, Dict[str, Any]] = {
    "400": {"description": "Некорректный запрос (Bad Request)"},
    "401": {"description": "Неавторизован: недействительный API-ключ / токен (Unauthorized)"},
    "403": {"description": "Доступ запрещен: требуются права администратора (Forbidden)"},
    "404": {"description": "Запрашиваемый ресурс не найден (Not Found)"},
    "405": {"description": "HTTP-метод не поддерживается (Method Not Allowed)"},
    "408": {"description": "Время ожидания запроса истекло (Request Timeout)"},
    "422": {"description": "Ошибка валидации параметров запроса (Validation Error)"},
    "429": {"description": "Превышен лимит запросов (Too Many Requests / Rate Limit)"},
    "500": {"description": "Внутренняя ошибка сервера (Internal Server Error)"},
    "502": {"description": "Ошибочный шлюз: туннель или внешний сервис недоступен (Bad Gateway)"},
    "503": {"description": "Сервис временно недоступен: сбой Redis / БД (Service Unavailable)"},
    "504": {"description": "Время ожидания внешнего сервиса истекло (Gateway Timeout)"},
}


def _inject_route_security_and_errors(schema: Dict[str, Any]) -> None:
    """Внедряет схемы авторизации и полную документацию всех кодов ошибок во все маршруты."""
    public_paths = {"/health", "/miniapp", "/miniapp/auth", "/miniapp/status"}
    for path, methods in schema.get("paths", {}).items():
        for m, op in methods.items():
            if m.lower() in {"get", "post", "put", "delete", "patch"}:
                op["security"] = [] if path in public_paths else [{"ApiKeyAuth": []}, {"BearerAuth": []}]
                resps = op.setdefault("responses", {})
                for code, desc in _HTTP_ERROR_RESPONSES.items():
                    if code not in resps:
                        resps[code] = desc


def _custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Генерирует полную OpenAPI 3.1 схему со схемами безопасности и кодами ошибок."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="para-api", version="2.0.0",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        routes=app.routes,
    )
    schema.setdefault("components", {})["securitySchemes"] = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key", "description": "API-ключ тестера"},
        "BearerAuth": {"type": "http", "scheme": "bearer", "description": "Bearer токен тестера"},
    }
    schema.pop("security", None)
    _inject_route_security_and_errors(schema)
    app.openapi_schema = schema
    return app.openapi_schema


def create_app() -> FastAPI:
    """Фабрика создания экземпляра приложения FastAPI."""
    app = FastAPI(
        title="para-api",
        description="Высокопроизводительный сервис КТМУ (gRPC + OpenAPI + Swagger UI)",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={"persistAuthorization": True, "displayRequestDuration": True},
    )
    _register_routers(app)
    app.openapi = lambda: _custom_openapi_schema(app)
    return app
