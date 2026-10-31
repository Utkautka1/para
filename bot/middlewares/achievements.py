"""
Middleware учёта активности для накопительных ачивок.

Регистрируется как outer-middleware: срабатывает на каждом апдейте, даже если
ни один хэндлер его не обработал. Это нужно для чата группы — обычные сообщения
одногруппников бот не обрабатывает, но «Болтун», «Мемолог» и «Коллоквиум»
считают именно их. Бот — админ группы, поэтому получает их, несмотря на privacy mode.

Учёт идёт в фоне и никогда не задерживает и не ломает обработку апдейта.
"""

import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import TOPIC_CHAT_ID
from core.logger import get_logger
from services.achievement_events import on_group_message, on_interaction

log = get_logger("achievement_middleware")

# Ссылки на фоновые задачи: без них event loop может собрать задачу сборщиком мусора
_BACKGROUND: set[asyncio.Task[None]] = set()


def _spawn(coro: Coroutine[Any, Any, None]) -> None:
    """Запускает учёт активности в фоне и держит ссылку до завершения задачи."""
    task = asyncio.create_task(coro)
    _BACKGROUND.add(task)
    task.add_done_callback(_BACKGROUND.discard)


def _activity_for(event: TelegramObject) -> Coroutine[Any, Any, None] | None:
    """
    Выбирает, как учесть апдейт: действие в ЛС/кнопка или сообщение в чате группы.

    Возвращает корутину учёта или None, если апдейт не относится к ачивкам.
    """
    if isinstance(event, CallbackQuery) and event.from_user:
        return on_interaction(event.from_user, event.bot)
    if not isinstance(event, Message) or not event.from_user:
        return None
    if event.chat.type == "private":
        return on_interaction(event.from_user, event.bot)
    if event.chat.id == TOPIC_CHAT_ID:
        return on_group_message(event, event.bot)
    return None


class AchievementActivityMiddleware(BaseMiddleware):
    """Считает действия одногруппников в боте и чате группы для ачивок."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Ставит учёт активности в фон и передаёт апдейт дальше без задержки."""
        activity = _activity_for(event)
        if activity is not None:
            _spawn(activity)
        return await handler(event, data)
