"""
Хэндлеры управления процессом отметки посещаемости.

Обрабатывает команду /attendance и все инлайн-кнопки (att:*)
исключительно для старосты (ALLOWED_USER_ID) и замстаросты (DEPUTY_USER_ID).
"""

import asyncio
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.filters.auth import AttendanceAuthFilter
from bot.templates.admin.attendance import (
    format_student_card,
    format_summary_text,
    get_lesson_select_kb,
    get_student_poll_kb,
)
from config import TIMEZONE
from core.api_client import get_api_schedule_for_date
from core.logger import get_logger
from services.attendance_manager import (
    calculate_summary_stats,
    clear_session,
    commit_session_to_table,
    create_attendance_session,
    get_active_session,
    mark_all_remaining_present,
    record_student_mark,
    step_back,
)

log = get_logger("attendance_handlers")

router = Router()
router.message.filter(AttendanceAuthFilter())
router.callback_query.filter(AttendanceAuthFilter())


async def _async_commit_and_update(
    message: Message | None, session, stats: dict[str, int]
) -> None:
    """Фоновая асинхронная запись в Яндекс Таблицу с обновлением статуса."""
    success = await commit_session_to_table(session)
    if not message:
        return
    badge = (
        "\n\n✅ <i>Успешно сохранено в Яндекс Таблицу</i>"
        if success else
        "\n\n⚠️ <i>Не удалось сохранить в Яндекс. Данные сохранены в Redis (/attendance).</i>"
    )
    try:
        await message.edit_text(format_summary_text(session, stats) + badge)
    except Exception as e:
        log.debug(f"Не удалось обновить статус выгрузки посещаемости: {e}")


async def _instant_topic_sync(session) -> None:
    """Мгновенно применяет оптимистичные отметки и обновляет топик в Telegram."""
    try:
        from services.attendance_stats import apply_session_optimistic_update
        from services.attendance_topic_updater import sync_attendance_topic_message
        await apply_session_optimistic_update(session)
        await sync_attendance_topic_message(force_refresh=False)
        log.info(f"⚡️ Мгновенное обновление топика для пары {session.lesson_num} выполнено")
    except Exception as e:
        log.error(f"Ошибка мгновенного обновления топика посещаемости: {e}")


async def finish_and_notify(cb: CallbackQuery, session) -> None:
    """Мгновенно отображает сводку старосте и запускает параллельную синхронизацию."""
    stats = calculate_summary_stats(session.marks)
    text_saving = (
        format_summary_text(session, stats)
        + "\n\n⏳ <i>Синхронизация с Яндекс Таблицей и топиком в фоне...</i>"
    )
    if cb.message:
        try:
            await cb.message.edit_text(text_saving)
        except Exception as e:
            log.debug(f"Не удалось обновить статус сообщения посещаемости: {e}")
    asyncio.create_task(_instant_topic_sync(session))
    asyncio.create_task(_async_commit_and_update(cb.message, session, stats))
    log.info(f"Сводка пары {session.lesson_num} выдана, запущены оптимистичный апдейт и выгрузка")


@router.message(Command("attendance"))
@router.callback_query(F.data == "att:menu")
async def show_attendance_menu(event: Message | CallbackQuery) -> None:
    """Открывает меню выбора даты для отметки посещаемости."""
    from bot.templates.admin.attendance import get_days_select_kb
    text = "📋 <b>Отметка посещаемости</b>\n\nВыберите учебный день для отметки пар:"
    kb = get_days_select_kb()
    if isinstance(event, CallbackQuery):
        if event.message:
            await event.message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("att:day:"))
async def cb_select_day(cb: CallbackQuery) -> None:
    """Выводит список пар на выбранную дату."""
    from datetime import date
    day_str = cb.data.split(":")[2]
    target_date = date.fromisoformat(day_str)
    lessons = await get_api_schedule_for_date(target_date)
    kb = get_lesson_select_kb(lessons, target_date)
    text = f"📋 <b>Дата: {target_date.strftime('%d.%m.%Y')}</b>\nВыберите пару для отметки посещаемости:"
    if cb.message:
        await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


def parse_start_callback(data: str):
    """Извлекает целевую дату и номер пары из callback данных."""
    from datetime import date
    parts = data.split(":")
    if len(parts) == 4:
        return date.fromisoformat(parts[2]), int(parts[3])
    return datetime.now(TIMEZONE).date(), int(parts[2])


def get_initiator_title(initiator_id: int) -> str:
    """Возвращает читаемый статус инициатора опроса (Староста / Замстаросты)."""
    from config import ALLOWED_USER_ID
    return "Староста" if initiator_id == ALLOWED_USER_ID else "Замстаросты"


async def check_session_ownership(cb: CallbackQuery, session) -> bool:
    """Проверяет принадлежность активной сессии текущему старосте."""
    if not session:
        await cb.answer("Сессия завершена или не найдена", show_alert=True)
        return False
    if session.initiator_id != cb.from_user.id:
        title = get_initiator_title(session.initiator_id)
        await cb.answer(f"⚠️ Опрос сейчас заполняет {title}. Действие отклонено.", show_alert=True)
        return False
    return True


@router.callback_query(F.data.startswith("att:start:"))
async def cb_start_attendance(cb: CallbackQuery) -> None:
    """Инициализирует сессию отметки и выводит первого студента."""
    active = await get_active_session()
    if active and active.initiator_id != cb.from_user.id:
        title = get_initiator_title(active.initiator_id)
        await cb.answer(f"⚠️ Опрос уже проводит {title}! Дождитесь завершения.", show_alert=True)
        return
    await cb.answer()
    target_date, lesson_num = parse_start_callback(cb.data)
    lessons = await get_api_schedule_for_date(target_date)
    matched = [les for les in lessons if getattr(les, "number", getattr(les, "period", -1) + 1) == lesson_num]
    title = matched[0].subject if matched else f"Пара {lesson_num}"
    if cb.message:
        await cb.message.edit_text("⏳ <i>Загрузка списка группы из таблицы...</i>")
    try:
        session = await create_attendance_session(target_date, lesson_num, title, cb.from_user.id)
    except Exception as e:
        log.error(f"Сбой инициализации сессии: {e}")
        if cb.message:
            await cb.message.edit_text(f"❌ Не удалось открыть таблицу: {e}")
        return
    card_text = format_student_card(session)
    kb = get_student_poll_kb(can_back=False)
    if cb.message:
        await cb.message.edit_text(card_text, reply_markup=kb)


@router.callback_query(F.data.startswith("att:mark:"))
async def cb_mark_student(cb: CallbackQuery) -> None:
    """Фиксирует отметку и переключает на следующего студента."""
    session = await get_active_session()
    if not await check_session_ownership(cb, session):
        return
    mark = cb.data.split(":")[2]
    session = await record_student_mark(mark)
    if not session:
        await cb.answer("Сессия завершена или не найдена", show_alert=True)
        return
    await cb.answer()
    if session.current_idx < len(session.students):
        text = format_student_card(session)
        kb = get_student_poll_kb(can_back=True)
        if cb.message:
            await cb.message.edit_text(text, reply_markup=kb)
        return
    await finish_and_notify(cb, session)


@router.callback_query(F.data == "att:back")
async def cb_step_back(cb: CallbackQuery) -> None:
    """Возвращает к предыдущему студенту для исправления отметки."""
    session = await get_active_session()
    if not await check_session_ownership(cb, session):
        return
    session = await step_back()
    if not session:
        await cb.answer("Сессия не найдена", show_alert=True)
        return
    can_back = session.current_idx > 0
    text = format_student_card(session)
    kb = get_student_poll_kb(can_back=can_back)
    if cb.message:
        await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data == "att:all_p")
async def cb_all_present(cb: CallbackQuery) -> None:
    """Проставляет 'П' всем оставшимся студентам и завершает опрос."""
    session = await get_active_session()
    if not await check_session_ownership(cb, session):
        return
    session = await mark_all_remaining_present()
    if not session:
        await cb.answer("Сессия не найдена", show_alert=True)
        return
    await cb.answer()
    await finish_and_notify(cb, session)


@router.callback_query(F.data.startswith("att:cancel:"))
async def cb_cancel_lesson(cb: CallbackQuery) -> None:
    """Отменяет опрос для указанной пары."""
    lesson_num = cb.data.split(":")[2]
    await clear_session()
    if cb.message:
        await cb.message.edit_text(f"❌ Отметка посещаемости за пару {lesson_num} отменена.")
    await cb.answer()


@router.callback_query(F.data == "att:abort")
async def cb_abort_survey(cb: CallbackQuery) -> None:
    """Прерывает активный опрос старостой."""
    session = await get_active_session()
    if session and session.initiator_id != cb.from_user.id:
        title = get_initiator_title(session.initiator_id)
        await cb.answer(f"⚠️ Опрос проводит {title}. Отменить может только автор.", show_alert=True)
        return
    await clear_session()
    if cb.message:
        await cb.message.edit_text("❌ Опрос посещаемости прерван.")
    await cb.answer()


@router.callback_query(F.data == "att:close")
async def cb_close_menu(cb: CallbackQuery) -> None:
    """Удаляет меню выбора пары."""
    if cb.message:
        await cb.message.delete()
    await cb.answer()
