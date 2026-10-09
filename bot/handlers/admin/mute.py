"""
Хэндлеры команд модерации и ограничения отправки сообщений (Мут в топиках).
"""

import html
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatPermissions, Message

from config import ALLOWED_USER_ID, FLOOD_TOPIC_THREAD_ID, TIMEZONE, TOPIC_CHAT_ID
from core.logger import get_logger
from services.user_cache import add_user_to_cache, get_cached_user_id
from utils.mute_parser import parse_duration_to_seconds

log = get_logger("admin_mute")
router = Router()


def cache_user_from_message(message: Message) -> None:
    """Сохраняет username и user_id участников в постоянный кэш."""
    if message.from_user and message.from_user.username:
        add_user_to_cache(message.from_user.username, message.from_user.id)
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        if u.username:
            add_user_to_cache(u.username, u.id)
    if message.entities:
        for e in message.entities:
            if e.type == "text_mention" and e.user and e.user.username:
                add_user_to_cache(e.user.username, e.user.id)


async def _find_in_admins(bot, chat_id: int, clean: str) -> tuple[int, str] | None:
    """Ищет пользователя среди администраторов чата."""
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for a in admins:
            if a.user and a.user.username and a.user.username.lower() == clean:
                add_user_to_cache(clean, a.user.id)
                return a.user.id, f"<b>{html.escape(a.user.full_name)}</b>"
    except TelegramBadRequest as e:
        log.debug(f"Не удалось получить администраторов чата {chat_id}: {e}")
    except Exception as e:
        log.debug(f"Ошибка проверки администраторов чата: {e}")
    return None


def _find_in_registry(clean: str) -> tuple[int, str] | None:
    """Ищет пользователя в реестре студентов по username."""
    from services.classmates_auth import load_classmates_registry
    registry = load_classmates_registry()
    for student in registry:
        uname = student.get("username")
        if uname and uname.lower() == clean and student.get("tg_id"):
            tg_id = student["tg_id"]
            add_user_to_cache(clean, tg_id)
            return tg_id, f"<b>{html.escape(student.get('full_name', f'@{clean}'))}</b>"
    return None


async def resolve_user_id_by_username(bot, chat_id: int, username: str) -> tuple[int, str] | None:
    """Находит ID пользователя по юзернейму через кэш, реестр или админов."""
    clean = username.lstrip("@").lower()
    cached_id = get_cached_user_id(clean)
    if cached_id:
        return cached_id, f"<b>@{clean}</b>"
    reg_match = _find_in_registry(clean)
    if reg_match:
        return reg_match
    return await _find_in_admins(bot, chat_id, clean)



def _resolve_from_entities(message: Message) -> tuple[int, str] | None:
    """Извлекает ID пользователя из сущностей упоминания (text_mention)."""
    if not message.entities:
        return None
    for e in message.entities:
        if e.type == "text_mention" and e.user:
            return e.user.id, f"<b>{html.escape(e.user.full_name)}</b>"
    return None


async def resolve_target_identity(message: Message, target_raw: str) -> tuple[int | None, str]:
    """Определяет ID и отображаемое имя из аргументов или сущностей сообщения."""
    if target_raw.isdigit():
        return int(target_raw), f"<b>ID: {target_raw}</b>"
    from_ent = _resolve_from_entities(message)
    if from_ent:
        return from_ent
    if target_raw.startswith("@"):
        cid = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID
        found = await resolve_user_id_by_username(message.bot, cid, target_raw)
        if found:
            return found
    return None, f"<b>{html.escape(target_raw)}</b>"


def _strip_mute_prefix(text: str) -> str:
    """Удаляет префикс команды мута из текста."""
    clean_text = text.strip()
    for prefix in [".закрыть рот", ".закрой рот"]:
        if clean_text.lower().startswith(prefix):
            return clean_text[len(prefix):].strip()
    return clean_text


def parse_reply_mute_args(text: str) -> tuple[str, str]:
    """Парсит длительность и причину при реплае."""
    parts = _strip_mute_prefix(text).split(maxsplit=1)
    if not parts or not parts[0]:
        return "10м", "без указания причины"
    first, rest = parts[0], parts[1] if len(parts) > 1 else ""
    if parse_duration_to_seconds(first) is not None:
        return first, rest if rest else "без указания причины"
    reason = f"{first} {rest}".strip() if rest else first
    return "10м", reason


async def parse_standalone_mute_args(message: Message) -> tuple[int | None, str, str, str]:
    """Парсит аргументы при прямом указании ID/@username без реплая."""
    parts = (message.text or "").strip().split(maxsplit=3)
    if len(parts) < 2:
        return None, "", "10м", "без указания причины"
    target_raw = parts[1]
    second = parts[2] if len(parts) > 2 else "10м"
    third = parts[3] if len(parts) > 3 else "без указания причины"
    if parse_duration_to_seconds(second) is not None:
        time_raw, reason = second, third
    else:
        time_raw = "10м"
        reason = f"{second} {third}".strip() if len(parts) > 2 else "без указания причины"
    target_id, target_name = await resolve_target_identity(message, target_raw)
    return target_id, target_name, time_raw, reason


async def extract_target_id_and_args(message: Message) -> tuple[int | None, str, str, str]:
    """Извлекает target_id, имя, время и причину из реплая или текста."""
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        time_raw, reason = parse_reply_mute_args(message.text or "")
        return u.id, f"<b>{html.escape(u.full_name)}</b>", time_raw, reason
    return await parse_standalone_mute_args(message)


async def apply_user_restriction(bot, chat_id: int, user_id: int, duration_sec: int) -> None:
    """Применяет ограничение отправки сообщений для пользователя."""
    until_dt = datetime.now(TIMEZONE) + timedelta(seconds=duration_sec)
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_dt
    )


async def _apply_unmute_permissions(bot, chat_id: int, user_id: int) -> None:
    """Снимает ограничения на отправку всех типов сообщений."""
    full_perms = ChatPermissions(
        can_send_messages=True, can_send_audios=True, can_send_documents=True,
        can_send_photos=True, can_send_videos=True, can_send_other_messages=True,
        can_add_web_page_previews=True
    )
    await bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=full_perms)


async def send_mute_notification(message: Message, res_text: str) -> None:
    """Отправляет отчет о муте/размуте в чат или топик."""
    if message.chat.type == "private":
        await message.bot.send_message(chat_id=TOPIC_CHAT_ID, message_thread_id=FLOOD_TOPIC_THREAD_ID, text=res_text)
        await message.answer(f"✅ <b>Успешно:</b>\n\n{res_text}")
    else:
        await message.answer(res_text)


async def _safe_delete_message(message: Message) -> None:
    """Удаляет сервисную команду в публичном чате без выброса исключений."""
    if message.chat.type != "private":
        try:
            await message.delete()
        except TelegramBadRequest as e:
            if "not found" in str(e).lower():
                log.debug(f"Сервисная команда {message.message_id} уже была удалена")
            else:
                log.warning(f"Не удалось удалить сервисную команду {message.message_id}: {e}")
        except Exception as e:
            log.warning(f"Не удалось удалить сервисную команду {message.message_id}: {e}")


def _build_mute_report(target_name: str, time_raw: str, reason: str) -> str:
    """Формирует HTML-текст отчета о наложении мута."""
    return (
        f"🔇 {target_name} <b>закрыли рот во всех топиках!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏳ <b>Длительность:</b> {time_raw}\n"
        f"📝 <b>Причина:</b> {html.escape(reason)}"
    )


def is_mute_command(text: str | None) -> bool:
    """Проверяет команду наложения мута."""
    if not text:
        return False
    t = text.lower().strip()
    return t.startswith((".закрыть рот", ".закрой рот"))


def is_unmute_command(text: str | None) -> bool:
    """Проверяет команду снятия мута."""
    if not text:
        return False
    t = text.lower().strip()
    return t.startswith((".открыть рот", ".открой рот"))


@router.message(F.text & F.text.func(is_mute_command))
async def cmd_mute_user(message: Message) -> None:
    """Ограничивает отправку сообщений пользователем в основном чате группы."""
    cache_user_from_message(message)
    if not message.from_user or message.from_user.id != ALLOWED_USER_ID:
        return
    target_id, target_name, time_raw, reason = await extract_target_id_and_args(message)
    if not target_id:
        await message.answer("⚠️ <b>Пользователь не найден!</b> Укажите ID или ответьте на его сообщение.")
        return
    duration_sec = parse_duration_to_seconds(time_raw) or 600
    target_chat_id = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID
    try:
        await apply_user_restriction(message.bot, target_chat_id, target_id, duration_sec)
        await send_mute_notification(message, _build_mute_report(target_name, time_raw, reason))
        await _safe_delete_message(message)
    except Exception as e:
        log.error(f"Ошибка мута target_id={target_id}: {e}")
        await message.answer(f"❌ <b>Не удалось наложить мут:</b> {html.escape(str(e))}")


@router.message(F.text & F.text.func(is_unmute_command))
async def cmd_unmute_user(message: Message) -> None:
    """Снимает ограничение отправки сообщений с пользователя."""
    if not message.from_user or message.from_user.id != ALLOWED_USER_ID:
        return
    target_id, target_name, _, _ = await extract_target_id_and_args(message)
    if not target_id:
        await message.answer("⚠️ <b>Пользователь не найден!</b> Укажите ID или ответьте на его сообщение.")
        return
    target_chat_id = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID
    try:
        await _apply_unmute_permissions(message.bot, target_chat_id, target_id)
        res_text = f"🔊 {target_name} <b>снова может говорить во всех топиках!</b>"
        await send_mute_notification(message, res_text)
        await _safe_delete_message(message)
    except Exception as e:
        log.error(f"Ошибка размута target_id={target_id}: {e}")
        await message.answer(f"❌ <b>Не удалось размутить:</b> {html.escape(str(e))}")
