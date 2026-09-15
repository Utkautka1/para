"""
Хэндлер обработки новых ДЗ в целевом топике (ID 405).

Отлавливает фото, документы (.docx, .pdf, .txt, исходный код) и тексты, отправляет в DeepSeek Vision,
сохраняет ID обработанных сообщений в Redis и отправляет готовый файл в топик "Готовое ДЗ" (ID 3951).
"""

import io
import os
from typing import Optional, List, Tuple
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
    Безопасно скачивает байты файла с ограничением по размеру.
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


def extract_docx_content(doc_bytes: bytes) -> Tuple[str, List[bytes]]:
    """
    Извлекает весь текст и картинки из .docx файла.
    """
    import docx
    doc = docx.Document(io.BytesIO(doc_bytes))
    full_text = []
    for p in doc.paragraphs:
        if p.text.strip():
            full_text.append(p.text.strip())
    for table in doc.tables:
        for row in table.rows:
            full_text.append(" | ".join(cell.text.strip() for cell in row.cells if cell.text.strip()))

    images = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref and hasattr(rel.target_part, 'blob'):
            images.append(rel.target_part.blob)

    return "\n".join(full_text), images


def extract_pdf_content(doc_bytes: bytes) -> str:
    """
    Извлекает весь текст из PDF документа.
    """
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(doc_bytes))
        pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        return "\n\n".join(pages)
    except Exception as e:
        log.error(f"Ошибка парсинга PDF: {e}")
        return ""


def parse_document_bytes(doc_bytes: bytes, fname: str, mime: Optional[str], prompt: str) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Разбирает байты документа (изображение, docx, pdf или текст).
    """
    fn = fname.lower()
    if (mime and mime.startswith("image")) or fn.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
        return doc_bytes, prompt or None

    if fn.endswith('.docx'):
        d_text, d_imgs = extract_docx_content(doc_bytes)
        combined = f"{prompt}\n\n[Текст из {fname}]:\n{d_text}".strip()
        return (d_imgs[0] if d_imgs else None), combined or None

    if fn.endswith('.pdf'):
        pdf_text = extract_pdf_content(doc_bytes)
        combined = f"{prompt}\n\n[Текст из PDF {fname}]:\n{pdf_text}".strip()
        return None, combined or None

    if fn.endswith(('.txt', '.md', '.py', '.json', '.csv', '.c', '.cpp', '.js', '.pas', '.java')):
        d_text = doc_bytes.decode('utf-8', errors='ignore')
        return None, f"{prompt}\n\n[Содержимое {fname}]:\n{d_text}".strip()

    return None, prompt or None


def combine_prompt_and_instructions(msg: Message, target_msg: Message) -> str:
    """
    Объединяет инструкцию из подписи/текста реплая и основное задание.
    """
    u_text = msg.text or msg.caption or ""
    t_text = target_msg.caption or target_msg.text or ""
    if u_text and t_text and u_text != t_text:
        return f"Инструкция пользователя: {u_text}\nТекст задания: {t_text}"
    return u_text or t_text or ""


async def extract_homework_payload(bot: Bot, msg: Message, target_msg: Message) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Извлекает картинку и полный промпт с пользовательскими инструкциями.
    """
    m = msg if (msg.photo or msg.document) else target_msg
    prompt = combine_prompt_and_instructions(msg, target_msg)

    if m.photo:
        p_bytes = await download_image_bytes(bot, m.photo[-1].file_id, m.photo[-1].file_size)
        return p_bytes, prompt or None

    if m.document:
        doc = m.document
        doc_b = await download_image_bytes(bot, doc.file_id, doc.file_size)
        if not doc_b:
            return None, prompt or None
        return parse_document_bytes(doc_b, doc.file_name or "doc", doc.mime_type, prompt)

    return None, prompt or None


async def process_homework_media(bot: Bot, msg: Message, img_bytes: Optional[bytes], prompt: Optional[str]) -> None:
    """
    Обрабатывает медиа ДЗ: решает в DeepSeek, создает документ и отправляет в топик решений.
    """
    try:
        solution = await solve_homework(image_bytes=img_bytes, text_prompt=prompt)
        doc_path = f"/tmp/solution_{msg.message_id}.docx"
        create_solution_docx(solution, output_path=doc_path)

        orig_link = build_original_post_link(msg.chat.id, msg.message_id)
        caption = f"✅ <b>Готовое решение ДЗ</b>\n\n📌 Ссылка на оригинальное задание: {orig_link}"

        await bot.send_document(
            chat_id=config.TOPIC_CHAT_ID,
            message_thread_id=config.HW_OUTPUT_TOPIC_THREAD_ID,
            document=FSInputFile(doc_path, filename=f"Решение_ДЗ_{msg.message_id}.docx"),
            caption=caption,
            parse_mode="HTML"
        )
        log.info(f"✅ Документ решения успешно отправлен в топик решений (msg_id={msg.message_id})")
    except Exception as e:
        log.error(f"❌ Ошибка отправки документа решения в Telegram: {e}")
    finally:
        if 'doc_path' in locals() and os.path.exists(doc_path):
            os.remove(doc_path)


def is_valid_homework_prompt(text: Optional[str], has_media: bool) -> bool:
    """
    Проверяет, содержит ли сообщение учебную задачу, картинку или документ.
    """
    if has_media:
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
    Проверяет рат-лимит, статус обработки и валидность медиа/текста.
    """
    if not await check_user_rate_limit(user_id):
        log.warning(f"⚠️ Превышен rate-limit для пользователя {user_id}.")
        return False

    if await is_message_processed(msg.message_id):
        log.debug(f"Сообщение {msg.message_id} уже обработано. Пропуск.")
        return False

    has_media = bool(msg.photo or msg.document or target_msg.photo or target_msg.document)
    text_prompt = msg.text or msg.caption or target_msg.caption or target_msg.text

    if not is_valid_homework_prompt(text_prompt, has_media):
        log.info(f"ℹ️ Игнорируем бытовое текстовое сообщение без задания (msg_id={msg.message_id}): '{text_prompt}'")
        return False

    return True


@router.message(F.message_thread_id == config.HW_INPUT_TOPIC_THREAD_ID)
async def handle_new_homework(msg: Message, bot: Bot) -> None:
    """
    Отлавливает новое ДЗ (фото, docx, файлы, текст) с защитой от спама.
    """
    user_id = msg.from_user.id if msg.from_user else 0
    target_msg = msg.reply_to_message if msg.reply_to_message else msg

    if not await is_homework_msg_allowed(msg, target_msg, user_id):
        return

    img_bytes, text_prompt = await extract_homework_payload(bot, msg, target_msg)

    if await check_and_mark_duplicate_hash(text_prompt, img_bytes):
        log.warning(f"⚠️ Повтор ДЗ по SHA256 хэшу (msg_id={msg.message_id}). Пропуск.")
        return

    await mark_message_processed(msg.message_id)

    log.info(f"🚀 Запуск авторешения ДЗ в DeepSeek (msg_id={msg.message_id})")
    await process_homework_media(bot, msg, img_bytes, text_prompt)
