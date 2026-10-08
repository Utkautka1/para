"""
Модуль аккуратных Inline-клавиатур личной Панели Администратора.

Содержит клавиатуры для управления синхронизацией, топиками,
а также списком тестировщиков и запуском Swagger UI Mini App.
"""

from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from config import MINIAPP_URL


def _build_topic_action_rows() -> list:
    """Формирует кнопки принудительного обновления и пересоздания топиков."""
    return [
        [
            InlineKeyboardButton(text="📢 Обновить топик", callback_data="admin:force_topic", style="success"),
            InlineKeyboardButton(text="🔁 Пересоздать", callback_data="admin:recreate_topic", style="danger"),
        ],
        [
            InlineKeyboardButton(text="📑 Обновить экзамены", callback_data="admin:force_exam", style="success"),
            InlineKeyboardButton(text="🔁 Пересоздать", callback_data="admin:recreate_exam", style="danger"),
        ],
        [
            InlineKeyboardButton(text="📊 Реестр посещаемости", callback_data="admin:force_att_topic", style="success"),
            InlineKeyboardButton(text="🔁 Пересоздать", callback_data="admin:recreate_att_topic", style="danger"),
        ],
        [InlineKeyboardButton(text="◀️ Вернуться к расписанию", callback_data="sched:today", style="primary")],
    ]


def _build_action_rows() -> list:
    """Формирует основные кнопки управления топиками и синхронизацией со стилями."""
    rows = [
        [InlineKeyboardButton(text="📝 Отметить посещаемость", callback_data="att:menu", style="success")],
        [
            InlineKeyboardButton(text="🔄 Синхронизировать всё", callback_data="admin:sync", style="primary"),
            InlineKeyboardButton(text="📊 Статус и Кэш", callback_data="admin:status", style="primary"),
        ],
        [InlineKeyboardButton(text="🧪 Swagger UI & Тестеры API", callback_data="admin:testers", style="primary")],
        [InlineKeyboardButton(text="👨‍🏫 Ручные ссылки преподавателей", callback_data="admin:list_custom", style="primary")],
        [InlineKeyboardButton(text="👥 Привязать студента по ID", callback_data="admin:bind_student", style="primary")],
    ]
    rows.extend(_build_topic_action_rows())
    return rows


def get_admin_main_kb() -> InlineKeyboardMarkup:
    """Генерирует инлайн-клавиатуру главного экрана админки со стилями кнопок."""
    return InlineKeyboardMarkup(inline_keyboard=_build_action_rows())


def get_swagger_launch_btn() -> InlineKeyboardButton:
    """Формирует кнопку запуска Mini App или информационную ссылку."""
    if MINIAPP_URL.startswith("https://"):
        return InlineKeyboardButton(text="🚀 Открыть Swagger UI (Mini App)", web_app=WebAppInfo(url=MINIAPP_URL))
    return InlineKeyboardButton(text="🚀 Ссылка на Swagger UI", callback_data="admin:show_swagger_link")


def get_testers_management_kb(testers: List[int]) -> InlineKeyboardMarkup:
    """Генерирует клавиатуру управления списком тестеров Swagger UI."""
    rows: list = [[get_swagger_launch_btn()]]
    rows.append([
        InlineKeyboardButton(text="➕ Добавить тестера", callback_data="admin:add_tester", style="success"),
        InlineKeyboardButton(text="🔄 Обновить список", callback_data="admin:testers", style="primary"),
    ])
    for uid in testers[:6]:
        rows.append([
            InlineKeyboardButton(text=f"👤 ID: {uid}", callback_data=f"admin:view_tester:{uid}"),
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"admin:del_tester:{uid}", style="danger"),
        ])
    rows.append([InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:menu", style="primary")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
