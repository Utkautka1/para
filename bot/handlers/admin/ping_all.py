"""
Модуль хэндлера общего пинга одногруппников (/all).

Позволяет администратору (ALLOWED_USER_ID) пинговать всех одногруппников
в любом топике группы от лица бота. Список одногруппников подтягивается
из единого источника birthdays.json.

Особенности реализации:
  1. Теги упоминаний прикрепляются открытым текстом внизу сообщения без
     спойлеров для мгновенной видимости и отправки push-уведомлений.
  2. Для пользователей с username используется @username, без username —
     кликабельная ссылка <a href="tg://user?id=...">Имя</a>.
  3. Отправитель команды автоматически исключается из пинга.
  4. Исходное сообщение команды удаляется, пост отправляется от лица бота.
  5. Полностью сохраняется исходное HTML-форматирование автора (жирный, курсив, ссылки).
  6. Поддерживается ответ на сообщение (reply) и медиафайлы с подписью.
"""

import html
import re
from typing import Any

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, User

from bot.filters.auth import AuthFilter
from config import BIRTHDAYS_FILE_PATH
from core.logger import get_logger
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
    Формирует активный HTML-тег кликабельного упоминания студента.

    Отдаёт абсолютный приоритет tg://user?id=, так как Telegram шлёт пуш
    только по ID, а простые @username от ботов зачастую игнорирует.

    Возвращает HTML-ссылку упоминания или @username, либо None.
    """

    tg_id = resolve_person_tg_id(person)
    username = person.get("username")
    name = html.escape(person.get("full_name", ""))

    if tg_id:
        label = f"@{username}" if username else name
        return f'<a href="tg://user?id={tg_id}">{label}</a>'

    if username:
        return f"@{username}"

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


def build_mentions_block(classmates: list[dict[str, Any]], sender: User | None) -> str:
    """
    Формирует единую строку кликабельных упоминаний одногруппников без автора.

    Объединяет валидные теги через пробел в единый текстовый блок.
    Используется в нижней части широковещательного сообщения.

    Возвращает строку со всеми тегами упоминаний.
    """

    sender_id = sender.id if sender else None
    sender_user = sender.username if sender else None
    tags = [format_mention_tag(p) for p in classmates if not is_sender(p, sender_id, sender_user)]
    valid_tags = [t for t in tags if t]

    return " ".join(valid_tags)


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


def build_broadcast_message(user_html: str, mentions: str, has_reply: bool = False) -> str:
    """
    Компонует итоговый HTML-текст поста с текстом автора и пингами внизу.

    Подставляет подходящий заголовок по умолчанию при пустом тексте сообщения.
    Разделяет текст автора и теги упоминаний двойным переводом строки.

    Возвращает готовый HTML-текст для рассылки.
    """

    if user_html:
        return f"{user_html}\n\n{mentions}"

    if has_reply:
        return f"📢 <b>Внимание к сообщению выше!</b>\n\n{mentions}"

    return f"📢 <b>Общий сбор группы!</b>\n\n{mentions}"


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
        log.warning(f"Не удалось удалить команду /all: {e}")
    except Exception as e:
        log.warning(f"Не удалось удалить команду /all: {e}")


async def send_broadcast_payload(message: Message, final_html: str, reply_to_id: int | None) -> Message:
    """
    Отправляет пост от лица бота в целевой топик чата с сохранением вложений.

    При наличии фото, видео или документа копирует медиафайл с новым текстом.
    Поддерживает сохранение связи с сообщением-ответом (reply_to_message_id).

    Возвращает отправленный объект Message.
    """

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


def compose_broadcast_content(classmates: list[dict[str, Any]], message: Message) -> tuple[str, int | None]:
    """
    Формирует итоговый HTML-текст рассылки и извлекает ID сообщения для реплая.

    Соединяет авторский текст сообщения с кликабельным блоком упоминаний.
    Учитывает контекст ответа на чужое сообщение в топике.

    Возвращает кортеж (final_html_text, reply_message_id).
    """

    mentions = build_mentions_block(classmates, message.from_user)
    user_html = extract_broadcast_text(message.html_text or "")
    reply_id = message.reply_to_message.message_id if message.reply_to_message else None
    final_text = build_broadcast_message(user_html, mentions, has_reply=bool(reply_id))

    return final_text, reply_id


async def dispatch_broadcast(message: Message, final_text: str, reply_id: int | None) -> None:
    """
    Отправляет широковещательный пост в чат и удаляет триггер-сообщение.

    Логирует успешную отправку с идентификатором чата и топика.
    В случае ошибки отправки информирует администратора в чате.

    Ничего не возвращает.
    """

    try:
        await send_broadcast_payload(message, final_text, reply_id)
        await safe_delete_command_message(message)
        log.info(f"✅ Успешный пинг всех в чате {message.chat.id}, топик {message.message_thread_id}")
    except Exception as e:
        log.error(f"❌ Ошибка отправки /all в чате {message.chat.id}: {e}")
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
    final_text, reply_id = compose_broadcast_content(classmates, message)
    await dispatch_broadcast(message, final_text, reply_id)
