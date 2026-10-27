"""
Тексты, стейты и клавиатуры для управления тестерами и Swagger UI Mini App.

Изолирует шаблоны отображения и разметку интерфейса от логики хэндлеров
в соответствии с канонической структурой проекта.
"""

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import MINIAPP_URL, SWAGGER_URL


class AddTesterState(StatesGroup):
    """FSM-стейт ожидания ввода Telegram ID для добавления тестера."""

    waiting_for_user_id = State()


def format_testers_text(testers: list[int], admin_key: str = "") -> str:
    """
    Формирует информационный текст экрана управления доступом к Swagger UI.

    Выводит внешний URL портала документации, ключ доступа и список Telegram ID тестеров.
    Используется в диалоге управления тестировщиками в панели старосты.

    Возвращает отформатированную HTML-строку.
    """

    items = "\n".join(f"  • <code>{uid}</code>" for uid in testers) or "  <i>(Список пуст)</i>"
    doc_url = (
        f"<code>{SWAGGER_URL}?key={admin_key}</code>"
        if admin_key
        else (f"<code>{SWAGGER_URL}</code>" if SWAGGER_URL else "<i>(Не задан)</i>")
    )
    key_line = f"🔑 <b>Ваш мастер-ключ (Admin):</b>\n<code>{admin_key}</code>\n\n" if admin_key else ""

    return (
        "🧪 <b>УПРАВЛЕНИЕ SWAGGER UI И ТЕСТЕРАМИ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{key_line}"
        f"🌐 <b>Swagger UI:</b> {doc_url}\n\n"
        f"👥 <b>Авторизованные тестеры ({len(testers)}):</b>\n{items}\n\n"
        "💡 <i>Используйте кнопки ниже для быстрого входа в Mini App или Swagger UI.</i>"
    )


def get_swagger_buttons(admin_key: str = "") -> list[InlineKeyboardButton]:
    """
    Формирует инлайн-кнопки для перехода в Mini App и прямого открытия Swagger UI.

    При наличии ключа добавляет его в query-параметры для бесшовной авторизации.

    Возвращает список инлайн-кнопок перехода в веб-порталы.
    """
    buttons: list[InlineKeyboardButton] = []
    if MINIAPP_URL.startswith("https://"):
        app_url = f"{MINIAPP_URL}?key={admin_key}" if admin_key else MINIAPP_URL
        buttons.append(InlineKeyboardButton(text="📱 Mini App", web_app=WebAppInfo(url=app_url)))

    if SWAGGER_URL.startswith("http"):
        doc_url = f"{SWAGGER_URL}?key={admin_key}" if admin_key else SWAGGER_URL
        buttons.append(InlineKeyboardButton(text="🌐 Swagger UI", url=doc_url))

    return buttons


def get_testers_management_kb(testers: list[int], admin_key: str = "") -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру управления списком тестеров Swagger UI.

    Включает кнопки запуска портала, добавления тестера и постраничного удаления.
    Ограничивает единовременный вывод первыми шестью пользователями.

    Возвращает объект InlineKeyboardMarkup.
    """

    rows: list = []
    top_btns = get_swagger_buttons(admin_key)
    if top_btns:
        rows.append(top_btns)

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
