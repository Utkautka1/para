"""
Хэндлер автоматической расшифровки голосовых и видеосообщений в топиках чата.

Перехватывает голосовые (voice) и видео-кружочки (video_note) в целевом
форум-чате и личных сообщениях, сохраняя привязку к исходному топику
через message_thread_id.
"""

import asyncio
import html
import os
import time
import uuid
from typing import NamedTuple, Optional

from aiogram import F, Router
from aiogram.types import Message

from bot.templates.user.voice import (
    format_rate_limit_error,
    format_too_big_error,
    format_too_long_error,
    format_transcription_empty,
    format_transcription_error,
    format_transcription_result,
    format_transcription_status,
)
from config import (
    TOPIC_CHAT_ID,
    MAX_AUDIO_DURATION,
    MAX_AUDIO_SIZE,
    MAX_CONCURRENT_PER_USER,
    DOWNLOAD_TIMEOUT,
    TRANSCRIBE_TIMEOUT,
    _USER_IN_FLIGHT,
)

from core.bot import bot
from core.logger import get_logger
from services.transcriber import split_text_to_chunks, transcriber_service

log = get_logger("bot_voice")
router = Router(name="voice_transcribe")




class AudioMeta:
    """Метаданные входящего аудиосообщения с поддержкой распаковки 3 элементов."""

    def __init__(
        self,
        file_id: str,
        duration: int,
        sender: str,
        file_size: int = 0,
        user_id: int = 0,
        username: str = "",
        chat_id: int = 0,
        thread_id: Optional[int] = None,
        media_type: str = "voice",
    ):
        self.file_id = file_id
        self.duration = duration
        self.sender = sender
        self.file_size = file_size
        self.user_id = user_id
        self.username = username
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.media_type = media_type

    def __iter__(self):
        """Обеспечивает обратную совместимость с распаковкой: file_id, dur, sender."""
        return iter((self.file_id, self.duration, self.sender))


def is_allowed_chat(chat_id: int, chat_type: str) -> bool:
    """Проверяет принадлежность чата к целевой группе или ЛС."""
    return chat_id == TOPIC_CHAT_ID or chat_type == "private"


def extract_audio_meta(message: Message) -> AudioMeta:
    """Извлекает подробные метаданные аудиосообщения для обработки."""
    user = message.from_user
    sender = user.full_name if user else "Собеседник"
    uid = user.id if user else 0
    uname = user.username or "" if user else ""
    chat = getattr(message, "chat", None)
    cid = chat.id if chat else 0
    thid = getattr(message, "message_thread_id", None)
    if message.voice:
        v = message.voice
        return AudioMeta(v.file_id, v.duration, sender, v.file_size or 0, uid, uname, cid, thid, "voice")
    if message.video_note:
        vn = message.video_note
        return AudioMeta(vn.file_id, vn.duration, sender, vn.file_size or 0, uid, uname, cid, thid, "video_note")
    return AudioMeta("", 0, sender, 0, uid, uname, cid, thid, "unknown")


def acquire_user_slot(user_id: int) -> bool:
    """Проверяет и резервирует слот одновременных задач для пользователя."""
    if user_id <= 0:
        return True
    current = _USER_IN_FLIGHT.get(user_id, 0)
    if current >= MAX_CONCURRENT_PER_USER:
        return False
    _USER_IN_FLIGHT[user_id] = current + 1
    return True


def release_user_slot(user_id: int) -> None:
    """Освобождает занятый слот пользователя после завершения транскрибации."""
    if user_id in _USER_IN_FLIGHT:
        _USER_IN_FLIGHT[user_id] -= 1
        if _USER_IN_FLIGHT[user_id] <= 0:
            _USER_IN_FLIGHT.pop(user_id, None)


def validate_audio_limits(duration: int, file_size: int, sender: str) -> Optional[str]:
    """Проверяет ограничения по длительности и размеру аудиофайла."""
    if duration > MAX_AUDIO_DURATION:
        log.warning(f"⚠️ Аудио от {sender} отклонено: длительность {duration}с > {MAX_AUDIO_DURATION}с")
        return format_too_long_error(MAX_AUDIO_DURATION)
    if file_size > MAX_AUDIO_SIZE:
        max_mb = MAX_AUDIO_SIZE // (1024 * 1024)
        log.warning(f"⚠️ Аудио от {sender} отклонено: размер {file_size} > {MAX_AUDIO_SIZE}")
        return format_too_big_error(max_mb)
    return None


def log_voice_request(meta: AudioMeta) -> None:
    """Логирует структурированную информацию о входящем аудиосообщении."""
    log.info("=" * 55)
    log.info(f"--- 🎙 Получено аудиосообщение ({meta.media_type}) ---")
    log.info(f"  Пользователь: {meta.user_id} (@{meta.username}) | {meta.sender}")
    log.info(f"  Чат / Топик:  chat={meta.chat_id} | thread={meta.thread_id}")
    log.info(f"  Параметры:    длительность={meta.duration}с | размер={meta.file_size} байт")
    log.info("=" * 55)


async def download_temp_audio(file_id: str) -> str:
    """Скачивает аудиофайл Telegram в RAM-диск (/dev/shm) с таймаутом."""
    base_dir = "/dev/shm/para_audio" if os.path.exists("/dev/shm") else "data/temp_audio"
    os.makedirs(base_dir, exist_ok=True)
    temp_path = f"{base_dir}/{uuid.uuid4().hex}.ogg"
    dl_start = time.monotonic()
    log.debug(f"Старт загрузки файла {file_id[:12]}... в {temp_path}")
    tg_file = await asyncio.wait_for(bot.get_file(file_id), timeout=DOWNLOAD_TIMEOUT)
    await asyncio.wait_for(
        bot.download_file(tg_file.file_path, destination=temp_path),
        timeout=DOWNLOAD_TIMEOUT,
    )
    dl_time = time.monotonic() - dl_start
    log.debug(f"Файл {os.path.basename(temp_path)} скачан за {dl_time:.2f}с")
    return temp_path


def cleanup_temp_file(path: str) -> None:
    """Удаляет временный аудиофайл с подавлением ошибок."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError as e:
        log.warning(f"⚠️ Не удалось удалить временный файл {path}: {e}")


async def send_overflow_chunks(message: Message, chunks: list[str]) -> None:
    """Отправляет последующие части длинного сообщения с экранированием HTML."""
    for extra_chunk in chunks:
        safe_chunk = html.escape(extra_chunk.strip())
        await message.reply(f"«{safe_chunk}»")


async def deliver_transcription(
    message: Message,
    status_msg: Message,
    sender_name: str,
    duration: int,
    text: str,
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


async def _download_and_transcribe(file_id: str) -> str:
    """Скачивает аудио и транскрибирует речь с таймаутом и очисткой диска."""
    temp_path = ""
    try:
        temp_path = await download_temp_audio(file_id)
        return await asyncio.wait_for(
            transcriber_service.transcribe_file(temp_path),
            timeout=TRANSCRIBE_TIMEOUT,
        )
    finally:
        cleanup_temp_file(temp_path)


async def process_audio_pipeline(
    file_id: str,
    sender: str,
    duration: int,
    message: Message,
    status_msg: Message,
    user_id: int = 0,
) -> None:
    """Выполняет защищенную обработку аудио, отправку текста и очистку слота."""
    start_time = time.monotonic()
    try:
        text = await _download_and_transcribe(file_id)
        await deliver_transcription(message, status_msg, sender, duration, text)
        elapsed = time.monotonic() - start_time
        log.info(f"✅ Аудио от {sender} (id={user_id}) обработано за {elapsed:.2f}с ({len(text)} симв.)")
    except Exception as e:
        log.error(f"❌ Ошибка расшифровки аудио ({file_id}) от {sender}: {e}")
        await status_msg.edit_text(format_transcription_error())
    finally:
        release_user_slot(user_id)


@router.message(F.voice | F.video_note)
async def handle_voice_or_video_note(message: Message) -> None:
    """Основной хэндлер голосовых заметок и видео-кружочков во всех топиках."""
    if not is_allowed_chat(message.chat.id, message.chat.type):
        return
    meta = extract_audio_meta(message)
    if not meta.file_id:
        return
    log_voice_request(meta)
    limit_err = validate_audio_limits(meta.duration, meta.file_size, meta.sender)
    if limit_err:
        await message.reply(limit_err)
        return
    if not acquire_user_slot(meta.user_id):
        log.warning(f"⚠️ Троттлинг: пользователь {meta.user_id} превысил лимит")
        await message.reply(format_rate_limit_error())
        return
    status_msg = await message.reply(format_transcription_status())
    await process_audio_pipeline(
        meta.file_id, meta.sender, meta.duration, message, status_msg, meta.user_id
    )

