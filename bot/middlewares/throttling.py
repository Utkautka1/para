"""
Middleware для защиты от частого нажатия инлайн-кнопок (Debounce / Throttling).

Предотвращает лавины параллельных обработчиков при повторных кликах
нетерпеливых пользователей по инлайн-кнопкам расписания и админки.
"""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from config import (
    THROTTLING_DEFAULT_COOLDOWN,
    THROTTLING_HEAVY_COOLDOWN,
    THROTTLING_NAV_COOLDOWN,
)
from core.logger import get_logger

log = get_logger("throttle_middleware")

# Кулдауны для категорий действий (в секундах)
HEAVY_COOLDOWN = THROTTLING_HEAVY_COOLDOWN
NAV_COOLDOWN = THROTTLING_NAV_COOLDOWN
DEFAULT_COOLDOWN = THROTTLING_DEFAULT_COOLDOWN


def _determine_cooldown(cb_data: str) -> float:
    """
    Определяет необходимый интервал кулдауна по префиксу callback_data.

    Назначает увеличенный таймаут для тяжелых сетевых синхронизаций
    и минимальный таймаут для быстрой навигации по расписанию.

    Возвращает значение кулдауна в секундах (float).
    """

    if cb_data in ("sched:refresh", "admin:sync"):
        return HEAVY_COOLDOWN

    if cb_data.startswith("sched:"):
        return NAV_COOLDOWN

    return DEFAULT_COOLDOWN


class CallbackThrottleMiddleware(BaseMiddleware):
    """Предотвращает спам-клики по инлайн-кнопкам бота."""

    def __init__(self) -> None:
        """
        Инициализирует локальное состояние трекинга времени кликов.

        Хранит словарь соответствия 'user_id:callback_data' -> timestamp.
        Работает в оперативной памяти процесса бота.
        """

        self._last_clicks: dict[str, float] = {}

    def _cleanup_old_entries(self, now: float) -> None:
        """
        Очищает устаревшие записи, предотвращая утечку оперативной памяти.

        Срабатывает только при превышении порога в 1000 активных записей.
        Удаляет ключи старше двойного максимального кулдауна.

        Ничего не возвращает (модифицирует словарь self._last_clicks).
        """

        if len(self._last_clicks) > 1000:
            threshold = HEAVY_COOLDOWN * 2
            self._last_clicks = {
                k: v for k, v in self._last_clicks.items()
                if now - v < threshold
            }

    async def _handle_callback_throttle(
        self, event: CallbackQuery, now: float
    ) -> bool:
        """
        Проверяет интервал времени между кликами и отправляет всплывающее предупреждение.

        Если прошло меньше времени кулдауна, показывает пользователю toast-уведомление.
        Защищает сервис от одновременных тяжелых запросов при спаме кнопками.

        Возвращает True, если клик разрешен, иначе False при троттлинге.
        """

        uid = event.from_user.id if event.from_user else 0
        cb_data = event.data or ""
        key = f"{uid}:{cb_data}"
        cooldown = _determine_cooldown(cb_data)
        last_time = self._last_clicks.get(key, 0.0)

        if now - last_time < cooldown:
            log.debug(f"Дребезг клика от {uid} ({cb_data}), кулдаун {cooldown}с")
            await event.answer("⏳ Подождите секунду...", show_alert=False)
            return False

        self._last_clicks[key] = now
        self._cleanup_old_entries(now)

        return True

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Перехватывает входящие события и отсекает частые нажатия инлайн-кнопок.

        Пропускает без задержки обычные сообщения и не связанные с callback события.
        Защищает граф хэндлеров aiogram от состояния гонки.

        Возвращает результат вызова следующего хэндлера цепочки или None.
        """

        if isinstance(event, CallbackQuery) and not await self._handle_callback_throttle(event, time.time()):
            return None

        return await handler(event, data)

