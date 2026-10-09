"""
Pydantic-схемы для управления подписчиками уведомлений о парах.
"""


from pydantic import BaseModel, Field


class SubscribersListResponse(BaseModel):
    """Список всех подписчиков на утренние и 10-минутные уведомления."""
    count: int = Field(..., description="Общее число подписчиков")
    subscribers: list[int] = Field(default_factory=list, description="Список Telegram Chat ID")


class SubscriberCountResponse(BaseModel):
    """Общее количество активных подписчиков бота."""
    count: int = Field(..., description="Количество подписчиков")


class SubscriberStatusResponse(BaseModel):
    """Статус подписки пользователя."""
    chat_id: int = Field(..., description="Telegram Chat ID пользователя")
    is_subscribed: bool = Field(..., description="Активна ли подписка на уведомления")


class SubscriberActionResponse(BaseModel):
    """Результат изменения статуса подписки."""
    chat_id: int = Field(..., description="Telegram Chat ID")
    is_subscribed: bool = Field(..., description="Новый статус подписки")
    message: str = Field(..., description="Результат операции")
