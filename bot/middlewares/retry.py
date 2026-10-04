"""
Middleware для прозрачной обработки Telegram flood control (429 RetryAfter).

При получении исключения TelegramRetryAfter приостанавливает выполнение
на указанный интервал retry_after и повторяет вызов хэндлера.
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import TelegramObject
from core.logger import get_logger

log = get_logger("retry_middleware")


class RetryAfterMiddleware(BaseMiddleware):
    """Перехватывает TelegramRetryAfter и повторяет запрос после паузы."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Исполняет хэндлер с retry при временном flood control."""
        for attempt in range(2):
            try:
                return await handler(event, data)
            except TelegramRetryAfter as e:
                log.warning(f"⚠️ Telegram flood control: пауза {e.retry_after}с (попытка {attempt + 1}/2)")
                await asyncio.sleep(e.retry_after)
            except Exception:
                raise
        return await handler(event, data)
