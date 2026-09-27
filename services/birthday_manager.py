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


from utils.storage import sync_atomic_save_json as save_json_file, sync_load_json as load_json_file


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


SEASONS_INFO = [
    ("🍂 ОСЕНЬ", [9, 10, 11]),
    ("❄️ ЗИМА", [12, 1, 2]),
    ("🌸 ВЕСНА", [3, 4, 5]),
    ("☀️ ЛЕТО", [6, 7, 8]),
]


def format_person_tag(item: Dict[str, Any]) -> str:
    """
    Формирует кликабельное имя человека (через username или tg://user?id).
    """
    name = item["full_name"]
    username = item.get("username")
    tg_id = item.get("tg_id")
    if username:
        return f"{name} (@{username})"
    if tg_id:
        return f'<a href="tg://user?id={tg_id}">{name}</a>'
    return name


def format_days_left_badge(days: int) -> str:
    """
    Формирует человекочитаемый бейдж оставшихся дней.
    """
    if days == 0:
        return "сегодня"
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


def format_today_block(today_items: List[Dict[str, Any]]) -> List[str]:
    """
    Формирует праздничный блок для именинников сегодняшнего дня.
    """
    if not today_items:
        return []
    lines = ["🎉 <b>СЕГОДНЯ ДЕНЬ РОЖДЕНИЯ!</b>", "<blockquote>"]
    for i in today_items:
        tag = format_person_tag(i)
        lines.append(f"🎂 <b>{tag}</b> — исполняется <b>{i['turning_age']} лет!</b> 🥳")
    lines.append("</blockquote>\n")
    return lines


def format_age_badge(age: int) -> str:
    """
    Формирует строку возраста с правильным склонением (лет/год/года).
    """
    last_two = age % 100
    last_one = age % 10
    if 11 <= last_two <= 14:
        return f"{age} лет"
    if last_one == 1:
        return f"{age} год"
    if 2 <= last_one <= 4:
        return f"{age} года"
    return f"{age} лет"


def format_upcoming_block(items: List[Dict[str, Any]]) -> List[str]:
    """
    Формирует блок ближайших именинников в цитате.
    """
    upcoming = [i for i in items if not i.get("is_today")]
    near = [i for i in upcoming if i["days_until"] <= 45]
    if len(near) < 3:
        near = upcoming[:3]
    if not near:
        return []

    lines = ["<blockquote>⏳ <b>БЛИЖАЙШИЕ ПРАЗДНИКИ:</b>"]
    for i in near:
        d_str = f"{i['day']:02d}.{i['month']:02d}"
        tag = format_person_tag(i)
        badge = format_days_left_badge(i["days_until"])
        age_str = format_age_badge(i["turning_age"])
        lines.append(f"▫️ <b>{d_str}</b> • {tag} — <b>{age_str}</b> ({badge})")
    lines.append("</blockquote>\n")
    return lines


def season_sort_key(item: Dict[str, Any], months: List[int]) -> int:
    """
    Вычисляет индекс сортировки даты внутри сезона.
    """
    return months.index(item["month"]) * 100 + item["day"]


def format_season_block(title: str, months: List[int], all_items: List[Dict[str, Any]]) -> List[str]:
    """
    Форматирует список именинников для одного сезона с указанием возраста.
    """
    s_items = [i for i in all_items if i["month"] in months]
    s_items.sort(key=lambda x: season_sort_key(x, months))
    if not s_items:
        return []

    lines = [f"<b>{title}</b>"]
    for i in s_items:
        d_str = f"{i['day']:02d}.{i['month']:02d}"
        tag = format_person_tag(i)
        age_str = format_age_badge(i["turning_age"])
        lines.append(f"▫️ <b>{d_str}</b> • {tag} — {age_str}")
    lines.append("")
    return lines


def format_birthday_registry_text(items: List[Dict[str, Any]]) -> str:
    """
    Формирует двухуровневый реестр дней рождения с сезонами и ближайшими.
    """
    lines = [
        "🎂 <b>ДНИ РОЖДЕНИЯ ГРУППЫ 1-КПД-3</b>",
        "────────────────────────────"
    ]
    lines.extend(format_today_block([i for i in items if i.get("is_today")]))
    lines.extend(format_upcoming_block(items))

    for title, months in SEASONS_INFO:
        lines.extend(format_season_block(title, months, items))

    lines.append("────────────────────────────")
    lines.append("<i>🔄 Бот ежедневно обновляет реестр и поздравляет в 09:00</i>")
    return "\n".join(lines).strip()


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


def get_person_mention(item: Dict[str, Any]) -> str:
    """
    Формирует кликабельное упоминание для персонального поздравления.
    """
    username = item.get("username")
    tg_id = item.get("tg_id")
    if username:
        return f"@{username}"
    if tg_id:
        return f'<a href="tg://user?id={tg_id}">{item["full_name"]}</a>'
    return item["full_name"]


def format_congrats_message(item: Dict[str, Any], wish_text: str) -> str:
    """
    Формирует HTML-текст поздравления с Днем Рождения.
    """
    mention = get_person_mention(item)
    age = item.get("turning_age", 18)
    return (
        f"🎉 {mention}, <b>с Днём Рождения!</b> 🎂\n"
        f"Тебе сегодня исполняется <b>{age} лет</b>!\n\n"
        f"<blockquote>{wish_text}</blockquote>\n\n"
        f"<i>Присоединяйтесь к поздравлениям в комментариях!</i> ✨"
    )


async def send_congrats_for_item(item: Dict[str, Any], today_str: str) -> None:
    """Отправляет персональное поздравление в топик 'Важное' (ID: 2)."""
    congrats_state: Dict[str, bool] = load_json_file(CONGRATS_STATE_FILE, {})
    person_key = item["full_name"]
    congrats_key = f"{today_str}_{person_key}"
    if congrats_state.get(congrats_key):
        return
    wishes = load_json_file(WISHES_FILE, [])
    text = format_congrats_message(item, pick_unique_wish(person_key, wishes))
    try:
        await bot.send_message(
            chat_id=TOPIC_CHAT_ID, message_thread_id=IMPORTANT_TOPIC_THREAD_ID, text=text
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


async def _edit_existing_birthday_message(msg_id: int, text: str) -> bool:
    """Пытается отредактировать существующее сообщение реестра ДР."""
    try:
        await bot.edit_message_text(chat_id=TOPIC_CHAT_ID, message_id=msg_id, text=text)
        log.debug(f"Реестр дней рождения обновлен: MSG_ID={msg_id}")
        return True
    except TelegramBadRequest as e:
        if "not modified" in str(e).lower():
            return True
        log.warning(f"Ошибка редактирования MSG_ID={msg_id} ({e}), пересоздаем...")
        return False


async def _create_new_birthday_message(text: str) -> bool:
    """Создает новое сообщение реестра ДР и закрепляет его без звука."""
    try:
        msg = await bot.send_message(
            chat_id=TOPIC_CHAT_ID, message_thread_id=BIRTHDAY_TOPIC_THREAD_ID, text=text
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


async def update_birthday_pinned_message(text: str) -> bool:
    """Обновляет существующее или создает новое закрепленное сообщение реестра ДР."""
    state = load_json_file(STATE_FILE, {})
    main_msg_id = state.get("main_msg_id")
    if main_msg_id and await _edit_existing_birthday_message(main_msg_id, text):
        return True
    return await _create_new_birthday_message(text)


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
