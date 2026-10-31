"""
Тексты, колбэки и клавиатуры управления ачивками и очками в админ-панели.

Экраны:
  1. Список студентов (алфавит) с их очками гильдии
  2. Карточка студента: XP, очки, бонусы, кнопки ±
  3. Категории ачивок → ачивки категории с переключателем ✅ / ➖
"""

import html

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.gamification_models import AchievementCategory, StudentProfile
from services.gamification_registry import ACHIEVEMENTS_MAP, SECRET_IDS

# Предел ручного ввода — защита от опечатки с лишними нулями
MAX_MANUAL_AMOUNT = 1_000_000

# Шаги кнопок ± для XP и очков гильдии
BONUS_STEPS = (-1000, -100, -10, 10, 100, 1000)

# Секретные ачивки показываются отдельной «категорией», их нет в публичных категориях
SECRET_CATEGORY = "secret"

CATEGORY_TITLES: dict[str, str] = {
    AchievementCategory.ATTENDANCE: "📅 Посещаемость",
    AchievementCategory.PUNCTUALITY: "⏰ Пунктуальность",
    AchievementCategory.BOT_INTERACTION: "🤖 Бот",
    AchievementCategory.AI_HOMEWORK: "🧠 ИИ и ДЗ",
    AchievementCategory.STUDENT_LIFE: "🎓 Студ. жизнь",
    AchievementCategory.SOCIAL: "💬 Социалка",
    AchievementCategory.EASTER_EGGS: "🥚 Пасхалки",
    AchievementCategory.MASTERY: "👑 Мастерство",
    SECRET_CATEGORY: "🤫 Секретные",
}


class GameAdminCallback(CallbackData, prefix="gma"):
    """
    Колбэк раздела «Ачивки и очки»: действие, индекс студента и параметр.

    Составной параметр разделяется «|»: «:» — разделитель самого CallbackData.
    """

    action: str
    idx: int = -1
    value: str = ""


class GameAdminState(StatesGroup):
    """Ожидание числа для бонуса XP или очков гильдии."""

    waiting_for_amount = State()


def _cb(action: str, idx: int = -1, value: str = "") -> str:
    """Упаковывает колбэк раздела в строку callback_data."""
    return GameAdminCallback(action=action, idx=idx, value=value).pack()


students_text = (
    "🏆 <b>АЧИВКИ И ОЧКИ</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "Выберите студента. В скобках — очки гильдии.\n\n"
    "<i>Каждое изменение приходит студенту уведомлением.</i>"
)


def students_ikb(students: list[StudentProfile]) -> InlineKeyboardMarkup:
    """
    Список студентов по алфавиту, по два в ряд
    - Фамилия И. (очки)
    - ◀️ Назад в админку
    :param students: профили в алфавитном порядке
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for idx, p in enumerate(students):
        builder.button(text=f"{p.short_fio} ({p.guild_points})", callback_data=_cb("card", idx))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:menu", style="primary"))
    return builder.as_markup()


def student_card_text(p: StudentProfile, xp_bonus: int, guild_bonus: int) -> str:
    """Карточка студента: уровень, XP, очки гильдии, бонусы и ачивки."""
    level = p.xp // 100 + 1
    return (
        f"👤 <b>{html.escape(p.fio)}</b>\n"
        f"{p.rank_icon} {html.escape(p.rank_name)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ XP: <b>{p.xp}</b> (уровень {level})\n"
        f"⚔️ Очки гильдии: <b>{p.guild_points}</b>\n"
        f"🎁 Бонус XP: <b>{xp_bonus:+d}</b> • бонус очков: <b>{guild_bonus:+d}</b>\n"
        f"🏆 Ачивки: <b>{len(p.unlocked_achievements)} / {len(ACHIEVEMENTS_MAP)}</b>\n"
        f"📊 П {p.present_count} • О {p.late_count} • У {p.excused_count} • Н {p.unexcused_count}"
    )


def _bonus_row(idx: int, kind: str) -> list[InlineKeyboardButton]:
    """Ряд кнопок ± для одного вида бонуса."""
    return [
        InlineKeyboardButton(text=f"{step:+d}", callback_data=_cb("bonus", idx, f"{kind}|{step}"))
        for step in BONUS_STEPS
    ]


def student_card_ikb(idx: int) -> InlineKeyboardMarkup:
    """
    Карточка студента
    - ✨ XP: −1000 … +1000
    - ⚔️ Очки гильдии: −1000 … +1000
    - 🏆 Ачивки • 🔁 Обнулить бонусы
    - ◀️ К списку
    :param idx: индекс студента в алфавитном списке
    :return: InlineKeyboardMarkup
    """
    rows = [
        [InlineKeyboardButton(text="✨ XP — вписать число", callback_data=_cb("ask", idx, "xp"))],
        _bonus_row(idx, "xp"),
        [InlineKeyboardButton(text="⚔️ Очки гильдии — вписать число", callback_data=_cb("ask", idx, "guild"))],
        _bonus_row(idx, "guild"),
        [
            InlineKeyboardButton(text="🏆 Ачивки", callback_data=_cb("cats", idx), style="success"),
            InlineKeyboardButton(text="🔁 Обнулить бонусы", callback_data=_cb("reset", idx), style="danger"),
        ],
        [InlineKeyboardButton(text="◀️ К списку", callback_data=_cb("list"), style="primary")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def categories_ikb(idx: int, unlocked: list[str]) -> InlineKeyboardMarkup:
    """
    Категории ачивок с числом открытых
    - 📅 Посещаемость (3/10) …
    - ◀️ К студенту
    :param idx: индекс студента
    :param unlocked: открытые ачивки студента
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for category, title in CATEGORY_TITLES.items():
        ids = category_achievements(category)
        owned = sum(1 for aid in ids if aid in unlocked)
        builder.button(text=f"{title} ({owned}/{len(ids)})", callback_data=_cb("cat", idx, category))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="◀️ К студенту", callback_data=_cb("card", idx), style="primary"))
    return builder.as_markup()


def category_achievements(category: str) -> list[str]:
    """Возвращает id ачивок категории; секретные — отдельной категорией."""
    if category == SECRET_CATEGORY:
        return sorted(SECRET_IDS)
    return [aid for aid, a in ACHIEVEMENTS_MAP.items() if a.category == category and aid not in SECRET_IDS]


def category_ikb(idx: int, category: str, unlocked: list[str]) -> InlineKeyboardMarkup:
    """
    Ачивки категории с переключателем
    - ✅ Название (+XP) — выдана, нажатие снимает
    - ➖ Название (+XP) — не выдана, нажатие выдаёт
    - ◀️ К категориям
    :param idx: индекс студента
    :param category: категория ачивок
    :param unlocked: открытые ачивки студента
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for aid in category_achievements(category):
        ach = ACHIEVEMENTS_MAP[aid]
        mark = "✅" if aid in unlocked else "➖"
        text = f"{mark} {ach.icon} {ach.title} (+{ach.xp_reward})"
        builder.button(text=text, callback_data=_cb("toggle", idx, f"{category}|{aid}"))
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ К категориям", callback_data=_cb("cats", idx), style="primary"))
    return builder.as_markup()


def category_text(p: StudentProfile, category: str) -> str:
    """Заголовок экрана категории ачивок студента."""
    return (
        f"🏆 <b>{CATEGORY_TITLES[category]}</b> — {html.escape(p.short_fio)}\n\n"
        "<i>✅ — выдана (нажмите, чтобы снять), ➖ — нет (нажмите, чтобы выдать)</i>"
    )


BONUS_LABELS = {"xp": "✨ XP", "guild": "⚔️ очков гильдии"}


def ask_amount_text(student: str, kind: str) -> str:
    """Просьба вписать число для бонуса студента."""
    return (
        f"✍️ <b>{BONUS_LABELS[kind]}</b> для <b>{html.escape(student)}</b>\n\n"
        "Впишите число:\n"
        "• <code>500</code> или <code>+500</code> — прибавить\n"
        "• <code>-30</code> — отнять\n"
        "• <code>=1000</code> — выставить бонус ровно"
    )


def ask_amount_ikb(idx: int) -> InlineKeyboardMarkup:
    """
    Запрос числа
    - ◀️ Отмена (возврат к карточке)
    :param idx: индекс студента
    :return: InlineKeyboardMarkup
    """
    button = InlineKeyboardButton(text="◀️ Отмена", callback_data=_cb("card", idx), style="primary")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


incorrect_amount_text = (
    "⚠️ <b>Не понял число.</b>\n\n"
    "Примеры: <code>500</code>, <code>-30</code>, <code>=1000</code> "
    f"(не больше {MAX_MANUAL_AMOUNT:,} по модулю). Впишите ещё раз."
)


def parse_amount(text: str | None) -> tuple[bool, int] | None:
    """
    Разбирает ввод старосты: '=N' — выставить бонус ровно, иначе — прибавить N.

    Возвращает (выставить_ровно, число) или None, если ввод не распознан.
    """
    raw = (text or "").strip().replace(" ", "")
    exact = raw.startswith("=")
    number = raw[1:] if exact else raw
    try:
        value = int(number)
    except ValueError:
        return None
    if abs(value) > MAX_MANUAL_AMOUNT or (value == 0 and not exact):
        return None
    return exact, value


student_not_found_text = "⚠️ Студент не найден — список обновился. Откройте его заново."
