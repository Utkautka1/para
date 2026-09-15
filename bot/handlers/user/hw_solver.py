"""
Хэндлер обработки новых ДЗ в целевом топике (ID 405).

Отлавливает фото, документы-картинки и тексты, отправляет в DeepSeek Vision,
сохраняет ID обработанных сообщений в Redis и отправляет готовый файл в топик "Готовое ДЗ" (ID 3951).
"""

import os
from typing import Optional
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
import config
from core.logger import get_logger
from services.redis_cache import (
    is_message_processed,
    mark_message_processed,
    check_user_rate_limit,
    is_hash_processed,
    mark_hash_processed
)
from services.deepseek_solver import solve_homework
from services.doc_generator import create_solution_docx

log = get_logger("hw_handler")
router = Router()

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


def build_original_post_link(chat_id: int, message_id: int) -> str:
    """
    Формирует прямую ссылку на оригинальное сообщение в Telegram.
    """
    clean_id = str(chat_id).replace("-100", "")
    return f"https://t.me/c/{clean_id}/{message_id}"


async def download_image_bytes(bot: Bot, file_id: str, file_size: Optional[int]) -> Optional[bytes]:
    """
    Безопасно скачивает байты файла изображения с ограничением по размеру.
    """
    if file_size and file_size > MAX_FILE_SIZE_BYTES:
        log.warning(f"Файл превышает лимит {MAX_FILE_SIZE_BYTES} байт. Пропускаем.")
        return None
    try:
        file = await bot.get_file(file_id)
        file_io = await bot.download_file(file.file_path)
        return file_io.read()
    except Exception as e:
        log.error(f"Ошибка скачивания файла {file_id}: {e}")
        return None


async def extract_image_bytes(bot: Bot, target_msg: Message) -> Optional[bytes]:
    """
    Извлекает байты картинки из сообщения или прикрепленного документа.
    """
    if target_msg.photo:
        photo = target_msg.photo[-1]
        return await download_image_bytes(bot, photo.file_id, photo.file_size)
    elif target_msg.document and target_msg.document.mime_type and target_msg.document.mime_type.startswith("image"):
        doc = target_msg.document
        return await download_image_bytes(bot, doc.file_id, doc.file_size)
    return None


async def process_homework_media(bot: Bot, msg: Message, img_bytes: Optional[bytes], prompt: Optional[str]) -> None:
    """
    Обрабатывает медиа ДЗ: решает в DeepSeek, создает документ и отправляет в топик решений.
    """
    solution = await solve_homework(image_bytes=img_bytes, text_prompt=prompt)
    doc_path = f"/tmp/solution_{msg.message_id}.docx"
    create_solution_docx(solution, output_path=doc_path)

    orig_link = build_original_post_link(msg.chat.id, msg.message_id)
    caption = f"✅ **Готовое решение ДЗ**\n\n📌 Ссылка на оригинальное задание: {orig_link}"

    await bot.send_document(
        chat_id=config.TOPIC_CHAT_ID,
        message_thread_id=config.HW_OUTPUT_TOPIC_THREAD_ID,
        document=FSInputFile(doc_path, filename=f"Решение_ДЗ_{msg.message_id}.docx"),
        caption=caption,
        parse_mode="Markdown"
    )
    if os.path.exists(doc_path):
        os.remove(doc_path)


def is_valid_homework_prompt(text: Optional[str], has_image: bool) -> bool:
    """
    Проверяет, содержит ли сообщение реальную учебную задачу или картинку.
    """
    if has_image:
        return True
    if not text:
        return False

    t = text.lower().strip()
    flood_words = {"привет", "хай", "как дела", "спасибо", "спасбо", "спсибо", "ок", "понял", "ку"}
    if t in flood_words or len(t) < 5:
        return False

    hw_keywords = ["реши", "вычисли", "найди", "доказать", "дз", "вариант", "задача", "задание", "номер", "№", "=", "+", "-"]
    return any(kw in t for kw in hw_keywords) or len(t) >= 25


def compute_prompt_hash(text: Optional[str], img_bytes: Optional[bytes]) -> str:
    """
    Вычисляет SHA256 хэш промпта и картинки для защиты от абуза дубликатами.
    """
    import hashlib
    hasher = hashlib.sha256()
    if text:
        hasher.update(text.encode('utf-8'))
    if img_bytes:
        hasher.update(img_bytes)
    return hasher.hexdigest()


async def check_and_mark_duplicate_hash(text: Optional[str], img_bytes: Optional[bytes]) -> bool:
    """
    Проверяет и маркирует SHA256 хэш контента. Возвращает True если это дубликат.
    """
    c_hash = compute_prompt_hash(text, img_bytes)
    if await is_hash_processed(c_hash):
        return True
    await mark_hash_processed(c_hash)
    return False


async def is_homework_msg_allowed(msg: Message, target_msg: Message, user_id: int) -> bool:
    """
    Проверяет рат-лимит, статус обработки и валидность бытового текста.
    """
    if not await check_user_rate_limit(user_id):
        log.warning(f"⚠️ Превышен rate-limit для пользователя {user_id}.")
        return False

    if await is_message_processed(target_msg.message_id):
        return False

    has_photo = bool(target_msg.photo)
    has_doc_img = bool(target_msg.document and target_msg.document.mime_type and target_msg.document.mime_type.startswith("image"))
    has_image = has_photo or has_doc_img
    text_prompt = msg.text or msg.caption or target_msg.caption or target_msg.text

    if not has_image and not is_valid_homework_prompt(text_prompt, False):
        log.info(f"ℹ️ Игнорируем бытовое сообщение без задания (msg_id={msg.message_id})")
        return False

    return True


@router.message(F.message_thread_id == config.HW_INPUT_TOPIC_THREAD_ID)
async def handle_new_homework(msg: Message, bot: Bot) -> None:
    """
    Отлавливает новое ДЗ с поддержкой защиты от спама (до 25 строк).
    """
    user_id = msg.from_user.id if msg.from_user else 0
    target_msg = msg.reply_to_message if msg.reply_to_message else msg

    if not await is_homework_msg_allowed(msg, target_msg, user_id):
        return

    img_bytes = await extract_image_bytes(bot, target_msg)
    text_prompt = msg.text or msg.caption or target_msg.caption or target_msg.text

    if await check_and_mark_duplicate_hash(text_prompt, img_bytes):
        log.warning(f"⚠️ Повтор ДЗ по SHA256 хэшу (msg_id={msg.message_id}). Пропуск.")
        return

    await mark_message_processed(target_msg.message_id)
    if target_msg.message_id != msg.message_id:
        await mark_message_processed(msg.message_id)

    log.info(f"🚀 Запуск авторешения ДЗ в DeepSeek (msg_id={msg.message_id})")
    await process_homework_media(bot, target_msg, img_bytes, text_prompt)
