"""
Хэндлеры команд модерации и ограничения отправки сообщений (Мут в топиках).
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from aiogram import Router, F
from aiogram.types import ChatPermissions, Message
from config import ALLOWED_USER_ID, TIMEZONE, TOPIC_CHAT_ID, TOPIC_THREAD_ID
from bot.filters.auth import AuthFilter
from utils.mute_parser import parse_duration_to_seconds

router = Router()


from services.user_cache import add_user_to_cache, get_cached_user_id


def cache_user_from_message(message: Message) -> None:
    """
    Сохраняет username и user_id из любых сообщений и сущностей Telegram в постоянный файл.

    :param message: Входящее сообщение
    """
    if message.from_user and message.from_user.username:
        add_user_to_cache(message.from_user.username, message.from_user.id)
    if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.username:
        u = message.reply_to_message.from_user
        add_user_to_cache(u.username, u.id)
    if message.entities:
        for e in message.entities:
            if e.type == "text_mention" and e.user and e.user.username:
                add_user_to_cache(e.user.username, e.user.id)


async def resolve_user_id_by_username(bot, chat_id: int, username: str) -> Optional[Tuple[int, str]]:
    """
    Пытается найти ID пользователя по юзернейму через дисковый кэш, список админов и Telegram API.

    :param bot: Экземпляр бота
    :param chat_id: ID чата группы
    :param username: Имя пользователя с @ или без
    :return: Кортеж (user_id, display_name) или None
    """
    clean = username.lstrip("@").lower()
    cached_id = get_cached_user_id(clean)
    if cached_id:
        return cached_id, f"<b>@{clean}</b>"

    try:
        admins = await bot.get_chat_administrators(chat_id)
        for a in admins:
            if a.user and a.user.username and a.user.username.lower() == clean:
                add_user_to_cache(clean, a.user.id)
                return a.user.id, f"<b>{a.user.full_name}</b>"
    except Exception:
        pass

    try:
        member = await bot.get_chat_member(chat_id, f"@{clean}")
        if member and member.user:
            add_user_to_cache(clean, member.user.id)
            return member.user.id, f"<b>{member.user.full_name}</b>"
    except Exception:
        pass

    return None






async def parse_standalone_mute_args(message: Message) -> Tuple[Optional[int], str, str, str]:
    """
    Парсит аргументы при указании ID или @username без реплая.

    :param message: Входящее сообщение
    :return: Кортеж (target_id, target_name, time_raw, reason)
    """
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


async def resolve_target_identity(message: Message, target_raw: str) -> Tuple[Optional[int], str]:
    """
    Определяет ID и отображаемое имя из строки аргументов или сущностей Telegram.

    :param message: Message
    :param target_raw: Исходный параметр пользователя
    :return: Кортеж (target_id, target_name)
    """
    target_id: Optional[int] = None
    target_name = f"<b>{target_raw}</b>"

    if target_raw.isdigit():
        return int(target_raw), f"<b>ID: {target_raw}</b>"

    if message.entities:
        for e in message.entities:
            if e.type == "text_mention" and e.user:
                return e.user.id, f"<b>{e.user.full_name}</b>"

    if target_raw.startswith("@"):
        cid = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID
        found = await resolve_user_id_by_username(message.bot, cid, target_raw)
        if found:
            return found

    return None, target_name


def parse_reply_mute_args(text: str) -> Tuple[str, str]:
    """
    Парсит время и причину при ответе на сообщение (реплай).

    :param text: Текст сообщения
    :return: Кортеж (time_raw, reason)
    """
    clean_text = text.strip()
    for prefix in [".закрыть рот", ".закрой рот"]:
        if clean_text.lower().startswith(prefix):
            clean_text = clean_text[len(prefix):].strip()
            break

    parts = clean_text.split(maxsplit=1)
    if not parts or not parts[0]:
        return "10м", "без указания причины"

    first_arg = parts[0]
    rest_arg = parts[1] if len(parts) > 1 else ""

    if parse_duration_to_seconds(first_arg) is not None:
        time_raw = first_arg
        reason = rest_arg if rest_arg else "без указания причины"
    else:
        time_raw = "10м"
        reason = f"{first_arg} {rest_arg}".strip()

    return time_raw, reason




async def extract_target_id_and_args(message: Message) -> Tuple[Optional[int], str, str, str]:
    """
    Извлекает target_id, target_name, time_raw и reason из сообщения или реплая.

    :param message: Входящее сообщение
    :return: Кортеж (target_id, target_name, time_raw, reason)
    """
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        time_raw, reason = parse_reply_mute_args(message.text or "")
        return u.id, f"<b>{u.full_name}</b>", time_raw, reason

    return await parse_standalone_mute_args(message)


async def apply_user_restriction(bot, chat_id: int, user_id: int, duration_sec: int) -> None:
    """
    Применяет ограничение отправки сообщений для пользователя.

    :param bot: Экземпляр Bot
    :param chat_id: ID чата
    :param user_id: ID целевого пользователя
    :param duration_sec: Длительность в секундах
    """
    until_dt = datetime.now(TIMEZONE) + timedelta(seconds=duration_sec)
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=until_dt
    )


from config import ALLOWED_USER_ID, FLOOD_TOPIC_THREAD_ID, TIMEZONE, TOPIC_CHAT_ID, TOPIC_THREAD_ID


async def send_mute_notification(message: Message, res_text: str) -> None:
    """
    Отправляет результаты выдачи мута в ЛС админу и в топик Флудилка (thread_id 4).

    :param message: Входящее сообщение
    :param res_text: Сформированный текст отчета
    """
    if message.chat.type == "private":
        await message.bot.send_message(chat_id=TOPIC_CHAT_ID, message_thread_id=FLOOD_TOPIC_THREAD_ID, text=res_text)
        await message.answer(f"✅ <b>Успешно замучен в чате группы:</b>\n\n{res_text}")
    else:
        await message.answer(res_text)



def is_mute_command(text: Optional[str]) -> bool:
    """
    Проверяет, является ли сообщение командой наложения мута.

    :param text: Текст сообщения
    :return: True, если команда мута
    """
    if not text:
        return False
    t = text.lower().strip()
    return t.startswith(".закрыть рот") or t.startswith(".закрой рот")



@router.message(F.text & F.text.func(is_mute_command))
async def cmd_mute_user(message: Message) -> None:
    """
    Ограничивает отправку сообщений пользователем в основном чате группы.

    :param message: Message
    """
    cache_user_from_message(message)
    if not message.from_user or message.from_user.id != ALLOWED_USER_ID:
        return


    target_id, target_name, time_raw, reason = await extract_target_id_and_args(message)
    duration_sec = parse_duration_to_seconds(time_raw) or 600

    if not target_id:
        msg = "⚠️ <b>Пользователь не найден!</b>\nУкажите ID (например, <code>.закрой рот 12345678 10м</code>) или ответьте на его сообщение."
        await message.answer(msg)
        return

    target_chat_id = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID

    try:
        await apply_user_restriction(message.bot, target_chat_id, target_id, duration_sec)
        res_text = (
            f"🔇 {target_name} <b>закрыли рот во всех топиках!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ <b>Длительность:</b> {time_raw}\n"
            f"📝 <b>Причина:</b> {reason}"
        )
        await send_mute_notification(message, res_text)
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
    except Exception as e:
        await message.answer(f"❌ <b>Не удалось наложить мут:</b> {e}")


def is_unmute_command(text: Optional[str]) -> bool:
    """
    Проверяет, является ли сообщение командой снятия мута.

    :param text: Текст сообщения
    :return: True, если команда снятия мута
    """
    if not text:
        return False
    t = text.lower().strip()
    return t.startswith(".открыть рот") or t.startswith(".открой рот")



@router.message(F.text & F.text.func(is_unmute_command))
async def cmd_unmute_user(message: Message) -> None:
    """
    Снимает ограничение отправки сообщений с пользователя.

    :param message: Message
    """
    if not message.from_user or message.from_user.id != ALLOWED_USER_ID:
        return

    target_id, target_name, _, _ = await extract_target_id_and_args(message)
    if not target_id:
        await message.answer("⚠️ <b>Пользователь не найден!</b> Укажите ID или ответьте на его сообщение.")
        return

    target_chat_id = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID
    try:
        await message.bot.restrict_chat_member(
            chat_id=target_chat_id,
            user_id=target_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        res_text = f"🔊 {target_name} <b>снова может говорить во всех топиках!</b>"
        await send_mute_notification(message, res_text)
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
    except Exception as e:
        await message.answer(f"❌ <b>Не удалось размутить:</b> {e}")





