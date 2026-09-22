"""
Модуль аккуратных Inline-клавиатур личной Панели Администратора.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_main_kb() -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру главного экрана админки.

    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Синхронизировать всё", callback_data="admin:sync"),
                InlineKeyboardButton(text="📊 Статус и Кэш", callback_data="admin:status")
            ],
            [
                InlineKeyboardButton(text="👨‍🏫 Ручные ссылки преподавателей", callback_data="admin:list_custom")
            ],
            [
                InlineKeyboardButton(text="📢 Обновить топик сейчас", callback_data="admin:force_topic"),
                InlineKeyboardButton(text="🔁 Пересоздать", callback_data="admin:recreate_topic")
            ],
            [
                InlineKeyboardButton(text="◀️ Вернуться к расписанию", callback_data="sched:today")
            ]
        ]
    )
