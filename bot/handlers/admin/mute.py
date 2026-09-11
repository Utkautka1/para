"""
Хэндлеры команд модерации и ограничения отправки сообщений (Мут в топиках).
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from aiogram import Router, F
from aiogram.types import ChatPermissions, Message
from config import TIMEZONE
from bot.filters.auth import AuthFilter
from utils.mute_parser import parse_duration_to_seconds

router = Router()
router.message.filter(AuthFilter())


def extract_target_user_info(message: Message) -> Tuple[Optional[int], str]:
    """
    Извлекает ID и отображаемое имя нарушителя из реплая или упоминания.

    :param message: Объект входящего сообщения
    :return: Кортеж (user_id, name)
    """
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        return u.id, f"<b>{u.full_name}</b>"
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention" and entity.user:
                return entity.user.id, f"<b>{entity.user.full_name}</b>"
    return None, ""


def parse_mute_args(text: str) -> Tuple[str, str]:
    """
    Извлекает параметры времени и причины из команды .закрыть рот.

    :param text: Текст сообщения
    :return: Кортеж (time_raw, reason)
    """
    parts = text.strip().split(maxsplit=3)
    if len(parts) >= 4 and (parts[2].startswith("@") or parts[2].isdigit()):
        return parts[3], parts[4] if len(parts) > 4 else "без указания причины"
    elif len(parts) >= 3 and not (parts[2].startswith("@") or parts[2].isdigit()):
        reason = " ".join(parts[3:]) if len(parts) > 3 else "без указания причины"
        return parts[2], reason
    return "10м", "без указания причины"


@router.message(F.text.startswith(".закрыть рот"))
async def cmd_mute_user(message: Message) -> None:
    """
    Ограничивает отправку сообщений пользователем во всех топиках чата.

    :param message: Message
    """
    target_id, target_name = extract_target_user_info(message)
    time_raw, reason = parse_mute_args(message.text or "")
    duration_sec = parse_duration_to_seconds(time_raw) or 600

    if not target_id:
        await message.answer("⚠️ <b>Пользователь не найден!</b> Ответьте на его сообщение или упомяните <code>@username</code>.")
        return

    until_dt = datetime.now(TIMEZONE) + timedelta(seconds=duration_sec)
    try:
        await message.bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_dt
        )
        res_text = (
            f"🔇 {target_name} <b>закрыли рот во всех топиках!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ <b>Длительность:</b> {time_raw}\n"
            f"📝 <b>Причина:</b> {reason}"
        )
        await message.answer(res_text)
    except Exception as e:
        await message.answer(f"❌ <b>Не удалось наложить мут:</b> {e}")
