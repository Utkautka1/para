"""
Pydantic-схемы для системной диагностики и управления кэшем.
"""

from pydantic import BaseModel, Field


class SystemInfoResponse(BaseModel):
    """Сводная диагностическая информация о сервисе para-api."""

    service: str = Field("para-api", description="Имя сервиса")
    version: str = Field("2.0.0", description="Версия API")
    timezone: str = Field(..., description="Текущий часовой пояс")
    server_time: str = Field(..., description="Текущее время сервера (ISO 8601)")
    redis_alive: bool = Field(..., description="Статус подключения к Redis")
    features: dict[str, bool] = Field(default_factory=dict, description="Активные модули и протоколы")


class CacheFlushRequest(BaseModel):
    """Запрос на очистку ключей кэша в Redis."""

    pattern: str = Field("sched:*", description="Маска удаляемых ключей Redis", examples=["sched:*", "att:*"])


class CacheFlushResponse(BaseModel):
    """Результат очистки кэша."""

    status: str = Field(..., description="Статус операции")
    pattern: str = Field(..., description="Использованная маска")
    deleted_keys: int = Field(..., description="Число удалённых ключей")


class IncidentItem(BaseModel):
    """Запись системного инцидента."""

    id: int = Field(..., description="ID инцидента")
    incident_type: str = Field(..., description="Тип инцидента")
    severity: str = Field(..., description="Критичность")
    title: str = Field(..., description="Заголовок")
    description: str = Field(..., description="Детали инцидента")
    trace_id: str | None = Field(None, description="Трассировочный ID")
    resolved: bool = Field(False, description="Флаг решения")
    created_at: str = Field(..., description="Время фиксации")


class IncidentListResponse(BaseModel):
    """Список зафиксированных системных инцидентов."""

    count: int = Field(..., description="Количество инцидентов")
    incidents: list[IncidentItem] = Field(default_factory=list, description="Список записей")


class BackupTriggerResponse(BaseModel):
    """Ответ запуска процесса резервного копирования."""

    status: str = Field(..., description="Статус запуска")
    message: str = Field(..., description="Детальное сообщение")
