"""
Менеджер дней рождения группы 1-КПД-3.

Отвечает за:
  1. Синхронизацию закрепленного реестра дней рождения в топике 6269.
  2. Ежедневный пересчет дней до праздника и исполняющегося возраста.
  3. Отправку персональных поздравлений в топик «Важное» (ID: 2).
"""

import asyncio
import json
import os
import random
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from aiogram.exceptions import TelegramBadRequest

from config import (
    BIRTHDAY_TOPIC_THREAD_ID,
    IMPORTANT_TOPIC_THREAD_ID,
    TIMEZONE,
    TOPIC_CHAT_ID,
)
from core.bot import bot
from core.logger import get_logger

log = get_logger("birthday_manager")

BIRTHDAYS_FILE = "data/birthdays.json"
WISHES_FILE = "data/birthday_wishes.json"
STATE_FILE = "data/birthday_topic_state.json"
HISTORY_FILE = "data/birthday_history.json"
CONGRATS_STATE_FILE = "data/birthday_congrats_state.json"


def load_json_file(file_path: str, default: Any) -> Any:
    """Безопасно загружает данные из JSON файла."""
    if not os.path.exists(file_path):
        return default
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Ошибка чтения {file_path}: {e}")
        return default


def save_json_file(file_path: str, data: Any) -> None:
    """Безопасно сохраняет данные в JSON файл с созданием директории."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Ошибка записи в {file_path}: {e}")


def calculate_days_and_age(item: Dict[str, Any], today: date) -> Dict[str, Any]:
    """Вычисляет оставшиеся дни до дня рождения и возраст именинника."""
    b_day, b_month, b_year = item["day"], item["month"], item["year"]
    try:
        bday_this_year = date(today.year, b_month, b_day)
    except ValueError:
        bday_this_year = date(today.year, b_month, 28)
    if bday_this_year < today:
        try:
            next_bday = date(today.year + 1, b_month, b_day)
        except ValueError:
            next_bday = date(today.year + 1, b_month, 28)
        days = (next_bday - today).days
        age = (today.year + 1) - b_year
        is_today = False
    elif bday_this_year == today:
        days, age, is_today = 0, today.year - b_year, True
    else:
        days, age, is_today = (bday_this_year - today).days, today.year - b_year, False
    return {**item, "days_until": days, "turning_age": age, "is_today": is_today}


def get_person_mention(item: Dict[str, Any]) -> str:
    """Формирует кликабельное упоминание по username или telegram ID."""
    name = item["full_name"]
    username = item.get("username")
    tg_id = item.get("tg_id")
    if username:
        return f"@{username}"
    if tg_id:
        return f'<a href="tg://user?id={tg_id}">{name}</a>'
    return name


def format_days_left_badge(days: int) -> str:
    """Формирует человекочитаемый бейдж оставшихся дней."""
    if days == 0:
        return "🎉 <b>СЕГОДНЯ!</b>"
    if days == 1:
        return "завтра"
    last_two = days % 100
    last_one = days % 10
    if 11 <= last_two <= 14:
        return f"через {days} дней"
    if last_one == 1:
        return f"через {days} день"
    if 2 <= last_one <= 4:
        return f"через {days} дня"
    return f"через {days} дней"


def format_single_birthday_row(item: Dict[str, Any]) -> str:
    """Форматирует одну строку в списке дней рождения."""
    d_str = f"{item['day']:02d}.{item['month']:02d}"
    mention = get_person_mention(item)
    badge = format_days_left_badge(item["days_until"])
    age = item["turning_age"]
    name = item["full_name"]
    tag_part = f" ({mention})" if mention != name else ""
    return f"▫️ <b>{d_str}</b> • {name}{tag_part} — <b>{badge}</b> (исполнится {age})"


def format_birthday_registry_text(items: List[Dict[str, Any]]) -> str:
    """Формирует красивый реестр дней рождения для закрепленного сообщения."""
    lines = [
        "🎂 <b>ДНИ РОЖДЕНИЯ ГРУППЫ 1-КПД-3</b>",
        "────────────────────────────"
    ]
    today_items = [i for i in items if i.get("is_today")]
    if today_items:
        lines.append("🎉 <b>СЕГОДНЯ ПРАЗДНУЮТ:</b>")
        for i in today_items:
            mention = get_person_mention(i)
            lines.append(f"▪️ <b>{i['full_name']}</b> ({mention}) — <b>{i['turning_age']} лет!</b> 🥳")
        lines.append("")
    lines.append("⏳ <b>БЛИЖАЙШИЕ ПРАЗДНИКИ:</b>")
    upcoming = [i for i in items if not i.get("is_today")]
    lines.extend(format_single_birthday_row(i) for i in upcoming)
    lines.append("\n<i>Бот ежедневно обновляет список и поздравляет в день праздника!</i>")
    return "\n".join(lines)


def pick_unique_wish(person_key: str, wishes: List[str]) -> str:
    """Выбирает случайное неповторяющееся поздравление для участника."""
    if not wishes:
        return "Желаем счастья, здоровья, успехов в учёбе и исполнения всех желаний!"
    history: Dict[str, List[int]] = load_json_file(HISTORY_FILE, {})
    used_indices = set(history.get(person_key, []))
    available = [idx for idx in range(len(wishes)) if idx not in used_indices]
    if not available:
        used_indices.clear()
        available = list(range(len(wishes)))
    choice_idx = random.choice(available)
    used_indices.add(choice_idx)
    history[person_key] = list(used_indices)
    save_json_file(HISTORY_FILE, history)
    return wishes[choice_idx]


async def send_congrats_for_item(item: Dict[str, Any], today_str: str) -> None:
    """Отправляет персональное поздравление в топик 'Важное' (ID: 2)."""
    congrats_state: Dict[str, bool] = load_json_file(CONGRATS_STATE_FILE, {})
    person_key = item["full_name"]
    congrats_key = f"{today_str}_{person_key}"
    if congrats_state.get(congrats_key):
        return
    wishes = load_json_file(WISHES_FILE, [])
    wish_text = pick_unique_wish(person_key, wishes)
    mention = get_person_mention(item)
    age = item.get("turning_age", 18)
    text = (
        f"🎉 {mention}, <b>с Днём Рождения!</b> 🎂\n"
        f"Тебе сегодня исполняется <b>{age} лет</b>!\n\n"
        f"<blockquote>{wish_text}</blockquote>\n\n"
        f"<i>Присоединяйтесь к поздравлениям в комментариях!</i> ✨"
    )
    try:
        await bot.send_message(
            chat_id=TOPIC_CHAT_ID,
            message_thread_id=IMPORTANT_TOPIC_THREAD_ID,
            text=text
        )
        congrats_state[congrats_key] = True
        save_json_file(CONGRATS_STATE_FILE, congrats_state)
        log.info(f"✅ Отправлено поздравление для {person_key} в топик {IMPORTANT_TOPIC_THREAD_ID}")
    except Exception as e:
        log.error(f"❌ Ошибка отправки поздравления для {person_key}: {e}")


async def check_and_send_birthday_congratulations(items: List[Dict[str, Any]], today: date) -> None:
    """Проверяет сегодняшних именинников и отправляет поздравления."""
    today_str = today.isoformat()
    for item in items:
        if item.get("is_today"):
            await send_congrats_for_item(item, today_str)


async def update_birthday_pinned_message(text: str) -> bool:
    """Обновляет или создает закрепленное сообщение в топике 'Дни рождения'."""
    state = load_json_file(STATE_FILE, {})
    main_msg_id = state.get("main_msg_id")
    if main_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=TOPIC_CHAT_ID, message_id=main_msg_id, text=text
            )
            log.debug(f"Реестр дней рождения обновлен: MSG_ID={main_msg_id}")
            return True
        except TelegramBadRequest as e:
            if "not modified" in str(e).lower():
                return True
            log.warning(f"Ошибка редактирования MSG_ID={main_msg_id} ({e}), пересоздаем...")
    try:
        msg = await bot.send_message(
            chat_id=TOPIC_CHAT_ID,
            message_thread_id=BIRTHDAY_TOPIC_THREAD_ID,
            text=text
        )
        save_json_file(STATE_FILE, {"main_msg_id": msg.message_id})
        try:
            await bot.pin_chat_message(chat_id=TOPIC_CHAT_ID, message_id=msg.message_id, disable_notification=True)
        except Exception as e:
            log.warning(f"Не удалось закрепить сообщение ДР: {e}")
        log.info(f"✅ Создано и закреплено сообщение ДР: MSG_ID={msg.message_id}")
        return True
    except Exception as e:
        log.error(f"❌ Ошибка отправки главного сообщения ДР: {e}")
        return False


async def sync_birthdays_topic() -> bool:
    """Основной цикл синхронизации реестра ДР и проверки поздравлений."""
    now_dt = datetime.now(TIMEZONE)
    today = now_dt.date()
    raw_birthdays: List[Dict[str, Any]] = load_json_file(BIRTHDAYS_FILE, [])
    if not raw_birthdays:
        log.warning("Список дней рождения пуст в data/birthdays.json")
        return False
    processed = [calculate_days_and_age(i, today) for i in raw_birthdays]
    processed.sort(key=lambda x: x["days_until"])
    await check_and_send_birthday_congratulations(processed, today)
    text = format_birthday_registry_text(processed)
    return await update_birthday_pinned_message(text)


async def birthday_sync_loop() -> None:
    """Фоновый цикл проверки дней рождения (каждые 30 минут)."""
    log.info("Запущен фоновый сервис дней рождения КТМУ")
    await asyncio.sleep(5)
    while True:
        try:
            await sync_birthdays_topic()
        except Exception as e:
            log.error(f"Ошибка в birthday_sync_loop: {e}")
        await asyncio.sleep(1800)
