"""
FastAPI-приложение para-api — фабрика приложения со Swagger UI и OpenAPI.
"""

from fastapi import FastAPI

from api.router.exams import router as exams_router
from api.router.health import router as health_router
from api.router.miniapp import router as miniapp_router
from api.router.schedule import router as schedule_router
from api.router.teachers import router as teachers_router


def create_app() -> FastAPI:
    """Собирает FastAPI-приложение с роутерами, Swagger UI и OpenAPI."""
    app = FastAPI(
        title="para-api",
        description="Высокопроизводительный сервис расписания КТМУ (gRPC + OpenAPI + Swagger UI)",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        swagger_ui_parameters={"persistAuthorization": True, "displayRequestDuration": True},
    )
    app.include_router(health_router)
    app.include_router(schedule_router)
    app.include_router(exams_router)
    app.include_router(teachers_router)
    app.include_router(miniapp_router)
    return app
