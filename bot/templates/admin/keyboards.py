"""
Модуль аккуратных Inline-клавиатур личной Панели Администратора.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def _build_action_rows() -> list:
    """Формирует основные кнопки управления топиками и синхронизацией со стилями."""
    return [
        [
            InlineKeyboardButton(text="📝 Отметить посещаемость", callback_data="att:menu", style="success")
        ],
        [
            InlineKeyboardButton(text="🔄 Синхронизировать всё", callback_data="admin:sync", style="primary"),
            InlineKeyboardButton(text="📊 Статус и Кэш", callback_data="admin:status", style="primary")
        ],
        [InlineKeyboardButton(text="👨‍🏫 Ручные ссылки преподавателей", callback_data="admin:list_custom", style="primary")],
        [
            InlineKeyboardButton(text="📢 Обновить топик", callback_data="admin:force_topic", style="success"),
            InlineKeyboardButton(text="🔁 Пересоздать", callback_data="admin:recreate_topic", style="danger")
        ],
        [
            InlineKeyboardButton(text="📑 Обновить экзамены", callback_data="admin:force_exam", style="success"),
            InlineKeyboardButton(text="🔁 Пересоздать", callback_data="admin:recreate_exam", style="danger")
        ],
        [
            InlineKeyboardButton(text="📊 Реестр посещаемости", callback_data="admin:force_att_topic", style="success"),
            InlineKeyboardButton(text="🔁 Пересоздать", callback_data="admin:recreate_att_topic", style="danger")
        ],
        [InlineKeyboardButton(text="◀️ Вернуться к расписанию", callback_data="sched:today", style="primary")]
    ]


def get_admin_main_kb() -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру главного экрана админки со стилями кнопок.

    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(inline_keyboard=_build_action_rows())
