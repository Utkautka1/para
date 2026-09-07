"""
Отдельный публичный роутер для копирования Zoom-реквизитов участниками топика.

Позволяет любому одногруппнику нажимать на кнопки скопировать ID/Код
без прохождения закрытого AuthFilter.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery

public_router = Router()


@public_router.callback_query(F.data.startswith("copy:"))
async def cb_public_copy_value(callback: CallbackQuery) -> None:
    """
    Публичный обработчик копирования ID и паролей Zoom.

    :param callback: CallbackQuery
    """
    val = callback.data.split("copy:", 1)[1]
    await callback.answer(f"Реквизиты: {val}", show_alert=False)


