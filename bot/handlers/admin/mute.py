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


async def resolve_user_id_by_username(bot, chat_id: int, username: str) -> Optional[Tuple[int, str]]:
    """
    Пытается найти ID пользователя по юзернейму в чате.

    :param bot: Экземпляр бота
    :param chat_id: ID чата группы
    :param username: Имя пользователя с @ или без
    :return: Кортеж (user_id, display_name) или None
    """
    clean_username = username.lstrip("@").lower()
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user and admin.user.username and admin.user.username.lower() == clean_username:
                return admin.user.id, f"<b>{admin.user.full_name}</b>"
    except Exception:
        pass
    return None


async def parse_standalone_mute_args(message: Message) -> Tuple[Optional[int], str, str, str]:
    """
    Парсит аргументы при указании ID или @username без реплая.

    :param message: Входящее сообщение
    :return: Кортеж (target_id, target_name, time_raw, reason)
    """
    text = message.text or ""
    parts = text.strip().split(maxsplit=3)
    if len(parts) < 2:
        return None, "", "10м", "без указания причины"

    target_raw = parts[1]
    time_raw = parts[2] if len(parts) > 2 else "10м"
    reason = parts[3] if len(parts) > 3 else "без указания причины"

    target_id: Optional[int] = None
    target_name = f"<b>{target_raw}</b>"

    if target_raw.isdigit():
        target_id = int(target_raw)
    elif message.entities:
        for entity in message.entities:
            if entity.type == "text_mention" and entity.user:
                target_id = entity.user.id
                target_name = f"<b>{entity.user.full_name}</b>"
                break

    if not target_id and target_raw.startswith("@"):
        chat_id = message.chat.id if message.chat.type != "private" else TOPIC_CHAT_ID
        found = await resolve_user_id_by_username(message.bot, chat_id, target_raw)
        if found:
            target_id, target_name = found

    return target_id, target_name, time_raw, reason


def parse_reply_mute_args(text: str) -> Tuple[str, str]:
    """
    Парсит время и причину при ответе на сообщение (реплай).

    :param text: Текст сообщения
    :return: Кортеж (time_raw, reason)
    """
    parts = text.strip().split(maxsplit=2)
    time_raw = parts[1] if len(parts) > 1 else "10м"
    reason = parts[2] if len(parts) > 2 else "без указания причины"
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


async def send_mute_notification(message: Message, res_text: str) -> None:
    """
    Отправляет результаты выдачи мута в ЛС админу и в основной топик группы.

    :param message: Входящее сообщение
    :param res_text: Сформированный текст отчета
    """
    if message.chat.type == "private":
        await message.bot.send_message(chat_id=TOPIC_CHAT_ID, message_thread_id=TOPIC_THREAD_ID, text=res_text)
        await message.answer(f"✅ <b>Успешно замучен в чате группы:</b>\n\n{res_text}")
    else:
        await message.answer(res_text)


@router.message(F.text & F.text.func(lambda t: t.lower().strip().startswith(".закрыть рот")))
async def cmd_mute_user(message: Message) -> None:
    """
    Ограничивает отправку сообщений пользователем в основном чате группы.

    :param message: Message
    """
    if not message.from_user or message.from_user.id != ALLOWED_USER_ID:
        return

    target_id, target_name, time_raw, reason = await extract_target_id_and_args(message)
    duration_sec = parse_duration_to_seconds(time_raw) or 600


    if not target_id:
        msg = "⚠️ <b>Пользователь не найден!</b>\nУкажите ID (например, <code>.закрыть рот 12345678 10м</code>) или ответьте на его сообщение."
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
    except Exception as e:
        await message.answer(f"❌ <b>Не удалось наложить мут:</b> {e}")



