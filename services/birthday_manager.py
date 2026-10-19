"""
Менеджер дней рождения группы 1-КПД-3.

Отвечает за:
  1. Синхронизацию закрепленного реестра дней рождения в топике 6269.
  2. Ежедневный пересчет дней до праздника и исполняющегося возраста.
  3. Отправку персональных поздравлений в топик «Важное» (ID: 2).
"""

import asyncio
import random
from datetime import date, datetime
from typing import Any

from aiogram.exceptions import TelegramBadRequest

from config import (
    BIRTHDAY_TOPIC_STATE_FILE,
    BIRTHDAY_TOPIC_THREAD_ID,
    BIRTHDAYS_FILE_PATH,
    CONGRATS_STATE_FILE_PATH,
    HISTORY_FILE_PATH,
    IMPORTANT_TOPIC_THREAD_ID,
    SEASONS_INFO,
    STAROSTA_HISTORY_FILE_PATH,
    STAROSTA_WISHES_FILE_PATH,
    TIMEZONE,
    TOPIC_CHAT_ID,
    WISHES_FILE_PATH,
)
from core.bot import bot
from core.logger import get_logger
from utils.storage import sync_atomic_save_json as save_json_file
from utils.storage import sync_load_json as load_json_file

log = get_logger("birthday_manager")

BIRTHDAYS_FILE = BIRTHDAYS_FILE_PATH
WISHES_FILE = WISHES_FILE_PATH
STAROSTA_WISHES_FILE = STAROSTA_WISHES_FILE_PATH
STATE_FILE = BIRTHDAY_TOPIC_STATE_FILE
HISTORY_FILE = HISTORY_FILE_PATH
STAROSTA_HISTORY_FILE = STAROSTA_HISTORY_FILE_PATH
CONGRATS_STATE_FILE = CONGRATS_STATE_FILE_PATH


def _compute_next_birthday(today: date, b_day: int, b_month: int) -> tuple[int, bool, int]:
    """
    Рассчитывает количество дней до ближайшего дня рождения с учетом високосных лет.

    Корректирует даты 29 февраля в невисокосные годы до 28 февраля и переносит
    расчет на следующий календарный год, если праздник в текущем году уже прошел.

    Возвращает кортеж (days_until, is_today, target_year).
    """
    try:
        bday_this_year = date(today.year, b_month, b_day)
    except ValueError:
        bday_this_year = date(today.year, b_month, 28)
    if bday_this_year < today:
        try:
            next_bday = date(today.year + 1, b_month, b_day)
        except ValueError:
            next_bday = date(today.year + 1, b_month, 28)
        return (next_bday - today).days, False, today.year + 1
    if bday_this_year == today:
        return 0, True, today.year
    return (bday_this_year - today).days, False, today.year


def calculate_days_and_age(item: dict[str, Any], today: date) -> dict[str, Any]:
    """
    Вычисляет оставшиеся дни до дня рождения и возраст, исполняющийся в праздник.

    Определяет статус 'is_today' для активации праздничных плашек и рассчитывает
    точный возраст именинника относительно года рождения.

    Возвращает обогащенную копию словаря item с полями days_until, turning_age, is_today.
    """
    days, is_today, target_year = _compute_next_birthday(today, item["day"], item["month"])
    age = target_year - item["year"]
    return {**item, "days_until": days, "turning_age": age, "is_today": is_today}


def format_person_tag(item: dict[str, Any]) -> str:
    """
    Формирует кликабельное имя человека для реестра Telegram.

    Использует публичный @username при наличии или постоянную HTML-ссылку
    tg://user?id= для пользователей, зафиксировавших свой цифровой идентификатор.

    Возвращает форматированную HTML-строку упоминания.
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
    Формирует понятный бейдж оставшихся дней с правильным русским склонением.

    Обрабатывает особые случаи 'сегодня', 'завтра' и правила грамматики
    (1 день, 2-4 дня, 5-20 дней).

    Возвращает текстовую строку обратного отсчета.
    """
    if days == 0:
        return "сегодня"
    if days == 1:
        return "завтра"
    last_two, last_one = days % 100, days % 10
    if 11 <= last_two <= 14:
        return f"через {days} дней"
    if last_one == 1:
        return f"через {days} день"
    if 2 <= last_one <= 4:
        return f"через {days} дня"
    return f"через {days} дней"


def format_today_block(today_items: list[dict[str, Any]]) -> list[str]:
    """
    Формирует праздничный блок в HTML-цитате для именинников сегодняшнего дня.

    Отображает поздравление вверху реестра с эмодзи и исполняющимся возрастом.

    Возвращает список строк разметки или пустой список при отсутствии именинников сегодня.
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
    Склоняет возраст человека по правилам русского языка (год / года / лет).

    Применяется в списках именинников для корректной грамматики.

    Возвращает строку вида '18 лет', '21 год', '22 года'.
    """
    last_two, last_one = age % 100, age % 10
    if 11 <= last_two <= 14:
        return f"{age} лет"
    if last_one == 1:
        return f"{age} год"
    if 2 <= last_one <= 4:
        return f"{age} года"
    return f"{age} лет"


def format_upcoming_block(items: list[dict[str, Any]]) -> list[str]:
    """
    Формирует блок ближайших именинников в цитате Telegram.

    Отбирает праздники в пределах 45 дней (или гарантированно минимум 3 ближайших),
    исключая сегодняшних именинников.

    Возвращает список форматированных строк блока или пустой список.
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


def season_sort_key(item: dict[str, Any], months: list[int]) -> int:
    """
    Вычисляет целочисленный индекс сортировки даты внутри заданного сезона.

    Обеспечивает естественный хронологический порядок отображения дней рождения
    (например, декабрь -> январь -> февраль для зимы).

    Возвращает числовой ключ сортировки.
    """
    return months.index(item["month"]) * 100 + item["day"]


def format_season_block(title: str, months: list[int], all_items: list[dict[str, Any]]) -> list[str]:
    """
    Форматирует сезонный блок именинников (осень, зима, весна, лето).

    Сортирует участников по датам внутри сезона и генерирует аккуратные строки списка.

    Возвращает список строк форматированного сезонного раздела.
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


def format_birthday_registry_text(items: list[dict[str, Any]]) -> str:
    """
    Собирает полный итоговый текст закрепленного сообщения реестра дней рождения.

    Включает шапку, блок сегодняшних именинников, ближайшие праздники и поквартальную
    раскладку по временам года из SEASONS_INFO.

    Возвращает готовую HTML-строку для отправки в топик.
    """
    lines = ["🎂 <b>ДНИ РОЖДЕНИЯ ГРУППЫ 1-КПД-3</b>", "────────────────────────────"]
    lines.extend(format_today_block([i for i in items if i.get("is_today")]))
    lines.extend(format_upcoming_block(items))
    for title, months in SEASONS_INFO:
        lines.extend(format_season_block(title, months, items))
    lines.append("────────────────────────────")
    lines.append("<i>🔄 Бот ежедневно обновляет реестр и поздравляет в 07:00</i>")
    return "\n".join(lines).strip()


def pick_unique_wish(person_key: str, wishes: list[str], history_file: str = HISTORY_FILE) -> str:
    """
    Выбирает случайное неповторяющееся поздравление для участника.

    Ведет локальную историю использованных индексов, сбрасывая ее при полном
    исчерпании доступных вариантов для предотвращения повторов поздравлений.

    Возвращает строку с выбранным текстом пожелания.
    """
    if not wishes:
        return "Желаем счастья, здоровья, успехов в учёбе и исполнения всех желаний!"
    history: dict[str, list[int]] = load_json_file(history_file, {})
    used_indices = set(history.get(person_key, []))
    available = [idx for idx in range(len(wishes)) if idx not in used_indices]
    if not available:
        used_indices.clear()
        available = list(range(len(wishes)))
    choice_idx = random.choice(available)  # nosec B311
    used_indices.add(choice_idx)
    history[person_key] = list(used_indices)
    save_json_file(history_file, history)
    return wishes[choice_idx]


def get_person_mention(item: dict[str, Any]) -> str:
    """
    Формирует кликабельное упоминание именинника для персонального поздравления.

    Использует @username для отправки уведомления или гиперссылку tg://user?id
    по сохраненному аппаратному идентификатору Telegram.

    Возвращает строку с тегом упоминания или именем студента.
    """
    username = item.get("username")
    tg_id = item.get("tg_id")
    if username:
        return f"@{username}"
    if tg_id:
        return f'<a href="tg://user?id={tg_id}">{item["full_name"]}</a>'
    return item["full_name"]


def format_starosta_block(starosta_text: str | None) -> str:
    """
    Формирует цитату с напутственным словом старосты группы.

    Оформляет отдельный блок пожелания от старосты в HTML-тег blockquote
    для визуального выделения в ленте топика.

    Возвращает форматированную строку или пустую строку при отсутствии текста.
    """
    if not starosta_text:
        return ""
    return f"👑 <b>Слово старосты:</b>\n<blockquote>«{starosta_text}»</blockquote>"


def format_congrats_message(item: dict[str, Any], wish_text: str, starosta_text: str | None = None) -> str:
    """
    Формирует праздничное персональное поздравление от имени группы и старосты.

    Автоматически адаптирует текст, если именинником является сам староста,
    и призывает одногруппников перейти в топик 'Флудилка' для поздравлений.

    Возвращает готовый HTML-текст праздничной публикации.
    """
    mention = get_person_mention(item)
    name = item["full_name"]
    age = item.get("turning_age", 18)
    is_starosta = name == "Стрыгин Дмитрий"
    s_block = format_starosta_block(None if is_starosta else starosta_text)
    mid = f"{s_block}\n\n" if s_block else ""
    call = "нашего старосту" if is_starosta else "виновника торжества"
    return (
        f"🥳 <b>Внимание, 1-КПД-3! Сегодня особенный день!</b>\n\n"
        f"Свой {age}-й день рождения отмечает <b>{name}</b> ({mention})! 🔥\n\n"
        f"<blockquote>{wish_text}</blockquote>\n\n"
        f"{mid}"
        f"💬 <i>Ребята, переходим в топик <b>Флудилка</b> и от души поздравляем {call}!</i> 🎉"
    )


async def _send_congrats_telegram(text: str, person_key: str, key: str, state: dict[str, bool]) -> None:
    """
    Отправляет поздравление в топик 'Важное' и сохраняет флаг доставки.

    Фиксирует факт отправки в файле состояния, гарантируя идемпотентность
    и предотвращая повторный спам поздравлением в течение дня.

    Ничего не возвращает.
    """
    try:
        await bot.send_message(chat_id=TOPIC_CHAT_ID, message_thread_id=IMPORTANT_TOPIC_THREAD_ID, text=text)
        state[key] = True
        save_json_file(CONGRATS_STATE_FILE, state)
        log.info(f"✅ Отправлено поздравление для {person_key} в топик {IMPORTANT_TOPIC_THREAD_ID}")
    except Exception as e:
        log.error(f"❌ Ошибка отправки поздравления для {person_key}: {e}")


async def send_congrats_for_item(item: dict[str, Any], today_str: str) -> None:
    """
    Оркестрирует отправку персонального поздравления для именинника.

    Проверяет реестр отправленных поздравлений за текущий день, подбирает
    уникальные пожелания и инициирует публикацию в Telegram.

    Ничего не возвращает.
    """
    congrats_state: dict[str, bool] = load_json_file(CONGRATS_STATE_FILE, {})
    person_key = item["full_name"]
    congrats_key = f"{today_str}_{person_key}"
    if congrats_state.get(congrats_key):
        return
    wishes = load_json_file(WISHES_FILE, [])
    s_wishes = load_json_file(STAROSTA_WISHES_FILE, [])
    wish = pick_unique_wish(person_key, wishes, HISTORY_FILE)
    s_wish = pick_unique_wish(person_key, s_wishes, STAROSTA_HISTORY_FILE)
    text = format_congrats_message(item, wish, s_wish)
    await _send_congrats_telegram(text, person_key, congrats_key, congrats_state)


def is_morning_congrats_time(now_dt: datetime) -> bool:
    """
    Проверяет наступление утреннего времени отправки поздравлений (07:00 МСК).

    Предотвращает ночные уведомления участников группы о праздниках.

    Возвращает True, если текущее время 07:00 или позже, иначе False.
    """
    return now_dt.hour >= 7


async def check_and_send_birthday_congratulations(items: list[dict[str, Any]], today: date) -> None:
    """
    Проверяет сегодняшних именинников и отправляет поздравления строго с 07:00.

    Сканирует подготовленный список студентов с флагом is_today и запускает
    отправку сообщений при наступлении утреннего времени.

    Ничего не возвращает.
    """
    now_dt = datetime.now(TIMEZONE)
    if not is_morning_congrats_time(now_dt):
        log.debug(f"Поздравления с ДР ожидают наступления 07:00 (сейчас {now_dt.strftime('%H:%M')})")
        return
    today_str = today.isoformat()
    for item in items:
        if item.get("is_today"):
            await send_congrats_for_item(item, today_str)


async def _edit_existing_birthday_message(msg_id: int, text: str) -> bool:
    """
    Редактирует существующее закрепленное сообщение реестра дней рождения.

    Перехватывает ошибку 'message is not modified' без создания ложных предупреждений,
    сообщая о необходимости пересоздания при удалении сообщения пользователем.

    Возвращает True в случае успеха, False при необходимости пересоздать пост.
    """
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
    """
    Публикует и закрепляет новое сообщение реестра дней рождения в топике.

    Отправляет пост в целевой thread, сохраняет его ID в файл состояния
    и закрепляет без звукового уведомления участников.

    Возвращает True при успешной отправке, False при ошибке Telegram API.
    """
    try:
        msg = await bot.send_message(chat_id=TOPIC_CHAT_ID, message_thread_id=BIRTHDAY_TOPIC_THREAD_ID, text=text)
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
    """
    Оркестрирует обновление или повторное создание закрепленного сообщения реестра.

    Сверяет ID из файла состояния: сначала пытается отредактировать старый пост,
    а при невозможности создает новый и закрепляет его.

    Возвращает True при успешной синхронизации сообщения.
    """
    state = load_json_file(STATE_FILE, {})
    main_msg_id = state.get("main_msg_id")
    if main_msg_id and await _edit_existing_birthday_message(main_msg_id, text):
        return True
    return await _create_new_birthday_message(text)


async def sync_birthdays_topic() -> bool:
    """
    Выполняет полный цикл синхронизации реестра дней рождения и отправки поздравлений.

    Считывает список студентов из birthdays.json, пересчитывает дни до праздника,
    триггерит поздравления и обновляет закрепленное сообщение в топике.

    Возвращает True в случае успешной публикации, иначе False.
    """
    now_dt = datetime.now(TIMEZONE)
    today = now_dt.date()
    raw_birthdays: list[dict[str, Any]] = load_json_file(BIRTHDAYS_FILE, [])
    if not raw_birthdays:
        log.warning("Список дней рождения пуст в data/birthdays.json")
        return False
    processed = [calculate_days_and_age(i, today) for i in raw_birthdays]
    processed.sort(key=lambda x: x["days_until"])
    await check_and_send_birthday_congratulations(processed, today)
    text = format_birthday_registry_text(processed)
    return await update_birthday_pinned_message(text)


async def birthday_sync_loop() -> None:
    """
    Запускает бесконечный цикл фоновой синхронизации дней рождения (каждые 30 минут).

    Обеспечивает своевременную смену даты и утреннее поздравление в 07:00 МСК
    с обработкой непредвиденных исключений без падения процесса.

    Ничего не возвращает (работает до завершения приложения).
    """
    log.info("Запущен фоновый сервис дней рождения КТМУ")
    await asyncio.sleep(5)
    while True:
        try:
            await sync_birthdays_topic()
        except Exception as e:
            log.error(f"Ошибка в birthday_sync_loop: {e}")
        await asyncio.sleep(1800)
