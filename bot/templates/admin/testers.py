"""
Тексты, стейты и клавиатуры для управления тестерами и Swagger UI Mini App.

Изолирует шаблоны отображения и разметку интерфейса от логики хэндлеров
в соответствии с канонической структурой проекта.
"""


from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import MINIAPP_URL


class AddTesterState(StatesGroup):
    """FSM-стейт ожидания ввода Telegram ID для добавления тестера."""
    waiting_for_user_id = State()


def format_testers_text(testers: list[int]) -> str:
    """Формирует HTML-текст со списком текущих тестировщиков."""
    items = "\n".join(f"  • <code>{uid}</code>" for uid in testers) or "  <i>(Список пуст)</i>"
    url_info = f"<code>{MINIAPP_URL}</code>" if MINIAPP_URL else "<i>(Не задан в .env)</i>"
    return (
        "🧪 <b>УПРАВЛЕНИЕ ТЕСТЕРАМИ SWAGGER UI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Mini App URL:</b> {url_info}\n\n"
        f"👥 <b>Авторизованные тестеры ({len(testers)}):</b>\n{items}\n\n"
        "💡 <i>Тестеры могут запускать Mini App и вызывать все методы API.</i>"
    )


def get_swagger_launch_btn() -> InlineKeyboardButton:
    """Формирует кнопку запуска Mini App или информационную ссылку."""
    if MINIAPP_URL.startswith("https://"):
        return InlineKeyboardButton(text="🚀 Открыть Swagger UI (Mini App)", web_app=WebAppInfo(url=MINIAPP_URL))
    return InlineKeyboardButton(text="🚀 Ссылка на Swagger UI", callback_data="admin:show_swagger_link")


def get_testers_management_kb(testers: list[int]) -> InlineKeyboardMarkup:
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
