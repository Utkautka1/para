"""
Модуль аккуратных Inline-клавиатур личной Панели Администратора.

Содержит клавиатуры для управления синхронизацией, топиками,
а также списком тестировщиков и запуском Swagger UI Mini App.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot.templates.admin.gamification import GameAdminCallback
from config import MINIAPP_URL


def _build_topic_action_rows() -> list:
    """
    Формирует ряды кнопок принудительного обновления и пересоздания топиков супергруппы.

    Предоставляет старосте кнопки для топика расписания, экзаменов и посещаемости.
    Кнопки пересоздания помечены стилем 'danger' для предупреждения о сбросе ID.

    Возвращает список рядов InlineKeyboardButton.
    """

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
    """
    Формирует основную матрицу кнопок панели управления администратора.

    Включает быстрый вход в посещаемость, полную синхронизацию, тестеров и топики.
    Служит структурным шаблоном для главного меню команды /admin.

    Возвращает полный список рядов кнопок админки.
    """

    rows = [
        [InlineKeyboardButton(text="📝 Отметить посещаемость", callback_data="att:menu", style="success")],
        [
            InlineKeyboardButton(text="🔄 Синхронизировать всё", callback_data="admin:sync", style="primary"),
            InlineKeyboardButton(text="📊 Статус и Кэш", callback_data="admin:status", style="primary"),
        ],
        [InlineKeyboardButton(text="🧪 Swagger UI & Тестеры API", callback_data="admin:testers", style="primary")],
        [InlineKeyboardButton(text="🏆 Ачивки и очки", callback_data=GameAdminCallback(action="list").pack())],
        [
            InlineKeyboardButton(
                text="👨‍🏫 Ручные ссылки преподавателей", callback_data="admin:list_custom", style="primary"
            )
        ],
        [InlineKeyboardButton(text="👥 Привязать студента по ID", callback_data="admin:bind_student", style="primary")],
    ]
    rows.extend(_build_topic_action_rows())

    return rows


def get_admin_main_kb() -> InlineKeyboardMarkup:
    """
    Генерирует главную инлайн-клавиатуру панели управления старосты.

    Оборачивает список рядов действий в объект разметки Telegram.
    Применяется в хэндлере /admin и колбэке 'admin:menu'.

    Возвращает готовый объект InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(inline_keyboard=_build_action_rows())


def get_swagger_launch_btn() -> InlineKeyboardButton:
    """
    Формирует кнопку запуска Telegram Mini App с порталом Swagger UI.

    Использует WebAppInfo при наличии валидного HTTPS URL в конфигурации.
    При локальном HTTP окружении возвращает колбэк-ссылку.

    Возвращает объект InlineKeyboardButton.
    """

    if MINIAPP_URL.startswith("https://"):
        return InlineKeyboardButton(text="🚀 Открыть веб-портал (Mini App)", web_app=WebAppInfo(url=MINIAPP_URL))

    return InlineKeyboardButton(text="🚀 Ссылка на веб-портал", callback_data="admin:show_swagger_link")


def get_testers_management_kb(testers: list[int]) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру управления списком разрешенных тестеров API.

    Отображает до 6 тестеров с кнопками быстрого удаления и кнопку добавления.
    Включает кнопку возврата в главное меню панели администратора.

    Возвращает InlineKeyboardMarkup управления тестерами.
    """

    rows: list = [[get_swagger_launch_btn()]]
    rows.append(
        [
            InlineKeyboardButton(text="➕ Добавить тестера", callback_data="admin:add_tester", style="success"),
            InlineKeyboardButton(text="🔄 Обновить список", callback_data="admin:testers", style="primary"),
        ]
    )
    for uid in testers[:6]:
        rows.append(
            [
                InlineKeyboardButton(text=f"👤 ID: {uid}", callback_data=f"admin:view_tester:{uid}"),
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"admin:del_tester:{uid}", style="danger"),
            ]
        )
    rows.append([InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:menu", style="primary")])

    return InlineKeyboardMarkup(inline_keyboard=rows)
