"""
Отдельный публичный роутер для копирования Zoom-реквизитов участниками топика.

Позволяет любому одногруппнику нажимать на кнопки скопировать ID/Код
без прохождения закрытого AuthFilter.
"""

from aiogram import F, Router
from aiogram.types import CallbackQuery

from core.logger import get_logger

log = get_logger("public_copy")

public_router = Router()


@public_router.callback_query(F.data.startswith("copy:"))
async def cb_public_copy_value(callback: CallbackQuery) -> None:
    """
    Отображает всплывающее окно с реквизитами конференции Zoom для копирования.

    Извлекает значение из callback_data и отдает во всплывающем alert клиенту Telegram.
    Доступен всем участникам беседы без жесткой авторизации по реестру.

    Ничего не возвращает.
    """

    val = callback.data.split("copy:", 1)[1]
    user_id = callback.from_user.id if callback.from_user else 0
    log.info("Публичный копир реквизитов вызван user_id=%s: %s", user_id, val)

    await callback.answer(f"Скопировано: {val}", show_alert=True)
