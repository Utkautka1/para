"""
Модуль синхронизации и авто-обновления сообщения в топике 'Посещаемость'.

Отвечает за:
  1. Публикацию и закрепление академического рейтинга группы по лигам
  2. Визуализацию прогресс-баров посещаемости и сквозного пульса группы
  3. Сохранение идентификатора сообщения в data/attendance_topic_state.json
  4. Фоновый цикл авто-обновления без лишних интерактивных кнопок в чате
"""

import asyncio
from datetime import datetime
import html
from typing import Any, Dict, List, Optional
from aiogram.exceptions import TelegramBadRequest

from config import ATTENDANCE_TOPIC_THREAD_ID, TIMEZONE, TOPIC_CHAT_ID
from core.bot import bot
from core.logger import get_logger
from services.attendance_stats import fetch_all_time_attendance
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("att_topic_updater")
STATE_FILE = "data/attendance_topic_state.json"
_ATT_MAIN_MSG_ID: Optional[int] = None


def load_attendance_topic_state() -> Optional[int]:
    """Загружает сохраненный ID главного сообщения топика посещаемости."""
    data = sync_load_json(STATE_FILE, default={})
    return data.get("main_msg_id") if isinstance(data, dict) else None


def save_attendance_topic_state(msg_id: Optional[int]) -> None:
    """Атомарно сохраняет ID главного сообщения топика посещаемости."""
    sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})


def make_progress_bar(pct: float) -> str:
    """Формирует аккуратную 4-символьную шкалу прогресса посещаемости."""
    filled = max(0, min(4, round(pct / 25.0)))
    return "▰" * filled + "▱" * (4 - filled)


def _format_compact_marks(p: int, o: int, u: int, n: int) -> str:
    """Формирует компактную строку отметок без лишних нулей."""
    parts = [f"{p}П"]
    if o > 0:
        parts.append(f"{o}О")
    if u > 0:
        parts.append(f"{u}У")
    parts.append(f"{n}Н")
    return " · ".join(parts)


def extract_short_fio(fio: str) -> str:
    """Извлекает Фамилию и Имя без отчества для исключения переносов строк."""
    parts = fio.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return fio


def _build_student_item(fio: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Преобразует сырые данные студента в структурированный элемент рейтинга."""
    tot = data.get("total", {})
    p, o = tot.get("П", 0), tot.get("О", 0)
    u, n = tot.get("У", 0), tot.get("Н", 0)
    total_classes = p + o + u + n
    pct = (p / total_classes * 100.0) if total_classes > 0 else 0.0
    return {
        "fio": extract_short_fio(fio),
        "p": p, "o": o, "u": u, "n": n,
        "pct": pct, "total": total_classes,
    }


def _build_topic_header(pulse: float, total: int, g_cnt: int, s_cnt: int, r_cnt: int) -> str:
    """Формирует презентабельную шапку академического дашборда группы."""
    return (
        "📊 <b>ДАШБОРД ПОСЕЩАЕМОСТИ • 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Студентов:</b> {total}  •  📈 <b>Пульс группы:</b> <b>{pulse:.1f}%</b>\n"
        f"🏆 Лидеры: <b>{g_cnt}</b>  •  ⚡️ В норме: <b>{s_cnt}</b>  •  🚨 Риск: <b>{r_cnt}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )


def _format_league_line(s: Dict[str, Any], icon: str) -> str:
    """Формирует ультра-компактную однострочную запись студента."""
    bar = make_progress_bar(s["pct"])
    marks = _format_compact_marks(s["p"], s["o"], s["u"], s["n"])
    clean_fio = html.escape(s["fio"])
    return f"{icon} <b>{clean_fio}</b> · <b>{s['pct']:.0f}%</b> {bar} ({marks})"


def _build_league_block(
    title: str, students: List[Dict[str, Any]], is_gold: bool = False, is_risk: bool = False
) -> List[str]:
    """Формирует визуальный блок отдельной лиги студентов."""
    if not students:
        return []
    lines = [f"\n{title}"]
    for idx, s in enumerate(students, 1):
        if is_gold:
            icon = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else "•"))
        elif is_risk:
            icon = "⛔️" if s["pct"] == 0 else "⚠️"
        else:
            icon = "•"
        lines.append(_format_league_line(s, icon))
    return lines


def _build_topic_footer() -> str:
    """Формирует подвал сообщения с легендой обозначений."""
    return (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>П — был, О — опоздал, У — уважительная, Н — прогул.</i>\n"
        "📱 <i>Личная статистика и срез по месяцам: /my_attendance в ЛС</i>"
    )


def format_attendance_topic_message(stats: Dict[str, Dict[str, Any]]) -> str:
    """Форматирует стильный академический дашборд рейтинга посещаемости."""
    if not stats:
        header = _build_topic_header(0.0, 0, 0, 0, 0)
        return header + "<i>Данные журнала посещаемости загружаются...</i> ⏳"
    items = [_build_student_item(fio, d) for fio, d in stats.items()]
    items.sort(key=lambda s: (-s["pct"], s["n"], s["fio"]))
    gold = [s for s in items if s["pct"] >= 90]
    silver = [s for s in items if 60 <= s["pct"] < 90]
    risk = [s for s in items if s["pct"] < 60]
    avg_pulse = sum(s["pct"] for s in items) / len(items) if items else 0.0
    header = _build_topic_header(avg_pulse, len(items), len(gold), len(silver), len(risk))
    lines = [header.rstrip()]
    lines.extend(_build_league_block("🏆 <b>ЗОЛОТАЯ ЛИГА (90–100%)</b>", gold, is_gold=True))
    lines.extend(_build_league_block("⚡️ <b>СЕРЕБРЯНАЯ ЛИГА (60–89%)</b>", silver))
    lines.extend(_build_league_block("🚨 <b>ЗОНА РИСКА (МЕНЕЕ 60%)</b>", risk, is_risk=True))
    lines.append(_build_topic_footer())
    return "\n".join(lines)


async def _pin_attendance_silently(message_id: int) -> None:
    """Закрепляет главное сообщение реестра в топике без звукового уведомления."""
    try:
        await bot.pin_chat_message(
            chat_id=TOPIC_CHAT_ID, message_id=message_id,
            disable_notification=True
        )
    except Exception as e:
        log.warning(f"Не удалось закрепить attendance MSG_ID={message_id}: {e}")


async def create_attendance_message(text: str) -> int:
    """Создает и закрепляет главное сообщение в топике посещаемости."""
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
    """Обрабатывает ошибки обновления сообщения в топике (not modified / удалено)."""
    global _ATT_MAIN_MSG_ID
    if "not modified" in err_str:
        log.debug(f"sync_att_topic: 'not modified' — реестр уже актуален ({_ATT_MAIN_MSG_ID})")
        return True
    if retry:
        log.error("❌ Повторная ошибка создания attendance-сообщения")
        return False
    log.warning(f"⚠️ Ошибка редактирования attendance MSG_ID={_ATT_MAIN_MSG_ID}, пересоздаём...")
    _ATT_MAIN_MSG_ID = None
    save_attendance_topic_state(None)
    return await send_or_edit_attendance_msg(text, _retry=True)


async def send_or_edit_attendance_msg(text: str, _retry: bool = False) -> bool:
    """Отправляет или обновляет главное сообщение в топике посещаемости."""
    global _ATT_MAIN_MSG_ID
    try:
        if _ATT_MAIN_MSG_ID is None:
            _ATT_MAIN_MSG_ID = await create_attendance_message(text)
            return True
        await bot.edit_message_text(
            chat_id=TOPIC_CHAT_ID,
            message_id=_ATT_MAIN_MSG_ID,
            text=text,
        )
        log.info(f"✅ Реестр посещаемости обновлен: MSG_ID={_ATT_MAIN_MSG_ID}")
        return True
    except TelegramBadRequest as e:
        return await handle_attendance_edit_error(text, str(e).lower(), _retry)
    except Exception as e:
        log.error(f"❌ Ошибка обновления реестра посещаемости: {type(e).__name__}: {e}")
        return False


async def recreate_attendance_topic_message() -> bool:
    """Удаляет старое сообщение топика посещаемости и создаёт новое."""
    global _ATT_MAIN_MSG_ID
    old_id = _ATT_MAIN_MSG_ID or load_attendance_topic_state()
    if old_id:
        try:
            await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=old_id)
            log.info(f"Старое attendance-сообщение MSG_ID={old_id} удалено")
        except Exception as e:
            log.warning(f"Не удалось удалить attendance MSG_ID={old_id}: {e}")
    _ATT_MAIN_MSG_ID = None
    save_attendance_topic_state(None)
    return await sync_attendance_topic_message(force_refresh=True)


async def sync_attendance_topic_message(force_refresh: bool = False) -> bool:
    """Синхронизирует данные из таблицы и обновляет сообщение в топике."""
    global _ATT_MAIN_MSG_ID
    if _ATT_MAIN_MSG_ID is None:
        _ATT_MAIN_MSG_ID = load_attendance_topic_state()
    try:
        stats = await fetch_all_time_attendance(force_refresh=force_refresh)
        text = format_attendance_topic_message(stats)
        return await send_or_edit_attendance_msg(text)
    except Exception as e:
        log.error(f"Ошибка синхронизации реестра посещаемости: {e}")
        return False


async def attendance_topic_sync_loop() -> None:
    """Фоновый цикл авто-обновления топика посещаемости каждые 15 минут."""
    log.info("Запущен фоновый сервис авто-обновления топика Посещаемость (15 мин)")
    while True:
        try:
            await sync_attendance_topic_message(force_refresh=False)
        except Exception as e:
            log.error(f"Ошибка в цикле attendance_topic_sync_loop: {e}")
        await asyncio.sleep(900)
