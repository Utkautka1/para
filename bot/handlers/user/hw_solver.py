"""
Хэндлер перехвата новых ДЗ в целевом топике (ID 405).

Отлавливает фото, документы (.docx, .pdf, .txt, код) и текстовые задачи,
валидирует их, проверяет антиспам и ставит задачу в очередь Redis (hw:tasks:queue)
для фонового воркера para-solver.
"""

import hashlib

from aiogram import Bot, F, Router
from aiogram.types import Message, ReactionTypeEmoji

import config
from core.logger import get_logger
from core.redis_cache import (
    check_user_rate_limit,
    is_hash_processed,
    is_message_processed,
    mark_hash_processed,
    mark_message_processed,
    push_hw_task,
)

log = get_logger("hw_handler")
router = Router()

# Максимальный размер файла (20 МБ) — ограничение Telegram Bot API
MAX_HW_FILE_SIZE = 20 * 1024 * 1024


def combine_prompt_and_instructions(msg: Message, target: Message) -> str:
    """Объединяет инструкцию из подписи/текста реплая и основное задание."""
    u_text = msg.text or msg.caption or ""
    t_text = target.caption or target.text or ""
    if u_text and t_text and u_text != t_text:
        return f"Инструкция: {u_text}\nЗадание: {t_text}"
    return u_text or t_text or ""


def is_valid_homework_prompt(text: str | None, has_media: bool) -> bool:
    """
    Проверяет, содержит ли сообщение запрос на решение учебной задачи.

    'Голые' медиафайлы без промпта не берутся в обработку, чтобы бот не трогал
    учебные материалы и конспекты, загружаемые в топик.
    """
    if not text:
        return False
    t = text.lower().strip()
    flood_words = {"привет", "хай", "как дела", "спасибо", "спасбо", "спсибо", "ок", "понял", "ку"}
    if t in flood_words or len(t) < 4:
        return False
    kw_list = [
        "реши", "вычисли", "найди", "доказать", "дз", "вариант", "задача",
        "задание", "номер", "№", "=", "+", "-", "?", "ответ"
    ]
    return any(kw in t for kw in kw_list) or len(t) >= 25


def extract_media_meta(msg: Message, target: Message) -> tuple[str | None, str | None, str | None, str | None, int]:
    """Извлекает идентификаторы и метаданные медиафайла (фото или документа)."""
    m = msg if (msg.photo or msg.document) else target
    if m.photo:
        p = m.photo[-1]
        return p.file_id, p.file_unique_id, "image.jpg", "image/jpeg", p.file_size or 0
    if m.document:
        d = m.document
        return d.file_id, d.file_unique_id, d.file_name or "doc", d.mime_type, d.file_size or 0
    return None, None, None, None, 0


def compute_content_hash(text: str | None, unique_id: str | None) -> str:
    """Вычисляет SHA256 хэш промпта и уникального ID файла для защиты от дубликатов."""
    hasher = hashlib.sha256()
    if text:
        hasher.update(text.encode("utf-8"))
    if unique_id:
        hasher.update(unique_id.encode("utf-8"))
    return hasher.hexdigest()


async def is_hw_allowed(msg: Message, target: Message, user_id: int) -> bool:
    """Проверяет лимиты пользователя, статус обработки и наличие учебного содержимого."""
    if user_id != config.ALLOWED_USER_ID and not await check_user_rate_limit(user_id):
        log.warning(f"⚠️ Превышен rate-limit для пользователя {user_id}.")
        return False
    if await is_message_processed(msg.message_id):
        log.debug(f"Сообщение {msg.message_id} уже обработано. Пропуск.")
        return False
    has_media = bool(msg.photo or msg.document or target.photo or target.document)
    prompt = combine_prompt_and_instructions(msg, target)
    if not is_valid_homework_prompt(prompt, has_media):
        log.info(f"ℹ️ Пропуск сообщения без задания (msg_id={msg.message_id}): '{prompt}'")
        return False
    return True


async def acknowledge_hw_task(bot: Bot, msg: Message) -> None:
    """Ставит реакцию-подтверждение о принятии задачи в очередь нейросети."""
    try:
        await bot.set_message_reaction(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reaction=[ReactionTypeEmoji(emoji="👀")]
        )
    except Exception as e:
        log.debug(f"Не удалось поставить реакцию на msg_id={msg.message_id}: {e}")


async def dispatch_hw_task(
    bot: Bot,
    msg: Message,
    user_id: int,
    prompt: str,
    meta: tuple[str | None, str | None, str | None, int]
) -> None:
    """Формирует payload и отправляет задачу в очередь воркера para-solver."""
    f_id, f_name, mime, f_size = meta
    task = {
        "chat_id": msg.chat.id,
        "message_id": msg.message_id,
        "message_thread_id": msg.message_thread_id,
        "user_id": user_id,
        "prompt": prompt,
        "file_id": f_id,
        "file_name": f_name,
        "mime_type": mime,
        "file_size": f_size
    }
    await push_hw_task(task)
    await acknowledge_hw_task(bot, msg)


async def validate_hw_file_size(bot: Bot, msg: Message, f_size: int, f_name: str | None) -> bool:
    """Проверяет размер медиафайла (не более 20 МБ) для предотвращения OOM."""
    if f_size > MAX_HW_FILE_SIZE:
        log.warning(f"⚠️ Файл '{f_name}' превышает лимит 20 МБ ({f_size} байт). Отклонено.")
        try:
            await bot.set_message_reaction(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                reaction=[ReactionTypeEmoji(emoji="🤷‍♂️")]
            )
        except Exception as e:
            log.debug(f"Не удалось выставить реакцию на тяжелый файл: {e}")
        return False
    return True


@router.message(
    (F.chat.id == config.TOPIC_CHAT_ID) &
    (F.message_thread_id == config.HW_INPUT_TOPIC_THREAD_ID)
)
async def handle_new_homework(msg: Message, bot: Bot) -> None:
    """Перехватывает сообщение с ДЗ и отправляет в очередь воркера solver."""
    user_id = msg.from_user.id if msg.from_user else 0
    target = msg.reply_to_message if msg.reply_to_message else msg
    if not await is_hw_allowed(msg, target, user_id):
        return

    prompt = combine_prompt_and_instructions(msg, target)
    f_id, u_id, f_name, mime, f_size = extract_media_meta(msg, target)
    if not await validate_hw_file_size(bot, msg, f_size, f_name):
        return

    c_hash = compute_content_hash(prompt, u_id)
    if await is_hash_processed(c_hash):
        log.warning(f"⚠️ Повтор ДЗ по SHA256 (msg_id={msg.message_id}). Пропуск.")
        return

    await mark_hash_processed(c_hash)
    await mark_message_processed(msg.message_id)
    meta = (f_id, f_name, mime, f_size)
    await dispatch_hw_task(bot, msg, user_id, prompt, meta)
