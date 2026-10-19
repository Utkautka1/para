"""
Middleware распределенного трейсинга OpenTelemetry для входящих событий Telegram.

Создает корневой спан (root span) для каждого входящего нажатия кнопки (CallbackQuery)
или текстового сообщения (Message). Записывает атрибуты пользователя, типа действия
и связывает идентификатор trace_id с контекстом текущей корутины asyncio.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from core.logger import get_logger
from core.telemetry import trace_span

log = get_logger("tracing_middleware")


def _extract_callback_attrs(query: CallbackQuery) -> tuple[str, dict[str, Any]]:
    """
    Формирует имя спана и словарь телеметрии для нажатия инлайн-кнопки.

    Возвращает кортеж из имени спана и словаря атрибутов OpenTelemetry.
    """
    prefix = query.data.split(":")[0] if query.data else "empty"
    span_name = f"telegram.callback:{prefix}"
    attrs: dict[str, Any] = {
        "telegram.event_type": "callback_query",
        "telegram.callback_data": query.data or "",
        "telegram.user_id": query.from_user.id if query.from_user else 0,
        "telegram.chat_id": query.message.chat.id if query.message else 0,
    }
    return span_name, attrs


def _extract_message_attrs(message: Message) -> tuple[str, dict[str, Any]]:
    """
    Формирует имя спана и словарь телеметрии для входящего сообщения.

    Возвращает кортеж из имени спана и словаря атрибутов OpenTelemetry.
    """
    cmd = message.text.split()[0][:20] if message.text else message.content_type
    span_name = f"telegram.message:{cmd}"
    attrs: dict[str, Any] = {
        "telegram.event_type": "message",
        "telegram.content_type": message.content_type,
        "telegram.user_id": message.from_user.id if message.from_user else 0,
        "telegram.chat_id": message.chat.id,
    }
    return span_name, attrs


class TracingMiddleware(BaseMiddleware):
    """Сквозной трейсинг событий бота: создает родительский спан и передает trace_id."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Перехватывает событие Telegram и оборачивает вызов хэндлера в спан."""
        if isinstance(event, CallbackQuery):
            name, attrs = _extract_callback_attrs(event)
        elif isinstance(event, Message):
            name, attrs = _extract_message_attrs(event)
        else:
            name, attrs = "telegram.event", {"telegram.event_type": type(event).__name__}

        async with trace_span(name, attributes=attrs):
            return await handler(event, data)
