"""
Pydantic-схемы для системной диагностики и управления кэшем.
"""

from typing import Dict
from pydantic import BaseModel, Field


class SystemInfoResponse(BaseModel):
    """Сводная диагностическая информация о сервисе para-api."""
    service: str = Field("para-api", description="Имя сервиса")
    version: str = Field("2.0.0", description="Версия API")
    timezone: str = Field(..., description="Текущий часовой пояс")
    server_time: str = Field(..., description="Текущее время сервера (ISO 8601)")
    redis_alive: bool = Field(..., description="Статус подключения к Redis")
    features: Dict[str, bool] = Field(default_factory=dict, description="Активные модули и протоколы")


class CacheFlushRequest(BaseModel):
    """Запрос на очистку ключей кэша в Redis."""
    pattern: str = Field("sched:*", description="Маска удаляемых ключей Redis", examples=["sched:*", "att:*"])


class CacheFlushResponse(BaseModel):
    """Результат очистки кэша."""
    status: str = Field(..., description="Статус операции")
    pattern: str = Field(..., description="Использованная маска")
    deleted_keys: int = Field(..., description="Число удалённых ключей")
