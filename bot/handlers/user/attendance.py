"""
Хэндлеры просмотра персональной посещаемости студента (/my_attendance).

Позволяет студентам группы 1-КПД-3:
  1. Узнать свои суммарные отметки П/О/У/Н за всё время в ЛС бота
  2. Видеть детальную помесячную разбивку (Сентябрь, Октябрь, ...)
  3. Отслеживать персональный процент посещаемости пар
  4. Обновлять сводку в топике по кнопке att_topic:refresh
"""

import html
from typing import Any

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.filters.auth import ClassmateAuthFilter
from core.background import spawn
from core.logger import get_logger
from services.achievement_events import on_attendance_view
from services.attendance_stats import fetch_all_time_attendance, find_student_attendance
from services.attendance_topic_updater import sync_attendance_topic_message
from services.classmates_auth import find_classmate_by_tg_id, process_user_auth

log = get_logger("user_attendance")
router = Router()
router.message.filter(ClassmateAuthFilter())
router.callback_query.filter(ClassmateAuthFilter())


def _calculate_attendance_percent(p: int, o: int, u: int, total: int) -> str:
    """
    Вычисляет процент посещаемости студента с учетом уважительных причин.

    Считает присутствие (П), опоздания (О) и уважительные причины (У) как посещенные.
    При нулевом общем количестве занятий возвращает 100.0%.

    Возвращает строку с процентом посещаемости с точностью до десятых.
    """

    if total <= 0:
        return "100.0%"

    valid_classes = p + o + u
    pct = (valid_classes / total) * 100.0

    return f"{pct:.1f}%"


def _format_personal_month_breakdown(months: dict[str, dict[str, int]]) -> str:
    """
    Формирует текстовый блок детальной помесячной статистики посещаемости.

    Итерируется по отсортированным месяцам и форматирует счетчики отметок.
    Возвращает заглушку курсивом при отсутствии данных за учебные месяцы.

    Возвращает отформатированную HTML-строку.
    """

    if not months:
        return "<i>Нет данных по месяцам</i>"

    lines = []
    for m_name, counts in sorted(months.items()):
        p = counts.get("П", 0)
        o = counts.get("О", 0)
        u = counts.get("У", 0)
        n = counts.get("Н", 0)
        lines.append(f"• <b>{m_name}:</b> ✅ {p} | ⏰ {o} | 📋 {u} | ❌ {n}")

    return "\n".join(lines)


def _format_card_header_and_summary(fio: str, p: int, o: int, u: int, n: int) -> str:
    """Формирует шапку и сводный блок отметок персональной карточки."""
    return (
        f"👤 <b>ТВОЯ ПОСЕЩАЕМОСТЬ: {html.escape(fio)}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Сводка за всё время:</b>\n"
        f"• ✅ Присутствовал: <b>{p}</b> пар\n"
        f"• ⏰ Опоздания: <b>{o}</b>\n"
        f"• 📋 Уважительная причина: <b>{u}</b>\n"
        f"• ❌ Пропуски (Н): <b>{n}</b>\n\n"
    )


def format_personal_attendance_card(fio: str, student_data: dict[str, Any]) -> str:
    """Формирует персональную HTML-карточку посещаемости конкретного студента."""
    tot = student_data.get("total", {})
    p, o, u, n = tot.get("П", 0), tot.get("О", 0), tot.get("У", 0), tot.get("Н", 0)
    total_classes = p + o + u + n
    pct_str = _calculate_attendance_percent(p, o, u, total_classes)
    months = _format_personal_month_breakdown(student_data.get("months", {}))
    summary = _format_card_header_and_summary(fio, p, o, u, n)
    return (
        f"{summary}📈 <b>Процент посещения:</b> <b>{pct_str}</b> (из {total_classes} пар)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📅 <b>По месяцам:</b>\n{months}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💡 <i>Если отметка неверна — обратись к старосте.</i>"
    )


def get_personal_attendance_kb() -> InlineKeyboardMarkup:
    """
    Возвращает инлайн-клавиатуру персонального экрана посещаемости студента.

    Содержит кнопку принудительного обновления данных из облачной таблицы.
    Позволяет студенту быстро увидеть свежие изменения после отметки старосты.

    Возвращает объект InlineKeyboardMarkup.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔄 Обновить мои данные", callback_data="att:my_refresh")]]
    )


def _resolve_student_fio(user, student: dict[str, Any] | None = None) -> str | None:
    """
    Определяет официальное ФИО студента по реестру одногруппников группы.

    Приоритетно использует сопоставление из объекта авторизации или поиск по TG ID.
    Если соответствие не найдено, использует имя профиля пользователя в Telegram.

    Возвращает строку с ФИО или None.
    """

    if student and student.get("full_name"):
        return student["full_name"]

    uid = user.id if user else 0
    st = find_classmate_by_tg_id(uid)
    if st and st.get("full_name"):
        return st["full_name"]

    return user.full_name if user else None


async def _respond_personal_attendance(message: Message, fio: str, data: dict[str, Any]) -> None:
    """Отправляет карточку посещаемости и фиксирует ачивку самопроверки."""
    spawn(on_attendance_view(message.from_user, message.bot))
    text = format_personal_attendance_card(data.get("fio", fio), data)
    await message.answer(text, reply_markup=get_personal_attendance_kb())


@router.message(Command("my_attendance"))
async def cmd_my_attendance(message: Message) -> None:
    """Отображает персональную карточку посещаемости авторизованного студента."""
    if message.chat.type != "private":
        await message.reply("🔒 <i>Персональная посещаемость доступна только в личных сообщениях.</i>")
        return
    is_auth, _, student = process_user_auth(message.from_user)
    if not is_auth:
        await message.answer("⛔ Доступ ограничен. Бот работает только для студентов группы 1-КПД-3.")
        return
    fio = _resolve_student_fio(message.from_user, student)
    stats = await fetch_all_time_attendance(force_refresh=False)
    data = find_student_attendance(stats, fio) if fio else None
    if not data:
        await message.answer(f"⚠️ Данные для <b>{html.escape(fio or 'студента')}</b> не найдены в журнале.")
        return
    await _respond_personal_attendance(message, str(fio), data)


@router.callback_query(F.data == "att:my_refresh")
async def cb_my_attendance_refresh(callback: CallbackQuery) -> None:
    """Обновляет персональную карточку посещаемости студента в ЛС по кнопке."""
    await callback.answer("⏳ Обновляю данные из журнала...")
    fio = _resolve_student_fio(callback.from_user)
    stats = await fetch_all_time_attendance(force_refresh=True)
    data = find_student_attendance(stats, fio) if fio else None
    if not data:
        await callback.answer("⚠️ Данные не найдены", show_alert=True)
        return

    spawn(on_attendance_view(callback.from_user, callback.bot))
    text = format_personal_attendance_card(data.get("fio", fio), data)
    try:
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_personal_attendance_kb())
    except TelegramBadRequest as e:
        log.debug("Обновление посещаемости пропущено: %s", e)


@router.callback_query(F.data == "att_topic:refresh")
async def cb_att_topic_refresh(callback: CallbackQuery) -> None:
    """
    Синхронизирует сводный реестр посещаемости по кнопке в топике Telegram.

    Сбрасывает кэш Яндекс Документов и пересчитывает общую таблицу пропусков.
    Отображает всплывающий alert с результатом синхронизации.

    Ничего не возвращает.
    """

    await callback.answer("⏳ Загружаю свежие данные из Яндекс Документов...", show_alert=False)
    success = await sync_attendance_topic_message(force_refresh=True)
    ans = "✅ Сводка посещаемости успешно обновлена!" if success else "⚠️ Ошибка синхронизации"

    await callback.answer(ans, show_alert=True)
