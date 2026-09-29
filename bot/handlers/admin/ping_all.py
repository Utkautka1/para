"""
Модуль хэндлера общего пинга одногруппников (/all).

Позволяет администратору (ALLOWED_USER_ID) пинговать всех одногруппников
в любом топике группы от лица бота. Список одногруппников подтягивается
из единого источника data/birthdays.json.

Особенности реализации:
  1. Теги упаковываются в Telegram-спойлер (<tg-spoiler>), чтобы не спамить
     простыней текста, при этом каждый упомянутый получает уведомление.
  2. Для пользователей с username используется @username, без username —
     кликабельная ссылка <a href="tg://user?id=...">Имя</a>.
  3. Отправитель команды автоматически исключается из пинга.
  4. Исходное сообщение команды удаляется, пост отправляется от лица бота.
  5. Полностью сохраняется исходное HTML-форматирование автора (жирный, курсив, ссылки).
  6. Поддерживается ответ на сообщение (reply) и медиафайлы с подписью.
"""

import html
import re
from typing import Any, Dict, List, Optional
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, User
from bot.filters.auth import AuthFilter
from core.logger import get_logger
from services.user_cache import get_cached_user_id
from utils.storage import load_json

log = get_logger("admin_ping_all")
router = Router()
router.message.filter(AuthFilter())

BIRTHDAYS_FILE_PATH = "data/birthdays.json"


async def load_classmates_list() -> List[Dict[str, Any]]:
    """
    Загружает актуальный список одногруппников из JSON-файла.

    Используем data/birthdays.json как единый источник правды, чтобы не дублировать
    данные студентов в разных файлах.
    """
    return await load_json(BIRTHDAYS_FILE_PATH, default=[])


def resolve_person_tg_id(person: Dict[str, Any]) -> Optional[int]:
    """
    Извлекает tg_id из записи или постоянного кэша пользователей.
    """
    if person.get("tg_id"):
        return person["tg_id"]
    username = person.get("username")
    return get_cached_user_id(username) if username else None


def format_mention_tag(person: Dict[str, Any]) -> Optional[str]:
    """
    Формирует кликабельный тег упоминания.

    Приоритет отдается tg_id: Telegram шлет пуш-уведомление ТОЛЬКО для
    ссылок tg://user?id= (text_mention), а обычный @username ботом игнорирует.
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


def is_sender(person: Dict[str, Any], sender_id: Optional[int], sender_username: Optional[str]) -> bool:
    """
    Проверяет, является ли запись в реестре отправителем команды.

    Сверяет как по числовому Telegram ID, так и по регистронезависимому юзернейму.
    """
    if sender_id and person.get("tg_id") == sender_id:
        return True
    if sender_username and person.get("username"):
        if person["username"].lower() == sender_username.lower():
            return True
    return False


def build_mentions_block(classmates: List[Dict[str, Any]], sender: Optional[User]) -> str:
    """
    Формирует список тегов упоминаний участников чата без автора команды.
    """
    sender_id = sender.id if sender else None
    sender_user = sender.username if sender else None
    tags = [
        format_mention_tag(p)
        for p in classmates
        if not is_sender(p, sender_id, sender_user)
    ]
    valid_tags = [t for t in tags if t]
    return " ".join(valid_tags)


def extract_broadcast_text(html_text: str) -> str:
    """
    Извлекает пользовательский HTML-текст после команды /all или .all.

    Отрезает саму команду с префиксом (/ или .) и упоминанием бота, сохраняя
    все дочерние теги разметки (жирный, курсив, ссылки, моноширинный).
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
    Собирает итоговый HTML: текст автора сверху, блок пингов в самом низу.
    """
    if user_html:
        return f"{user_html}\n\n{mentions}"
    if has_reply:
        return f"📢 <b>Внимание к сообщению выше!</b>\n\n{mentions}"
    return f"📢 <b>Общий сбор группы!</b>\n\n{mentions}"


async def safe_delete_command_message(message: Message) -> None:
    """
    Безопасно удаляет триггер-сообщение автора команды.

    Игнорирует ошибки, если сообщение уже удалено пользователем или таймером.
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


async def send_broadcast_payload(message: Message, final_html: str, reply_to_id: Optional[int]) -> Message:
    """
    Отправляет пост от лица бота в целевой чат и топик (текст или медиа).

    При наличии фото/видео/документа копирует его с новым описанием.
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
    Проверяет, что команда вызвана в группе или супергруппе, а не в ЛС.

    При вызове в приватном диалоге выводит предупреждение и возвращает False.
    """
    if message.chat.type == "private":
        await message.answer("⚠️ Команда /all предназначена для вызова в топиках группы.")
        return False
    return True


def compose_broadcast_content(
    classmates: List[Dict[str, Any]], message: Message
) -> tuple[str, Optional[int]]:
    """
    Формирует итоговый HTML рассылки и определяет ID реплая.

    Размещает текст автора вверху, а пинги одногруппников — внизу сообщения.
    """
    mentions = build_mentions_block(classmates, message.from_user)
    user_html = extract_broadcast_text(message.html_text or "")
    reply_id = message.reply_to_message.message_id if message.reply_to_message else None
    final_text = build_broadcast_message(user_html, mentions, has_reply=bool(reply_id))
    return final_text, reply_id


async def dispatch_broadcast(message: Message, final_text: str, reply_id: Optional[int]) -> None:
    """
    Выполняет отправку поста и удаление исходной команды с логированием.

    Перехватывает ошибки доставки, информируя инициатора команды при сбое.
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
    Координирует валидацию, компоновку и отправку общего пинга группы.

    Выступает чистым оркестратором без смешения бизнес-логики.
    """
    if not await validate_group_chat(message):
        return
    classmates = await load_classmates_list()
    final_text, reply_id = compose_broadcast_content(classmates, message)
    await dispatch_broadcast(message, final_text, reply_id)
