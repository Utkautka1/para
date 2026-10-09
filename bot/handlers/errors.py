"""
Глобальный обработчик необработанных исключений диспетчера aiogram.

Перехватывает системные сбои в хэндлерах, гасит анимацию ожидания callback-кнопок
и информирует пользователя о временной ошибке вместо зависания интерфейса.
"""

from aiogram import Router
from aiogram.types import ErrorEvent

from core.logger import get_logger

log = get_logger("error_handler")
router = Router()


@router.error()
async def global_error_handler(event: ErrorEvent) -> bool:
    """Перехватывает исключения хэндлеров, логирует и уведомляет пользователя."""
    log.error(f"❌ Необработанная ошибка в хэндлере: {event.exception}")
    update = event.update
    if update.callback_query:
        try:
            await update.callback_query.answer("⚠️ Временный сбой сервиса. Попробуйте снова.", show_alert=True)
        except Exception as e:  # noqa: BLE001
            log.debug(f"Не удалось ответить на сбойный callback: {e}")
    elif update.message:
        try:
            await update.message.answer("⚠️ Произошла ошибка. Пожалуйста, повторите попытку через пару секунд.")
        except Exception as e:  # noqa: BLE001
            log.debug(f"Не удалось отправить уведомление об ошибке: {e}")
    return True
