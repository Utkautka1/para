"""
Точка входа сервиса para-api (FastAPI + Uvicorn).

Единая точка доступа к данным расписания, экзаменов и преподавателей.
Все эндпоинты (кроме /health) защищены X-API-Key.
API доступен только внутри Docker-сети, порт наружу не публикуется.
"""

import uvicorn
from fastapi import FastAPI

from api.router.exams import router as exams_router
from api.router.health import router as health_router
from api.router.schedule import router as schedule_router
from api.router.teachers import router as teachers_router
from core.logger import get_logger

log = get_logger("api_main")


def create_app() -> FastAPI:
    """Собирает FastAPI-приложение с роутерами и метаданными."""
    app = FastAPI(
        title="para-api",
        description="Внутренний API парсинга расписания КТМУ",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.include_router(health_router)
    app.include_router(schedule_router)
    app.include_router(exams_router)
    app.include_router(teachers_router)
    return app


app = create_app()


if __name__ == "__main__":
    log.info("=" * 60)
    log.info("ЗАПУСК Internal API (para-api)")
    log.info("  Порт: 8000 | Docs: отключены | Auth: X-API-Key")
    log.info("=" * 60)
    api_host = os.getenv("API_HOST", "0.0.0.0")  # nosec B104
    uvicorn.run(app, host=api_host, port=8000, log_level="warning")

