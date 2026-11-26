"""
Модуль хэндлера общего пинга одногруппников (/all).

Позволяет администратору (ALLOWED_USER_ID) пинговать всех одногруппников
в любом топике группы от лица бота. Список одногруппников подтягивается
из единого источника birthdays.json.

Особенности реализации:
  1. Основной пост отправляется чистым (без портянки никнеймов).
  2. Упоминания разбиваются на пачки по PING_ALL_CHUNK_SIZE (до 5 человек)
     и отправляются отдельными сервисными ответами, чтобы гарантировать
     100% доставку push-уведомлений Telegram всем участникам.
  3. Для пользователей с username используется @username, без username —
     кликабельная ссылка <a href="tg://user?id=...">Имя</a>.
  4. Отправитель команды автоматически исключается из списка пинга.
  5. Исходное сообщение команды удаляется, пост публикуется от лица бота.
  6. Полностью сохраняется исходное HTML-форматирование автора поста.
"""

import asyncio
import html
import re
from typing import Any

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, User

from bot.filters.auth import AuthFilter
from config import BIRTHDAYS_FILE_PATH, PING_ALL_BATCH_DELAY, PING_ALL_CHUNK_SIZE
from core.logger import get_logger
from services.achievement_events import mark_ping_all
from services.user_cache import get_cached_user_id
from utils.storage import load_json

log = get_logger("admin_ping_all")
router = Router()
router.message.filter(AuthFilter())


async def load_classmates_list() -> list[dict[str, Any]]:
    """
    Загружает актуальный список одногруппников из файла birthdays.json.

    Использует единый источник правды data/birthdays.json для исключения дублирования.
    При отсутствии файла возвращает пустой список по умолчанию.

    Возвращает список словарей студентов с именами, username и tg_id.
    """
    return await load_json(BIRTHDAYS_FILE_PATH, default=[])


def resolve_person_tg_id(person: dict[str, Any]) -> int | None:
    """
    Извлекает Telegram ID из записи студента либо из кэша юзернеймов Redis.

    Защищает от пропуска упоминания, если tg_id отсутствует в статическом файле.
    Ищет по сохраненному username в реестре активности пользователей.

    Возвращает числовой Telegram ID или None, если не удалось найти.
    """
    if person.get("tg_id"):
        return person["tg_id"]

    username = person.get("username")
    return get_cached_user_id(username) if username else None


def format_mention_tag(person: dict[str, Any]) -> str | None:
    """
    Формирует видимый кликабельный тег студента для push-уведомления.

    Приоритет: @username для пользователей с юзернеймом,
    либо <a href="tg://user?id=...">Имя</a> для пользователей без него.

    Возвращает кликабельную строку упоминания или None, если нет данных.
    """
    username = person.get("username")
    if username:
        return f"@{username}"

    tg_id = resolve_person_tg_id(person)
    if tg_id:
        name = html.escape(person.get("full_name") or "Студент")
        return f'<a href="tg://user?id={tg_id}">{name}</a>'

    return None


def is_sender(person: dict[str, Any], sender_id: int | None, sender_username: str | None) -> bool:
    """
    Проверяет, является ли запись студента автором вызванной команды.

    Сравнивает как числовой Telegram ID, так и регистронезависимый username.
    Исключает самого администратора из списка пингуемых одногруппников.

    Возвращает True, если студент является автором команды, иначе False.
    """
    if sender_id and person.get("tg_id") == sender_id:
        return True

    return bool(sender_username and person.get("username") and person["username"].lower() == sender_username.lower())


def filter_classmates_to_ping(classmates: list[dict[str, Any]], sender: User | None) -> list[dict[str, Any]]:
    """
    Отбирает одногруппников для пинга, исключая автора команды.

    Фильтрует список студентов по id и username инициатора /all.

    Возвращает отфильтрованный список студентов для рассылки.
    """
    sender_id = sender.id if sender else None
    sender_user = sender.username if sender else None
    return [p for p in classmates if not is_sender(p, sender_id, sender_user)]


def chunk_classmates(
    classmates: list[dict[str, Any]],
    chunk_size: int = PING_ALL_CHUNK_SIZE,
) -> list[list[dict[str, Any]]]:
    """
    Разбивает список студентов на пачки фиксированного размера.

    Telegram доставляет push-уведомления максимум для 5 тегов в сообщении,
    поэтому пачки ограничиваются chunk_size (по умолчанию 5).

    Возвращает список пакетов одногруппников.
    """
    if chunk_size <= 0:
        return [classmates] if classmates else []
    return [classmates[i : i + chunk_size] for i in range(0, len(classmates), chunk_size)]


def format_chunk_message(chunk: list[dict[str, Any]]) -> str:
    """
    Форматирует одну пачку упоминаний в строку сервисного ответа.

    Объединяет валидные теги через пробел с эмодзи-префиксом.

    Возвращает готовую строку с тегами или пустую строку, если тегов нет.
    """
    tags = [format_mention_tag(p) for p in chunk]
    valid_tags = [t for t in tags if t]
    return f"👥 {' '.join(valid_tags)}" if valid_tags else ""


def extract_broadcast_text(html_text: str) -> str:
    """
    Извлекает пользовательский текст сообщения после команды /all или .all.

    Отрезает саму команду с префиксом (/ или .) и упоминанием юзернейма бота.
    Сохраняет исходное форматирование автора (жирный, курсив, ссылки).

    Возвращает очищенную HTML-строку пользовательского сообщения.
    """
    return re.sub(
        r"^[/.](?:all)(?:@[A-Za-z0-9_]+)?(?:\s+|$)",
        "",
        html_text,
        count=1,
        flags=re.IGNORECASE,
    ).strip()


def build_broadcast_message(user_html: str, has_reply: bool = False) -> str:
    """
    Компонует основной чистый текст поста без единого никнейма.

    Никнеймы отправляются отдельными сервисными ответами,
    чтобы основной пост оставался визуально чистым и лаконичным.

    Возвращает готовый HTML-текст для главного поста.
    """
    if user_html:
        return user_html

    if has_reply:
        return "📢 <b>Внимание к сообщению выше!</b>"

    return "📢 <b>Общий сбор группы!</b>"


async def safe_delete_command_message(message: Message) -> None:
    """
    Безопасно удаляет исходное командное сообщение администратора.

    Подавляет ошибки TelegramBadRequest, если сообщение уже удалено.
    Обеспечивает эффект публикации поста напрямую от лица бота.

    Ничего не возвращает.
    """
    try:
        await message.delete()
    except TelegramBadRequest as e:
        if "not found" in str(e).lower():
            log.debug("Сообщение с командой /all уже было удалено")
            return
        log.warning("Не удалось удалить команду /all: %s", e)
    except Exception as e:
        log.warning("Не удалось удалить команду /all: %s", e)


async def send_broadcast_payload(message: Message, final_html: str, reply_to_id: int | None) -> Message:
    """Отправляет пост от лица бота в целевой топик чата с сохранением вложений."""
    thread_id = message.message_thread_id
    if message.photo or message.video or message.document or message.animation:
        return await message.copy_to(
            chat_id=message.chat.id,
            message_thread_id=thread_id,
            caption=final_html,
            parse_mode="HTML",
            reply_to_message_id=reply_to_id,
        )

    return await message.bot.send_message(
        chat_id=message.chat.id,
        message_thread_id=thread_id,
        text=final_html,
        parse_mode="HTML",
        reply_to_message_id=reply_to_id,
    )


async def send_mention_batch(
    message: Message,
    chat_id: int,
    thread_id: int | None,
    reply_to_id: int,
    batch_text: str,
) -> None:
    """
    Отправляет одну пачку упоминаний как реплай на основной пост.

    Каждая пачка содержит до 5 участников, обеспечивая push от Telegram.

    Ничего не возвращает.
    """
    try:
        await message.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=batch_text,
            parse_mode="HTML",
            reply_to_message_id=reply_to_id,
        )
    except Exception as e:
        log.warning("Не удалось отправить пачку упоминаний /all: %s", e)


async def dispatch_mention_batches(
    message: Message,
    main_msg_id: int,
    chunks: list[list[dict[str, Any]]],
) -> None:
    """
    Последовательно отправляет пачки упоминаний с микропаузой.

    Микропауза PING_ALL_BATCH_DELAY предотвращает Telegram FloodWait
    и гарантирует отдельную генерацию push-уведомлений.

    Ничего не возвращает.
    """
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    for chunk in chunks:
        batch_text = format_chunk_message(chunk)
        if not batch_text:
            continue
        await send_mention_batch(message, chat_id, thread_id, main_msg_id, batch_text)
        await asyncio.sleep(PING_ALL_BATCH_DELAY)


async def validate_group_chat(message: Message) -> bool:
    """
    Проверяет, что команда /all вызвана в группе или супергруппе колледжа.

    При ошибочном вызове в ЛС выводит подсказку и останавливает выполнение.
    Защищает от бессмысленного пинга студентов в личной переписке.

    Возвращает True, если чат групповой, иначе False.
    """
    if message.chat.type == "private":
        await message.answer("⚠️ Команда /all предназначена для вызова в топиках группы.")
        return False

    return True


def compose_broadcast_content(message: Message) -> tuple[str, int | None]:
    """
    Формирует чистый текст поста и извлекает ID сообщения для реплая.

    Не добавляет никнеймы в текст — они отправляются отдельными пачками.
    Учитывает контекст ответа на чужое сообщение в топике.

    Возвращает кортеж (final_html_text, reply_message_id).
    """
    user_html = extract_broadcast_text(message.html_text or "")
    reply_id = message.reply_to_message.message_id if message.reply_to_message else None
    final_text = build_broadcast_message(user_html, has_reply=bool(reply_id))

    return final_text, reply_id


async def run_broadcast_pipeline(
    message: Message,
    final_text: str,
    reply_id: int | None,
    classmates: list[dict[str, Any]],
) -> None:
    """Выполняет отправку главного поста и пакетов упоминаний."""
    sent_msg = await send_broadcast_payload(message, final_text, reply_id)
    await safe_delete_command_message(message)
    ping_list = filter_classmates_to_ping(classmates, message.from_user)
    chunks = chunk_classmates(ping_list, PING_ALL_CHUNK_SIZE)
    await dispatch_mention_batches(message, sent_msg.message_id, chunks)
    await mark_ping_all()
    log.info("✅ Успешный пинг всех в чате %s (пачек: %s)", message.chat.id, len(chunks))


async def dispatch_broadcast(
    message: Message,
    final_text: str,
    reply_id: int | None,
    classmates: list[dict[str, Any]],
) -> None:
    """Запускает рассылку с перехватом ошибок и уведомлением администратора."""
    try:
        await run_broadcast_pipeline(message, final_text, reply_id, classmates)
    except Exception as e:
        log.error("❌ Ошибка отправки /all в чате %s: %s", message.chat.id, e)
        await message.answer(f"❌ Ошибка отправки сообщения: {html.escape(str(e))}")


@router.message(Command("all", prefix="/.", ignore_case=True))
async def cmd_ping_all(message: Message) -> None:
    """
    Оркестрирует полный сценарий общего пинга группы 1-КПД-3 по команде /all.

    Проверяет тип чата, загружает реестр студентов и отправляет публикацию.
    Не содержит смешения низкоуровневых операций форматирования.

    Ничего не возвращает.
    """
    if not await validate_group_chat(message):
        return

    classmates = await load_classmates_list()
    final_text, reply_id = compose_broadcast_content(message)
    await dispatch_broadcast(message, final_text, reply_id, classmates)
