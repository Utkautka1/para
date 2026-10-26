"""
Pydantic-схемы для Telegram Mini App и управления тестерами.

Определяют форматы запросов аутентификации initData, ответов с сессиями
и структур управления списком тестировщиков API.
"""

from pydantic import BaseModel, Field


class MiniappAuthRequest(BaseModel):
    """Запрос авторизации из Telegram Mini App или с ПК разработчика."""

    init_data: str | None = Field(None, description="Сырая строка Telegram.WebApp.initData")
    api_key: str | None = Field(None, description="API-ключ или пароль разработчика для входа с ПК")


class MiniappAuthResponse(BaseModel):
    """Ответ успешной авторизации тестера."""

    status: str = "ok"
    user_id: int
    first_name: str | None = None
    username: str | None = None
    redirect_url: str = "/docs"


class MiniappCheckResponse(BaseModel):
    """Статус текущей сессии тестера."""

    authenticated: bool
    user_id: int | None = None
    is_tester: bool


class TesterItemResponse(BaseModel):
    """Информация об одном тестере."""

    user_id: int
    is_admin: bool


class TesterListResponse(BaseModel):
    """Список всех активных тестеров API."""

    count: int
    testers: list[TesterItemResponse]
