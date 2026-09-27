"""
Healthcheck роутер — GET /health.

Не требует авторизации — используется Docker healthcheck
для проверки жизнеспособности контейнера para-api.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Ответ healthcheck."""
    status: str


@router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    """Простая проверка жизнеспособности API-сервиса."""
    return HealthResponse(status="ok")
