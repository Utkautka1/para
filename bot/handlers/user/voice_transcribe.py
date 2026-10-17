"""
Хэндлер автоматической расшифровки голосовых и видеосообщений в топиках чата.

Перехватывает голосовые (voice) и видео-кружочки (video_note) в целевом
форум-чате и личных сообщениях, сохраняя привязку к исходному топику
через message_thread_id.
"""

import os
import uuid
from aiogram import F, Router
from aiogram.types import Message

from config import TOPIC_CHAT_ID
from core.bot import bot
from core.logger import get_logger
from bot.templates.user.voice import (
    format_transcription_empty,
    format_transcription_error,
    format_transcription_result,
    format_transcription_status,
)
from services.transcriber import split_text_to_chunks, transcriber_service

log = get_logger("bot_voice")
router = Router(name="voice_transcribe")


def is_allowed_chat(chat_id: int, chat_type: str) -> bool:
    """Проверяет принадлежность чата к целевой группе или ЛС."""
    return chat_id == TOPIC_CHAT_ID or chat_type == "private"


def extract_audio_meta(message: Message) -> tuple[str, int, str]:
    """Извлекает file_id, длительность и имя отправителя сообщения."""
    sender_name = message.from_user.full_name if message.from_user else "Собеседник"
    if message.voice:
        return message.voice.file_id, message.voice.duration, sender_name
    if message.video_note:
        return message.video_note.file_id, message.video_note.duration, sender_name
    return "", 0, sender_name


async def download_temp_audio(file_id: str) -> str:
    """Скачивает аудиофайл Telegram в RAM-диск (/dev/shm) или временную директорию."""
    base_dir = "/dev/shm/para_audio" if os.path.exists("/dev/shm") else "data/temp_audio"
    os.makedirs(base_dir, exist_ok=True)
    temp_path = f"{base_dir}/{uuid.uuid4().hex}_{file_id[:10]}.ogg"
    telegram_file = await bot.get_file(file_id)
    await bot.download_file(telegram_file.file_path, destination=temp_path)
    return temp_path


def cleanup_temp_file(path: str) -> None:
    """Удаляет временный аудиофайл с подавлением ошибок."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError as e:
        log.warning(f"⚠️ Не удалось удалить временный файл {path}: {e}")


async def send_overflow_chunks(message: Message, chunks: list[str]) -> None:
    """Отправляет последующие части длинного сообщения в исходный топик."""
    for extra_chunk in chunks:
        await message.reply(f"«{extra_chunk}»")


async def deliver_transcription(
    message: Message,
    status_msg: Message,
    sender_name: str,
    duration: int,
    text: str
) -> None:
    """Доставляет результат расшифровки с разбивкой на части при необходимости."""
    if not text.strip():
        await status_msg.edit_text(format_transcription_empty(sender_name, duration))
        return
    chunks = split_text_to_chunks(text)
    first_text = format_transcription_result(sender_name, duration, chunks[0])
    await status_msg.edit_text(first_text)
    if len(chunks) > 1:
        await send_overflow_chunks(message, chunks[1:])


async def process_audio_pipeline(
    file_id: str,
    sender: str,
    duration: int,
    message: Message,
    status_msg: Message
) -> None:
    """Выполняет скачивание, распознавание и доставку текста аудио."""
    temp_path = ""
    try:
        temp_path = await download_temp_audio(file_id)
        recognized_text = await transcriber_service.transcribe_file(temp_path)
        await deliver_transcription(message, status_msg, sender, duration, recognized_text)
    except Exception as e:
        log.error(f"❌ Ошибка расшифровки аудио ({file_id}): {e}")
        await status_msg.edit_text(format_transcription_error())
    finally:
        cleanup_temp_file(temp_path)


@router.message(F.voice | F.video_note)
async def handle_voice_or_video_note(message: Message) -> None:
    """Основной хэндлер голосовых заметок и видео-кружочков во всех топиках."""
    if not is_allowed_chat(message.chat.id, message.chat.type):
        return
    file_id, duration, sender = extract_audio_meta(message)
    if not file_id:
        return
    status_msg = await message.reply(format_transcription_status())
    await process_audio_pipeline(file_id, sender, duration, message, status_msg)

