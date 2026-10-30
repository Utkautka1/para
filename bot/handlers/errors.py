"""
Глобальный обработчик необработанных исключений диспетчера aiogram.

Перехватывает системные сбои в хэндлерах, гасит анимацию ожидания callback-кнопок
и информирует пользователя о временной ошибке вместо зависания интерфейса.
"""

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ErrorEvent

from core.logger import get_logger

log = get_logger("error_handler")
router = Router()


async def _notify_callback_error(cb) -> None:
    """
    Отправляет всплывающее alert-уведомление при сбое внутри CallbackQuery.

    Гасит бесконечную анимацию ожидания нажатия на инлайн-кнопке Telegram.
    Подавляет ошибки вторичной отправки при истечении срока валидности callback query.

    Ничего не возвращает.
    """

    try:
        await cb.answer("⚠️ Временный сбой сервиса. Попробуйте снова.", show_alert=True)
    except Exception as e:
        log.debug("Не удалось ответить на сбойный callback: %s", e)


async def _notify_message_error(msg) -> None:
    """
    Отправляет текстовое сообщение пользователю при сбое внутри Message хэндлера.

    Информирует о временной ошибке вместо молчаливого игнорирования команды.
    Перехватывает возможные сбои блокировки бота пользователем.

    Ничего не возвращает.
    """

    try:
        await msg.answer("⚠️ Произошла ошибка. Пожалуйста, повторите попытку через пару секунд.")
    except Exception as e:
        log.debug("Не удалось отправить уведомление об ошибке: %s", e)


async def _dispatch_error_alert(exc: Exception) -> None:
    """Асинхронно отправляет алерт о сбое хэндлера в Fatal топик."""
    try:
        import html

        from db.sqlite.models import IncidentSeverity
        from services.alerting import send_admin_alert

        err_type = type(exc).__name__
        err_msg = str(exc) or err_type
        await send_admin_alert(
            incident_type="UNHANDLED_EXCEPTION",
            severity=IncidentSeverity.CRITICAL,
            title=f"Необработанная ошибка ({err_type})",
            description=f"<code>{html.escape(err_msg[:500])}</code>",
        )
    except Exception as e:
        log.debug("Не удалось отправить алерт об ошибке: %s", e)


def _is_stale_callback(exc: Exception) -> bool:
    """
    Проверяет, что Telegram отверг ответ на устаревшее нажатие кнопки.

    Так бывает после перезапуска бота: нажатия, накопленные за время простоя,
    приходят позже 15-секундного окна ответа. Это не сбой кода, а следствие простоя.
    """
    return isinstance(exc, TelegramBadRequest) and "query is too old" in str(exc)


@router.error()
async def global_error_handler(event: ErrorEvent) -> bool:
    """
    Перехватывает любые непредвиденные исключения в жизненном цикле aiogram.

    Логирует стек ошибки с уровнем ERROR и отправляет пользователю уведомление.
    Предотвращает падение процесса и зависание клиентского интерфейса Telegram.

    Возвращает True для подтверждения успешной обработки события сбоя.
    """
    if _is_stale_callback(event.exception):
        log.warning("⚠️  Ответ на устаревшее нажатие кнопки отклонён Telegram (бот был недоступен)")
        return True

    log.error("❌ Необработанная ошибка в хэндлере: %s", event.exception)
    await _dispatch_error_alert(event.exception)
    update = event.update

    if update.callback_query:
        await _notify_callback_error(update.callback_query)
    elif update.message:
        await _notify_message_error(update.message)

    return True
