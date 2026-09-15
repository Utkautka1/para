"""
Хэндлер обработки новых ДЗ в целевом топике (ID 405).

Отлавливает фото, документы-картинки и тексты, отправляет в DeepSeek Vision,
сохраняет ID обработанных сообщений в Redis и отправляет готовый файл в топик "Готовое ДЗ" (ID 3951).
"""

import os
from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
import config
from core.logger import get_logger
from services.redis_cache import is_message_processed, mark_message_processed
from services.deepseek_solver import solve_homework
from services.doc_generator import create_solution_docx

log = get_logger("hw_handler")
router = Router()


def build_original_post_link(chat_id: int, message_id: int) -> str:
    """
    Формирует прямую ссылку на оригинальное сообщение в Telegram.

    :param chat_id: ID супергруппы
    :param message_id: ID сообщения
    :return: Ссылка t.me/c/...
    """
    clean_id = str(chat_id).replace("-100", "")
    return f"https://t.me/c/{clean_id}/{message_id}"


async def process_homework_media(bot: Bot, msg: Message, img_bytes: bytes, prompt: str | None) -> None:
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


def is_valid_homework_prompt(text: str | None, has_image: bool) -> bool:
    """
    Проверяет, содержит ли сообщение реальную учебную задачу или картинку.
    Игнорирует флуд ('Привет', 'Как дела?') для защиты баланса DeepSeek API.
    """
    if has_image:
        return True
    if not text:
        return False
    
    t = text.lower().strip()
    # Простые бытовые сообщения
    flood_words = {"привет", "хай", "как дела", "спасибо", "спасбо", "спсибо", "ок", "понял", "ку"}
    if t in flood_words or len(t) < 5:
        return False
    
    # Ключевые слова учебных заданий
    hw_keywords = ["реши", "вычисли", "найди", "доказать", "дз", "вариант", "задача", "задание", "номер", "№", "=", "+", "-"]
    if any(kw in t for kw in hw_keywords) or len(t) >= 25:
        return True
    return False


@router.message(F.message_thread_id == config.HW_INPUT_TOPIC_THREAD_ID)
async def handle_new_homework(msg: Message, bot: Bot) -> None:
    """
    Отлавливает новое входящее ДЗ в топике ДЗ с фильтрацией бытового флуда.
    """
    target_msg = msg.reply_to_message if msg.reply_to_message else msg

    img_bytes = None
    if target_msg.photo:
        file = await bot.get_file(target_msg.photo[-1].file_id)
        file_io = await bot.download_file(file.file_path)
        img_bytes = file_io.read()
    elif target_msg.document and target_msg.document.mime_type and target_msg.document.mime_type.startswith("image"):
        file = await bot.get_file(target_msg.document.file_id)
        file_io = await bot.download_file(file.file_path)
        img_bytes = file_io.read()

    text_prompt = msg.text or msg.caption or target_msg.caption or target_msg.text
    has_image = img_bytes is not None

    # Фильтр бытовых сообщений без картинок
    if not is_valid_homework_prompt(text_prompt, has_image):
        log.debug(f"Игнорируем сообщение без задания (msg_id={msg.message_id}): '{text_prompt}'")
        return

    if await is_message_processed(target_msg.message_id):
        log.debug(f"Задание из сообщения {target_msg.message_id} уже было обработано. Пропускаем.")
        return

    log.info(f"Получено ДЗ в топике {msg.message_thread_id} (msg_id={msg.message_id}, target_id={target_msg.message_id})")
    await mark_message_processed(target_msg.message_id)
    if target_msg.message_id != msg.message_id:
        await mark_message_processed(msg.message_id)

    await process_homework_media(bot, target_msg, img_bytes, text_prompt)


