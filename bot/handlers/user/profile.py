"""
Хэндлеры студенческого профиля, достижений и лидерборда группы 1-КПД-3.

Отвечает за:
  1. Вывод личной карточки студента (/profile) с рангом, XP и ачивками
  2. Публикацию турнирной таблицы группы (/leaderboard) с пьедесталом
  3. Инлайн-кнопки перехода в Telegram Mini App для интерактивного просмотра
"""

import html

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from config import ALLOWED_USER_ID, MINIAPP_URL
from core.logger import get_logger
from services.classmates_auth import find_classmate_by_tg_id
from services.gamification import get_group_leaderboard, get_student_profile_by_fio
from services.gamification_registry import ACHIEVEMENTS_MAP

log = get_logger("user_profile")
router = Router()


def _build_miniapp_keyboard() -> InlineKeyboardMarkup:
    """Формирует клавиатуру с WebApp кнопкой для открытия рейтинга и ачивок."""
    url = MINIAPP_URL.rstrip("/") if MINIAPP_URL else "https://t.me"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏆 Открыть рейтинг в Mini App", web_app=WebAppInfo(url=url))],
        ]
    )


def _format_profile_achievements(ach_ids: list[str]) -> str:
    """Формирует компактный блок открытых ачивок студента."""
    if not ach_ids:
        return "<i>Достижения пока не разблокированы</i>"
    top_icons = [
        f"{ACHIEVEMENTS_MAP[aid].icon} {html.escape(ACHIEVEMENTS_MAP[aid].title)}"
        for aid in ach_ids[:4]
        if aid in ACHIEVEMENTS_MAP
    ]
    return "  •  ".join(top_icons)


def _format_profile_message(p) -> str:
    """Формирует HTML-текст персональной карточки студента с рангом и XP."""
    achs_text = _format_profile_achievements(p.unlocked_achievements)
    clean_fio = html.escape(p.fio)
    return (
        "👤 <b>СТУДЕНЧЕСКИЙ ПРОФИЛЬ • 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎓 <b>{clean_fio}</b>\n"
        f"Ранг: {p.rank_icon} <b>{html.escape(p.rank_name)}</b>\n"
        f"✨ Академический опыт: <b>{p.xp} XP</b>\n\n"
        f"📊 Посещаемость: <b>{p.attendance_pct}%</b> ({p.total_classes} пар)\n"
        f"✅ Присутствовал: <b>{p.present_count}</b>  •  ⏱ Опозданий: <b>{p.late_count}</b>\n"
        f"📋 По справке: <b>{p.excused_count}</b>  •  ⛔️ Прогулов: <b>{p.unexcused_count}</b>\n\n"
        f"🎖 <b>ОТКРЫТЫЕ ДОСТИЖЕНИЯ ({len(p.unlocked_achievements)}/80):</b>\n"
        f"{achs_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


@router.message(Command("profile", "me", "achievements"))
async def handle_profile_command(message: Message) -> None:
    """Отображает профиль студента, ранг и открытые достижения."""
    user = message.from_user
    if not user:
        return
    classmate = find_classmate_by_tg_id(user.id)
    raw_fio = (classmate.get("full_name") or classmate.get("name")) if classmate else None
    if user.id == ALLOWED_USER_ID:
        raw_fio = "Стрыгин Дмитрий"
    fio: str = str(raw_fio) if raw_fio else (user.full_name or "Студент")
    profile = await get_student_profile_by_fio(fio)
    if not profile:
        await message.answer(
            f"❌ Не удалось найти статистику студента <b>{html.escape(fio)}</b> в журнале группы.",
            parse_mode="HTML",
        )
        return
    text = _format_profile_message(profile)
    await message.answer(text=text, parse_mode="HTML", reply_markup=_build_miniapp_keyboard())


def _format_leaderboard_row(idx: int, p) -> str:
    """Формирует строку студента в турнирной таблице группы."""
    medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else f"{idx}."))
    clean_name = html.escape(p.short_fio)
    return f"{medal} <b>{clean_name}</b> — <b>{p.attendance_pct}%</b> ({p.rank_icon} {p.xp} XP)"


def _format_leaderboard_message(profiles: list) -> str:
    """Формирует текстовое сообщение с топом успеваемости группы."""
    total = len(profiles)
    pulse = round(sum(p.attendance_pct for p in profiles) / total, 1) if total else 0.0
    rows = [_format_leaderboard_row(i + 1, p) for i, p in enumerate(profiles[:10])]
    board_text = "\n".join(rows)
    return (
        "🏆 <b>ТУРНИРНАЯ ТАБЛИЦА • 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Всего: <b>{total}</b>  •  📈 Пульс группы: <b>{pulse}%</b>\n\n"
        f"{board_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 <i>Полная интерактивная таблица всех 26 студентов доступна в Mini App:</i>"
    )


@router.message(Command("leaderboard", "top", "rating"))
async def handle_leaderboard_command(message: Message) -> None:
    """Отображает топ-10 студентов группы 1-КПД-3."""
    profiles = await get_group_leaderboard()
    if not profiles:
        await message.answer("<i>Журнал посещаемости пока загружается...</i>", parse_mode="HTML")
        return
    text = _format_leaderboard_message(profiles)
    await message.answer(text=text, parse_mode="HTML", reply_markup=_build_miniapp_keyboard())
