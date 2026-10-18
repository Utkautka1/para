"""
Модуль синхронизации и авто-обновления сообщения в топике 'Экзамены'.

Сохраняет состояние EXAM_MAIN_MSG_ID в data/exam_topic_state.json.
Автоматически формирует реестр экзаменов с точным расчётом дат проведения.
"""

import asyncio
import html
from datetime import date, datetime, timedelta

from aiogram.exceptions import TelegramBadRequest

from config import (
    EXAM_TOPIC_STATE_FILE,
    EXAM_TOPIC_THREAD_ID,
    TIMEZONE,
    TOPIC_CHAT_ID,
)
from core.api_client import get_api_exams
from core.bot import bot
from core.logger import get_logger
from services.models import ExamItem
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("exam_topic_updater")
STATE_FILE = EXAM_TOPIC_STATE_FILE
_EXAM_MAIN_MSG_ID: int | None = None


def get_default_semester_start() -> date:
    """
    Вычисляет 1 сентября текущего учебного года при недоступности API.

    Используется как базовая дата отсчета учебных недель, если API КТМУ недоступно.

    Возвращает объект даты date(YYYY, 9, 1).
    """
    today = datetime.now(TIMEZONE).date()
    start_year = today.year if today.month >= 8 else today.year - 1

    return date(start_year, 9, 1)


async def get_effective_semester_start() -> date:
    """
    Определяет актуальную дату старта семестра из расписания КТМУ.

    Запрашивает конфиг расписания колледжа, при сбоях откатываясь к 1 сентября.

    Возвращает объект date начала семестра.
    """
    try:
        from services.schedule_parser import fetch_schedule_data

        data = await fetch_schedule_data(force_refresh=False)
        if data:
            s_str = data.get("config", {}).get("semesterStart")
            if s_str:
                return date.fromisoformat(s_str)
    except Exception as e:
        log.warning(f"Не удалось получить semesterStart для экзаменов: {e}")

    return get_default_semester_start()


def load_exam_topic_state() -> int | None:
    """
    Загружает ID главного закрепленного сообщения топика экзаменов.

    Считывает состояние из JSON-файла для предотвращения дублирования сообщений при рестарте.

    Возвращает целочисленный ID сообщения Telegram или None.
    """
    data = sync_load_json(STATE_FILE, default={})

    return data.get("main_msg_id") if isinstance(data, dict) else None


def save_exam_topic_state(msg_id: int | None) -> None:
    """
    Атомарно сохраняет ID главного сообщения топика экзаменов.

    Защищает от повреждения файла состояния при внезапном падении контейнера.

    Ничего не возвращает.
    """
    sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})


def get_week_date_range_str(week_num: int, semester_start: date | None = None) -> str:
    """
    Вычисляет диапазон календарных дат для указанного номера учебной недели.

    Рассчитывает понедельник и воскресенье относительно даты старта семестра.

    Возвращает отформатированную строку диапазона дат (например, '01.09–07.09').
    """
    start_d = semester_start or get_default_semester_start()
    start_sunday = start_d + timedelta(days=(6 - start_d.weekday()))

    if week_num == 1:
        return f"{start_d.strftime('%d.%m')}–{start_sunday.strftime('%d.%m')}"

    mon = start_sunday + timedelta(days=1) + timedelta(weeks=week_num - 2)
    sun = mon + timedelta(days=6)

    return f"{mon.strftime('%d.%m')}–{sun.strftime('%d.%m.%Y')}"


def _format_exam_weeks_label(weeks: list[int], semester_start: date | None) -> str:
    """
    Формирует текстовое описание недель и календарных дат сдачи экзамена.

    Возвращает строку с перечислением номеров недель и интервалов дат.
    """
    if not weeks:
        return "Дата уточняется"

    date_ranges = [get_week_date_range_str(w, semester_start) for w in weeks]
    return f"{', '.join(map(str, weeks))} нед. (🗓 <b>{', '.join(date_ranges)}</b>)"


def format_exam_card(ex: ExamItem, semester_start: date | None = None) -> str:
    """
    Формирует отдельную карточку аттестации или экзамена с экранированием HTML.

    Включает название предмета, форму контроля, подгруппу, даты, преподавателя и аудиторию.

    Возвращает отформатированный HTML-фрагмент карточки.
    """
    weeks_str = _format_exam_weeks_label(ex.weeks, semester_start)
    sg_str = f" • 👥 Подгруппа {ex.subgroup}" if ex.subgroup > 0 else ""

    subj = html.escape(ex.subject)
    e_type = html.escape(ex.exam_type)
    teacher = html.escape(ex.teacher)
    addr = html.escape(ex.address)
    room = html.escape(ex.room)

    return (
        f"📌 <b>{subj}</b> ({e_type}){sg_str}\n"
        f"⏳ <b>Период сдачи:</b> {weeks_str}\n"
        f"👨‍🏫 <i>{teacher}</i>\n"
        f"{ex.format_str} • 🏢 {addr} ({room})"
    )


def format_exams_schedule_message(exams: list[ExamItem], semester_start: date | None = None) -> str:
    """
    Форматирует расписание экзаменов и аттестаций в полный HTML-текст сообщения.

    Добавляет заголовок реестра и объединяет карточки предметов через разделители.

    Возвращает готовый для отправки в Telegram HTML-текст.
    """
    header = (
        "📑 <b>АТТЕСТАЦИИ И ЭКЗАМЕНЫ ГРУППЫ 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    if not exams:
        return header + "<i>Информация о зачётах и экзаменах формируется...</i> ☕️"

    blocks = [format_exam_card(ex, semester_start) for ex in exams]
    return header + "\n\n".join(blocks)


async def _pin_exam_silently(message_id: int) -> None:
    """
    Закрепляет сообщение экзаменов в топике без системного пуш-уведомления.

    Использует disable_notification=True для исключения лишнего шума в чате.

    Ничего не возвращает.
    """
    try:
        await bot.pin_chat_message(
            chat_id=TOPIC_CHAT_ID,
            message_id=message_id,
            disable_notification=True,
        )
    except Exception as e:
        log.warning(f"Не удалось закрепить exam MSG_ID={message_id}: {e}")


async def create_exam_message(text: str) -> int:
    """
    Создает и закрепляет главное сообщение в топике экзаменов.

    Отправляет пост в Telegram, сохраняет ID в стейт и закрепляет его.

    Возвращает целочисленный message_id созданного сообщения.
    """
    msg = await bot.send_message(
        chat_id=TOPIC_CHAT_ID,
        message_thread_id=EXAM_TOPIC_THREAD_ID,
        text=text,
    )
    save_exam_topic_state(msg.message_id)
    await _pin_exam_silently(msg.message_id)

    log.info(f"Сообщение экзаменов создано и закреплено: MSG_ID={msg.message_id}")
    return msg.message_id


async def handle_exam_edit_error(text: str, err_str: str, retry: bool) -> bool:
    """
    Обрабатывает ошибку редактирования сообщения топика экзаменов.

    При неизменности текста возвращает True, при других ошибках пересоздает сообщение.

    Возвращает True в случае успеха восстановления, иначе False.
    """
    global _EXAM_MAIN_MSG_ID

    if "not modified" in err_str:
        log.debug(f"sync_exam_topic: 'not modified' (MSG_ID={_EXAM_MAIN_MSG_ID})")
        return True

    if retry:
        log.error("❌ Повторная ошибка создания exam-сообщения")
        return False

    log.warning(f"⚠️ Ошибка редактирования exam MSG_ID={_EXAM_MAIN_MSG_ID}, пересоздаём...")
    _EXAM_MAIN_MSG_ID = None
    save_exam_topic_state(None)

    return await send_or_edit_exam_msg(text, _retry=True)


async def _edit_exam_msg(text: str) -> bool:
    """
    Редактирует текст активного сообщения экзаменов в топике.

    Возвращает True в случае успешного редактирования.
    """
    await bot.edit_message_text(
        chat_id=TOPIC_CHAT_ID,
        message_id=_EXAM_MAIN_MSG_ID,
        text=text,
    )
    log.info(f"✅ Сообщение экзаменов обновлено: MSG_ID={_EXAM_MAIN_MSG_ID}")
    return True


async def send_or_edit_exam_msg(text: str, _retry: bool = False) -> bool:
    """
    Отправляет новое или редактирует существующее сообщение в топике экзаменов.

    Перехватывает исключения Telegram API с вызовом обработчика сбоев.

    Возвращает True при успешном обновлении, иначе False.
    """
    global _EXAM_MAIN_MSG_ID

    try:
        if _EXAM_MAIN_MSG_ID is None:
            _EXAM_MAIN_MSG_ID = await create_exam_message(text)
            return True

        return await _edit_exam_msg(text)
    except TelegramBadRequest as e:
        return await handle_exam_edit_error(text, str(e).lower(), _retry)
    except Exception as e:
        log.error(f"❌ Ошибка обновления топика экзаменов: {type(e).__name__}: {e}")
        return False


async def _delete_old_exam_msg(old_id: int | None) -> None:
    """
    Пытается удалить старое сообщение экзаменов из топика супергруппы.

    Ничего не возвращает.
    """
    if not old_id:
        return

    try:
        await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=old_id)
        log.info(f"Старое exam-сообщение MSG_ID={old_id} удалено")
    except Exception as e:
        log.warning(f"Не удалось удалить exam MSG_ID={old_id}: {e}")


async def recreate_exam_topic_message() -> bool:
    """
    Удаляет текущее сообщение экзаменов и принудительно создает новое с нуля.

    Используется администратором для сброса рассинхронизации ID сообщений.

    Возвращает True в случае успешного пересоздания.
    """
    global _EXAM_MAIN_MSG_ID

    old_id = _EXAM_MAIN_MSG_ID or load_exam_topic_state()
    await _delete_old_exam_msg(old_id)

    _EXAM_MAIN_MSG_ID = None
    save_exam_topic_state(None)

    return await sync_exam_topic_message()


async def sync_exam_topic_message() -> bool:
    """
    Атомарно публикует или обновляет расписание экзаменов в топике.

    Загружает актуальный список экзаменов из API, форматирует HTML и обновляет пост.

    Возвращает True при успешном обновлении, иначе False.
    """
    global _EXAM_MAIN_MSG_ID

    if _EXAM_MAIN_MSG_ID is None:
        _EXAM_MAIN_MSG_ID = load_exam_topic_state()

    exams = await get_api_exams()
    sem_start = await get_effective_semester_start()
    text = format_exams_schedule_message(exams, sem_start)

    try:
        return await send_or_edit_exam_msg(text)
    except Exception as e:
        log.error(f"Ошибка обновления топика экзаменов: {e}")
        return False


async def exam_topic_sync_loop() -> None:
    """
    Фоновый рабочий цикл авто-обновления топика экзаменов каждые 10 минут.

    Обеспечивает периодическую актуализацию дат сессии и консультаций.

    Никогда не завершается штатно при нормальной работе сервиса.
    """
    log.info("Запущен фоновый сервис авто-обновления топика Экзамены (10 мин)")

    while True:
        try:
            await sync_exam_topic_message()
        except Exception as e:
            log.error(f"Ошибка в цикле exam_topic_sync_loop: {e}")

        await asyncio.sleep(600)
