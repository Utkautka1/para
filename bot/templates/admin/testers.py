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


def format_testers_text(testers: list[int]) -> str:
    """
    Формирует информационный текст экрана управления доступом к Swagger UI.

    Выводит внешний URL портала документации и список Telegram ID тестеров.
    Используется в диалоге управления тестировщиками в панели старосты.

    Возвращает отформатированную HTML-строку.
    """

    items = "\n".join(f"  • <code>{uid}</code>" for uid in testers) or "  <i>(Список пуст)</i>"
    web_url = f"<code>{SWAGGER_URL}</code>" if SWAGGER_URL else "<i>(Не задан)</i>"

    return (
        "🧪 <b>УПРАВЛЕНИЕ SWAGGER UI И ТЕСТЕРАМИ</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Swagger UI:</b> {web_url}\n\n"
        f"👥 <b>Авторизованные тестеры ({len(testers)}):</b>\n{items}\n\n"
        "💡 <i>Нажмите кнопку ниже, чтобы открыть веб-интерфейс Swagger UI.</i>"
    )


def get_swagger_buttons() -> list[InlineKeyboardButton]:
    """
    Формирует инлайн-кнопки для перехода в Swagger UI в браузере и Mini App.

    Проверяет наличие сконфигурированных адресов перед добавлением кнопок.
    Защищает от отправки кнопок с пустыми недействительными ссылками.

    Возвращает список объектов InlineKeyboardButton.
    """

    btns = []
    if SWAGGER_URL:
        btns.append(InlineKeyboardButton(text="🚀 Открыть Swagger UI", url=SWAGGER_URL))

    if MINIAPP_URL.startswith("https://"):
        btns.append(InlineKeyboardButton(text="📱 Mini App", web_app=WebAppInfo(url=MINIAPP_URL)))

    return btns


def get_testers_management_kb(testers: list[int]) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру управления списком тестеров Swagger UI.

    Включает кнопки запуска портала, добавления тестера и постраничного удаления.
    Ограничивает единовременный вывод первыми шестью пользователями.

    Возвращает объект InlineKeyboardMarkup.
    """

    rows: list = []
    top_btns = get_swagger_buttons()
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
