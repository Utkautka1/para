"""
Модуль синхронизации и авто-обновления сообщения в топике 'Посещаемость'.

Отвечает за:
  1. Публикацию и закрепление академического рейтинга группы по лигам
  2. Визуализацию прогресс-баров посещаемости и сквозного пульса группы
  3. Сохранение идентификатора сообщения в data/attendance_topic_state.json
  4. Фоновый цикл авто-обновления без лишних интерактивных кнопок в чате
"""

import asyncio
import html
from datetime import datetime
from typing import Any

from aiogram.exceptions import TelegramBadRequest

from config import (
    ATTENDANCE_SYNC_DAY_INTERVAL_SECONDS,
    ATTENDANCE_SYNC_NIGHT_INTERVAL_SECONDS,
    ATTENDANCE_TOPIC_STATE_FILE,
    ATTENDANCE_TOPIC_THREAD_ID,
    TIMEZONE,
    TOPIC_CHAT_ID,
)
from core.bot import bot
from core.logger import get_logger
from core.redis_cache import redis_lock
from services.attendance_stats import fetch_all_time_attendance
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("att_topic_updater")
STATE_FILE = ATTENDANCE_TOPIC_STATE_FILE
_ATT_MAIN_MSG_ID: int | None = None


def load_attendance_topic_state() -> int | None:
    """
    Загружает сохраненный ID главного сообщения топика посещаемости.

    Считывает состояние из JSON-файла для восстановления контекста после перезагрузки.

    Возвращает целое число ID сообщения Telegram или None.
    """
    data = sync_load_json(STATE_FILE, default={})

    return data.get("main_msg_id") if isinstance(data, dict) else None


def save_attendance_topic_state(msg_id: int | None) -> None:
    """
    Атомарно сохраняет ID главного сообщения топика посещаемости.

    Предотвращает порчу файла состояния при аварийной остановке сервиса.

    Ничего не возвращает.
    """
    sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})


def make_progress_bar(pct: float) -> str:
    """
    Формирует аккуратную 4-символьную шкалу прогресса посещаемости.

    Визуализирует процент посещаемости закрашенными и пустыми блоками.

    Возвращает строку вида '▰▰▰▱'.
    """
    filled = max(0, min(4, round(pct / 25.0)))

    return "▰" * filled + "▱" * (4 - filled)


def extract_short_fio(fio: str) -> str:
    """
    Извлекает Фамилию и Имя без отчества для исключения переносов строк.

    Компактизирует длинные ФИО для аккуратного мобильного отображения.

    Возвращает строку 'Фамилия Имя'.
    """
    parts = fio.split()

    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"

    return fio


def _build_student_item(fio: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Преобразует сырые данные студента в структурированный элемент рейтинга.

    Уважительная причина (У) не снижает общий процент академической успеваемости.

    Возвращает словарь агрегированных показателей студента.
    """
    tot = data.get("total", {})
    p, o = tot.get("П", 0), tot.get("О", 0)
    u, n = tot.get("У", 0), tot.get("Н", 0)
    total_classes = p + o + u + n
    valid_classes = p + o + u
    pct = (valid_classes / total_classes * 100.0) if total_classes > 0 else 100.0

    return {
        "fio": extract_short_fio(fio),
        "p": p,
        "o": o,
        "u": u,
        "n": n,
        "pct": pct,
        "total": total_classes,
    }


def _build_compact_topic_header(pulse: float, total: int, p_cnt: int, d_cnt: int) -> str:
    """
    Формирует презентабельную компактную шапку дашборда группы.

    Выводит общий академический пульс и сводное количество студентов.

    Возвращает отформатированную HTML-шапку дашборда.
    """
    return (
        "📊 <b>ПОСЕЩАЕМОСТЬ • 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Всего: <b>{total}</b>  •  📈 Пульс: <b>{pulse:.1f}%</b>\n"
        f"✨ Без пропусков: <b>{p_cnt}</b>  •  ⚠️ С пропусками: <b>{d_cnt}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )


def _decline_absence(n: int) -> str:
    """
    Склоняет слово 'прогул' по грамматическим правилам русского языка.

    Учитывает падежные окончания для числительных от 1 до бесконечности.

    Возвращает строку вида '1 прогул', '2 прогула', '5 прогулов'.
    """
    if 11 <= (n % 100) <= 14:
        return f"{n} прогулов"

    rem = n % 10
    if rem == 1:
        return f"{n} прогул"
    if 2 <= rem <= 4:
        return f"{n} прогула"

    return f"{n} прогулов"


def _format_debt_details(s: dict[str, Any]) -> str:
    """
    Формирует понятный список причин пропусков (прогулы, опоздания, справки).

    Возвращает строку с перечислением типов пропусков или 'без замечаний'.
    """
    parts = []

    if s["n"] > 0:
        parts.append(_decline_absence(s["n"]))
    if s["o"] > 0:
        parts.append(f"{s['o']} оп.")
    if s["u"] > 0:
        parts.append(f"{s['u']} по справке")

    return ", ".join(parts) if parts else "без замечаний"


def _format_debt_student(s: dict[str, Any]) -> str:
    """
    Формирует строку студента, имеющего пропуски или опоздания.

    Выбирает визуальный эмодзи-индикатор риска (⛔️ отчисление, 🚨 внимание).

    Возвращает HTML-строку должника.
    """
    details = _format_debt_details(s)
    clean_fio = html.escape(s["fio"])

    if s["pct"] == 0 or s["n"] >= 12:
        icon = "⛔️"
    elif s["n"] >= 5:
        icon = "🚨"
    else:
        icon = "•"

    return f"{icon} <b>{clean_fio}</b> — <b>{s['pct']:.0f}%</b> ({details})"


def _format_perfect_student(s: dict[str, Any]) -> str:
    """
    Формирует аккуратную строку отличника без лишнего визуального шума.

    Выводит отметку о справках, если студент не имеет несанкционированных прогулов.

    Возвращает HTML-строку студента без пропусков.
    """
    clean_fio = html.escape(s["fio"])

    if s["u"] > 0:
        return f"• <b>{clean_fio}</b> <i>({s['u']} по справке)</i>"

    return f"• <b>{clean_fio}</b>"


def _build_topic_footer() -> str:
    """
    Формирует подвал сообщения со ссылкой на ЛС и временем обновления.

    Возвращает строку футера с разделителем.
    """
    now_str = datetime.now(TIMEZONE).strftime("%H:%M")

    return (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📱 <i>Личная статистика и срез по датам: /my_attendance в ЛС</i>\n"
        f"⏱ <i>Обновлено: {now_str} МСК</i>"
    )


def _group_students_by_debts(items: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    """
    Разделяет общий список студентов на отличников и имеющих пропуски/долги.

    Возвращает кортеж (perfect_students, debt_students).
    """
    perfect = [s for s in items if s["n"] == 0 and s["o"] == 0]
    debts = [s for s in items if s["n"] > 0 or s["o"] > 0]

    perfect.sort(key=lambda s: s["fio"])
    debts.sort(key=lambda s: (-s["pct"], -s["n"], s["fio"]))

    return perfect, debts


def _build_topic_body_lines(perfect: list[dict[str, Any]], debts: list[dict[str, Any]]) -> list[str]:
    """
    Формирует текстовые секции отличников и должников реестра посещаемости.

    Возвращает список отформатированных строк.
    """
    lines = ["\n🏆 <b>БЕЗ ПРОПУСКОВ (100%):</b>"]
    lines.extend(_format_perfect_student(s) for s in perfect)

    if debts:
        lines.append("\n⚠️ <b>ЖУРНАЛ ПРОПУСКОВ И ОПОЗДАНИЙ:</b>")
        lines.extend(_format_debt_student(s) for s in debts)

    return lines


def format_attendance_topic_message(stats: dict[str, dict[str, Any]]) -> str:
    """
    Формирует дашборд с компактным блоком отличников и журналом долгов.

    Считает процент посещаемости группы и генерирует структурированный дашборд.

    Возвращает готовый для отправки в Telegram HTML-текст.
    """
    if not stats:
        header = _build_compact_topic_header(0.0, 0, 0, 0)
        return header + "<i>Данные журнала посещаемости загружаются...</i> ⏳"

    items = [_build_student_item(fio, d) for fio, d in stats.items()]
    perfect, debts = _group_students_by_debts(items)
    pulse = sum(s["pct"] for s in items) / len(items) if items else 0.0

    header = _build_compact_topic_header(pulse, len(items), len(perfect), len(debts))
    lines = [header.rstrip(), *_build_topic_body_lines(perfect, debts)]
    lines.append(_build_topic_footer())

    return "\n".join(lines)


async def _pin_attendance_silently(message_id: int) -> None:
    """
    Закрепляет главное сообщение реестра в топике без звукового уведомления.

    Использует disable_notification=True для исключения спама участникам.

    Ничего не возвращает.
    """
    try:
        await bot.pin_chat_message(
            chat_id=TOPIC_CHAT_ID,
            message_id=message_id,
            disable_notification=True,
        )
    except Exception as e:
        log.warning(f"Не удалось закрепить attendance MSG_ID={message_id}: {e}")


async def create_attendance_message(text: str) -> int:
    """
    Создает и закрепляет главное сообщение в топике посещаемости.

    Отправляет пост в Telegram, сохраняет ID в стейт и закрепляет его.

    Возвращает целочисленный ID созданного сообщения.
    """
    msg = await bot.send_message(
        chat_id=TOPIC_CHAT_ID,
        message_thread_id=ATTENDANCE_TOPIC_THREAD_ID,
        text=text,
    )
    save_attendance_topic_state(msg.message_id)
    await _pin_attendance_silently(msg.message_id)

    log.info(f"Сообщение реестра посещаемости создано: MSG_ID={msg.message_id}")
    return msg.message_id


async def handle_attendance_edit_error(text: str, err_str: str, retry: bool) -> bool:
    """
    Обрабатывает ошибки обновления сообщения в топике (not modified / удалено).

    При неизменности возвращает True, при других ошибках инициирует разовый retry.

    Возвращает True в случае успеха восстановления, иначе False.
    """
    global _ATT_MAIN_MSG_ID

    if "not modified" in err_str:
        log.debug(f"sync_att_topic: 'not modified' ({_ATT_MAIN_MSG_ID})")
        return True

    if retry:
        log.error("❌ Повторная ошибка создания attendance-сообщения")
        return False

    log.warning(f"⚠️ Ошибка редактирования attendance MSG_ID={_ATT_MAIN_MSG_ID}, пересоздаём...")
    _ATT_MAIN_MSG_ID = None
    save_attendance_topic_state(None)

    return await send_or_edit_attendance_msg(text, _retry=True)


async def _edit_attendance_msg(text: str) -> bool:
    """
    Редактирует текст активного сообщения посещаемости в топике Telegram.

    Возвращает True в случае успешного редактирования.
    """
    await bot.edit_message_text(
        chat_id=TOPIC_CHAT_ID,
        message_id=_ATT_MAIN_MSG_ID,
        text=text,
    )
    log.info(f"✅ Реестр посещаемости обновлен: MSG_ID={_ATT_MAIN_MSG_ID}")
    return True


async def send_or_edit_attendance_msg(text: str, _retry: bool = False) -> bool:
    """
    Отправляет или обновляет главное сообщение в топике посещаемости.

    Использует ленивое создание при отсутствии ID или обновляет существующий пост.

    Возвращает True в случае успешного обновления, иначе False.
    """
    global _ATT_MAIN_MSG_ID

    try:
        if _ATT_MAIN_MSG_ID is None:
            _ATT_MAIN_MSG_ID = await create_attendance_message(text)
            return True

        return await _edit_attendance_msg(text)
    except TelegramBadRequest as e:
        return await handle_attendance_edit_error(text, str(e).lower(), _retry)
    except Exception as e:
        log.error(f"❌ Ошибка обновления реестра посещаемости: {type(e).__name__}: {e}")
        return False


async def _delete_old_attendance_msg(old_id: int | None) -> None:
    """
    Пытается удалить старое сообщение посещаемости из топика Telegram.

    Ничего не возвращает.
    """
    if not old_id:
        return

    try:
        await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=old_id)
        log.info(f"Старое attendance-сообщение MSG_ID={old_id} удалено")
    except Exception as e:
        log.warning(f"Не удалось удалить attendance MSG_ID={old_id}: {e}")


async def recreate_attendance_topic_message() -> bool:
    """
    Удаляет старое сообщение топика посещаемости и создаёт новое.

    Используется администратором для принудительного сброса состояния.

    Возвращает True в случае успешного создания нового сообщения.
    """
    global _ATT_MAIN_MSG_ID

    old_id = _ATT_MAIN_MSG_ID or load_attendance_topic_state()
    await _delete_old_attendance_msg(old_id)

    _ATT_MAIN_MSG_ID = None
    save_attendance_topic_state(None)

    return await sync_attendance_topic_message(force_refresh=True)


async def sync_attendance_topic_message(force_refresh: bool = False) -> bool:
    """
    Синхронизирует данные из таблицы и обновляет сообщение в топике под Redis-локом.

    Защищает от параллельных конфликтующих обновлений через распределенный лок.

    Возвращает True при успешном обновлении, иначе False.
    """
    global _ATT_MAIN_MSG_ID

    if _ATT_MAIN_MSG_ID is None:
        _ATT_MAIN_MSG_ID = load_attendance_topic_state()

    async with redis_lock("att:lock:topic_sync", ttl=20) as acquired:
        if not acquired:
            log.debug("Синхронизация топика посещаемости пропущена: занят лок")
            return False

        try:
            stats = await fetch_all_time_attendance(force_refresh=force_refresh)
            text = format_attendance_topic_message(stats)
            return await send_or_edit_attendance_msg(text)
        except Exception as e:
            log.error(f"Ошибка синхронизации реестра посещаемости: {e}")
            return False


def _get_attendance_sync_sleep_seconds() -> int:
    """
    Определяет интервал: 3 мин в учебные часы (08-19), иначе 15 мин.

    Экономит ресурсы сервера и API ночью и по воскресеньям.

    Возвращает количество секунд задержки до следующей синхронизации.
    """
    now = datetime.now(TIMEZONE)

    if 8 <= now.hour < 19 and now.weekday() < 6:
        return ATTENDANCE_SYNC_DAY_INTERVAL_SECONDS

    return ATTENDANCE_SYNC_NIGHT_INTERVAL_SECONDS


async def attendance_topic_sync_loop() -> None:
    """
    Фоновый рабочий цикл авто-обновления топика с адаптивным интервалом.

    Опрашивает журнал посещаемости и актуализирует закрепленный пост в топике.

    Никогда не завершается штатно при нормальной работе сервиса.
    """
    log.info("Запущен адаптивный фоновый сервис авто-обновления топика Посещаемость")

    while True:
        try:
            await sync_attendance_topic_message(force_refresh=False)
        except Exception as e:
            log.error(f"Ошибка в цикле attendance_topic_sync_loop: {e}")

        sleep_sec = _get_attendance_sync_sleep_seconds()
        await asyncio.sleep(sleep_sec)
