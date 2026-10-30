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
    _USER_IN_FLIGHT,
    DOWNLOAD_TIMEOUT,
    MAX_AUDIO_DURATION,
    MAX_AUDIO_SIZE,
    MAX_CONCURRENT_PER_USER,
    TOPIC_CHAT_ID,
)
from core.bot import bot
from core.logger import get_logger
from services.stt_queue import resolve_audio_dir, transcribe_via_stt
from services.transcriber import split_text_to_chunks

log = get_logger("bot_voice")
router = Router(name="voice_transcribe")


class AudioMeta:
    """Контейнер нормализованных метаданных аудиосообщения Telegram."""

    def __init__(
        self,
        file_id: str,
        duration: int,
        sender: str,
        file_size: int = 0,
        user_id: int = 0,
        username: str = "",
        chat_id: int = 0,
        thread_id: int | None = None,
        media_type: str = "voice",
    ):
        """
        Инициализирует контейнер метаданных входящего голосового или видеосообщения.

        Сохраняет параметры файла, пользователя и треда для логирования и обработки.
        Поддерживает значения по умолчанию для опциональных параметров.
        """

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
        """
        Обеспечивает распаковку основных полей: file_id, duration, sender.

        Сохраняет обратную совместимость с позиционной деструктуризацией кортежа.
        Позволяет использовать объект как кортеж из трех элементов.

        Возвращает итератор по (file_id, duration, sender).
        """

        return iter((self.file_id, self.duration, self.sender))


def is_allowed_chat(chat_id: int, chat_type: str) -> bool:
    """
    Проверяет, разрешена ли обработка голосовых сообщений в данном чате.

    Ограничивает транскрибацию целевым форум-чатом группы или личными сообщениями бота.
    Предотвращает обработку случайных сообщений в сторонних группах.

    Возвращает True, если чат разрешен, иначе False.
    """

    return chat_id == TOPIC_CHAT_ID or chat_type == "private"


def extract_audio_meta(message: Message) -> AudioMeta:
    """
    Извлекает нормализованные метаданные аудио- или видеосообщения Telegram.

    Унифицирует различия между voice (OGG/Opus) и video_note (кружочки MP4).
    Извлекает параметры отправителя, идентификаторы чата и темы форума.

    Возвращает экземпляр AudioMeta с атрибутами медиасообщения.
    """

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
    """
    Атомарно проверяет и резервирует слот параллельной обработки для пользователя.

    Защищает от исчерпания VRAM и CPU при спаме несколькими длинными аудиосообщениями.
    Разрешает максимум MAX_CONCURRENT_PER_USER одновременных задач.

    Возвращает True, если слот успешно выделен, иначе False (троттлинг).
    """

    if user_id <= 0:
        return True

    current = _USER_IN_FLIGHT.get(user_id, 0)
    if current >= MAX_CONCURRENT_PER_USER:
        return False

    _USER_IN_FLIGHT[user_id] = current + 1

    return True


def release_user_slot(user_id: int) -> None:
    """
    Освобождает занятый слот пользователя после завершения транскрибации.

    Уменьшает счетчик активных задач в памяти процесса бота.
    Удаляет ключ из словаря при обнулении счетчика для экономии RAM.

    Ничего не возвращает.
    """

    if user_id in _USER_IN_FLIGHT:
        _USER_IN_FLIGHT[user_id] -= 1
        if _USER_IN_FLIGHT[user_id] <= 0:
            _USER_IN_FLIGHT.pop(user_id, None)


def validate_audio_limits(duration: int, file_size: int, sender: str) -> str | None:
    """
    Проверяет длительность и размер файла на соответствие лимитам Telegram и модели.

    Предотвращает зависания пайплайна и отказ в обслуживании (DoS).
    Логирует факт превышения установленных пороговых значений.

    Возвращает текст ошибки для пользователя или None, если файл валиден.
    """

    if duration > MAX_AUDIO_DURATION:
        log.warning("⚠️ Аудио от %s отклонено: длительность %sс > %sс", sender, duration, MAX_AUDIO_DURATION)
        return format_too_long_error(MAX_AUDIO_DURATION)

    if file_size > MAX_AUDIO_SIZE:
        max_mb = MAX_AUDIO_SIZE // (1024 * 1024)
        log.warning("⚠️ Аудио от %s отклонено: размер %s > %s", sender, file_size, MAX_AUDIO_SIZE)
        return format_too_big_error(max_mb)

    return None


def log_voice_request(meta: AudioMeta) -> None:
    """
    Логирует структурированную информацию о входящем аудиосообщении.

    Фиксирует тип медиа (voice/video_note), отправителя, чат, тред и хронометраж.
    Помогает при отладке и аудите нагрузки на графический процессор.

    Ничего не возвращает.
    """

    log.info("=" * 55)
    log.info("--- 🎙 Получено аудиосообщение (%s) ---", meta.media_type)
    log.info("  Пользователь: %s (@%s) | %s", meta.user_id, meta.username, meta.sender)
    log.info("  Чат / Топик:  chat=%s | thread=%s", meta.chat_id, meta.thread_id)
    log.info("  Параметры:    длительность=%sс | размер=%s байт", meta.duration, meta.file_size)
    log.info("=" * 55)


def _determine_audio_extension(file_path: str | None) -> str:
    """
    Извлекает расширение исходного медиафайла Telegram из его пути.

    Для кружочков (video_note) возвращает mp4, для voice — ogg/oga.
    Ограничивает расширения белым списком поддерживаемых аудио-форматов.

    Возвращает строку расширения без точки (по умолчанию 'ogg').
    """

    raw_ext = os.path.splitext(file_path or "")[1].lstrip(".")
    valid_extensions = ("mp4", "ogg", "oga", "wav", "mp3")

    return raw_ext if raw_ext in valid_extensions else "ogg"


async def download_temp_audio(file_id: str) -> str:
    """
    Скачивает медиафайл из Telegram в общий с сервисом stt tmpfs-том.

    Загружает файл через Bot API с контролем таймаута (DOWNLOAD_TIMEOUT).
    Формирует уникальное имя файла на основе UUID для избежания коллизий.

    Возвращает абсолютный путь к скачанному временному файлу.
    """

    # Каталог общий с сервисом stt (tmpfs-том): stt читает файл по этому же пути
    base_dir = resolve_audio_dir()
    dl_start = time.monotonic()
    tg_file = await asyncio.wait_for(bot.get_file(file_id), timeout=DOWNLOAD_TIMEOUT)
    ext = _determine_audio_extension(tg_file.file_path)
    temp_path = f"{base_dir}/{uuid.uuid4().hex}.{ext}"

    log.debug("Старт загрузки файла %s... в %s", file_id[:12], temp_path)
    await asyncio.wait_for(
        bot.download_file(tg_file.file_path, destination=temp_path),
        timeout=DOWNLOAD_TIMEOUT,
    )
    dl_time = time.monotonic() - dl_start
    log.debug("Файл %s скачан за %.2fс", os.path.basename(temp_path), dl_time)

    return temp_path


def cleanup_temp_file(path: str) -> None:
    """
    Удаляет временный аудиофайл с диска с безопасным подавлением ошибок.

    Предотвращает утечки памяти общего tmpfs-тома stt_audio.
    Логирует предупреждение при сбоях файловой системы.

    Ничего не возвращает.
    """

    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError as e:
        log.warning("⚠️ Не удалось удалить временный файл %s: %s", path, e)


async def send_overflow_chunks(message: Message, chunks: list[str]) -> None:
    """
    Отправляет последующие части длинного сообщения с экранированием HTML.

    Используется, если результат распознавания превышает 4096 символов Telegram.
    Досылает каждый чанк последовательными ответами на исходное сообщение.

    Ничего не возвращает.
    """

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
    """
    Отправляет результат распознавания текста пользователю или в топик.

    Если текст превышает лимит сообщения, разбивает на чанки и досылает реплаями.
    При тишине или отсутствии распознанной речи выводит соответствующее уведомление.

    Ничего не возвращает.
    """

    if not text.strip():
        await status_msg.edit_text(format_transcription_empty(sender_name, duration))
        return

    chunks = split_text_to_chunks(text)
    await status_msg.edit_text(format_transcription_result(sender_name, duration, chunks[0]))

    if len(chunks) > 1:
        await send_overflow_chunks(message, chunks[1:])


async def _download_and_transcribe(file_id: str) -> str:
    """
    Выполняет полный цикл скачивания и распознавания речи с контролем таймаута.

    Использует блок finally для безусловного удаления временного файла с диска,
    гарантируя отсутствие утечек даже при сбое или таймауте модели.

    Возвращает распознанный текст строки.
    """

    temp_path = ""
    try:
        temp_path = await download_temp_audio(file_id)
        # Таймаут TRANSCRIBE_TIMEOUT соблюдается внутри ожидания ответа от stt
        return await transcribe_via_stt(temp_path)
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
    """
    Координирует сквозной процесс транскрибации от скачивания до отправки.

    Гарантирует освобождение зарезервированного слота пользователя в блоке finally.
    Логирует длительность выполнения и перехватывает исключения инференса.

    Ничего не возвращает.
    """

    start_time = time.monotonic()
    try:
        text = await _download_and_transcribe(file_id)
        await deliver_transcription(message, status_msg, sender, duration, text)
        from services.achievement_service import award_achievement

        asyncio.create_task(award_achievement(user_id, "bot_voice_stt", message.bot, sender))
        if duration >= 60:
            asyncio.create_task(award_achievement(user_id, "bot_podcast", message.bot, sender))
        elapsed = time.monotonic() - start_time
        log.info("✅ Аудио от %s (id=%s) обработано за %.2fс (%s симв.)", sender, user_id, elapsed, len(text))
    except Exception as e:
        log.error("❌ Ошибка расшифровки аудио (%s) от %s: %s", file_id, sender, e)
        await status_msg.edit_text(format_transcription_error())
    finally:
        release_user_slot(user_id)


async def _check_and_acquire_voice(message: Message, meta: AudioMeta) -> bool:
    """
    Проверяет лимиты аудиосообщения и резервирует слот пользователя.

    Отправляет уведомление пользователю при превышении лимитов или троттлинге.
    Логирует запрос перед началом валидации.

    Возвращает True, если обработку можно запускать, иначе False.
    """

    log_voice_request(meta)
    limit_err = validate_audio_limits(meta.duration, meta.file_size, meta.sender)
    if limit_err:
        await message.reply(limit_err)
        return False

    if not acquire_user_slot(meta.user_id):
        log.warning("⚠️ Троттлинг: пользователь %s превысил лимит", meta.user_id)
        await message.reply(format_rate_limit_error())
        return False

    return True


@router.message(F.voice | F.video_note)
async def handle_voice_or_video_note(message: Message) -> None:
    """
    Точка входа для голосовых сообщений и видео-кружочков во всех топиках.

    Фильтрует чаты, валидирует лимиты длительности и применяет троттлинг.
    Запускает асинхронный пайплайн распознавания речи с индикатором статуса.

    Ничего не возвращает.
    """

    if not is_allowed_chat(message.chat.id, message.chat.type):
        return

    meta = extract_audio_meta(message)
    if not meta.file_id:
        return

    if not await _check_and_acquire_voice(message, meta):
        return

    status_msg = await message.reply(format_transcription_status())
    await process_audio_pipeline(meta.file_id, meta.sender, meta.duration, message, status_msg, meta.user_id)
