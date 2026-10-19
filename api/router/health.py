"""
Healthcheck роутер — GET /health.

Не требует авторизации — используется Docker healthcheck
для проверки жизнеспособности контейнера para-api.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Модель ответа проверки жизнеспособности сервиса para-api."""

    status: str


@router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    """
    Выполняет быструю проверку доступности и жизнеспособности сервиса API.

    Используется оркестратором Docker и внешними балансировщиками без авторизации.
    Возвращает статический статус 'ok' при нормальной работе event loop.

    Возвращает объект HealthResponse со статусом 'ok'.
    """

    return HealthResponse(status="ok")
