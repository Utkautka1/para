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


@router.message(F.message_thread_id == config.HW_INPUT_TOPIC_THREAD_ID)
async def handle_new_homework(msg: Message, bot: Bot) -> None:
    """
    Отлавливает любое новое входящее ДЗ (фото, файлы, текст) в топике ДЗ.
    """
    if await is_message_processed(msg.message_id):
        log.debug(f"Сообщение {msg.message_id} уже было обработано ранее. Пропускаем.")
        return

    log.info(f"Получено новое ДЗ в топике {msg.message_thread_id} (msg_id={msg.message_id})")
    await mark_message_processed(msg.message_id)

    img_bytes = None
    if msg.photo:
        file = await bot.get_file(msg.photo[-1].file_id)
        file_io = await bot.download_file(file.file_path)
        img_bytes = file_io.read()
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image"):
        file = await bot.get_file(msg.document.file_id)
        file_io = await bot.download_file(file.file_path)
        img_bytes = file_io.read()

    text_prompt = msg.caption or msg.text
    await process_homework_media(bot, msg, img_bytes, text_prompt)
