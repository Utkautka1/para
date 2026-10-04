"""
Сервис-воркер решения домашних заданий через DeepSeek.

Работает в бесконечном цикле:
  1. Извлекает задачу из Redis-очереди hw:tasks:queue (BLPOP)
  2. Скачивает и парсит прикреплённый файл (изображение, docx, pdf)
  3. Отправляет запрос в DeepSeek API (stateless)
  4. Формирует .docx файл с решением по ГОСТ
  5. Отправляет документ в топик «Готовое ДЗ» (ID 3951)
"""

import asyncio
import io
import os
import uuid
from typing import List, Optional, Tuple
from aiogram import Bot
from aiogram.types import FSInputFile
import config
from core.bot import bot
from core.logger import get_logger
from core.redis import init_redis, redis_client
from services.deepseek_solver import solve_homework
from services.doc_generator import create_solution_docx
from services.redis_cache import ack_hw_task, pop_hw_task, recover_stale_hw_tasks

log = get_logger("solver_worker")
MAX_FILE_SIZE = 20 * 1024 * 1024


def build_post_link(chat_id: int, message_id: int) -> str:
    """Формирует прямую ссылку на оригинальное сообщение задания в Telegram."""
    clean_id = str(chat_id).replace("-100", "")
    return f"https://t.me/c/{clean_id}/{message_id}"


async def download_file_bytes(tg_bot: Bot, file_id: str, file_size: int) -> Optional[bytes]:
    """Безопасно скачивает байты файла Telegram с лимитом размера 20 МБ."""
    if file_size > MAX_FILE_SIZE:
        log.warning(f"Файл {file_id} превышает лимит {MAX_FILE_SIZE} байт. Пропуск.")
        return None
    try:
        f_info = await tg_bot.get_file(file_id)
        if not f_info.file_path:
            return None
        downloaded = await tg_bot.download_file(f_info.file_path)
        return downloaded.read()
    except Exception as e:
        log.error(f"Ошибка скачивания файла {file_id}: {e}")
        return None


def extract_docx_data(doc_bytes: bytes) -> Tuple[str, List[bytes]]:
    """Извлекает весь текст и встроенные картинки из .docx документа."""
    import docx
    doc = docx.Document(io.BytesIO(doc_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            row_txt = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
            if row_txt:
                paragraphs.append(row_txt)
    images = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref and hasattr(rel.target_part, "blob"):
            images.append(rel.target_part.blob)
    return "\n".join(paragraphs), images


def extract_pdf_data(doc_bytes: bytes) -> str:
    """Извлекает текст со всех страниц PDF документа."""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(doc_bytes))
        pages = [p.extract_text() for p in reader.pages if p.extract_text()]
        return "\n\n".join(pages)
    except Exception as e:
        log.error(f"Ошибка парсинга PDF документа: {e}")
        return ""


def parse_file_payload(doc_bytes: bytes, file_name: str, mime: Optional[str], prompt: str) -> Tuple[Optional[bytes], Optional[str]]:
    """Разбирает байты файла (изображение, docx, pdf, текст) в формат для DeepSeek."""
    fn = file_name.lower()
    if (mime and mime.startswith("image")) or fn.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
        return doc_bytes, prompt or None
    if fn.endswith(".docx"):
        text, imgs = extract_docx_data(doc_bytes)
        combined = f"{prompt}\n\n[Текст из {file_name}]:\n{text}".strip()
        return (imgs[0] if imgs else None), combined or None
    if fn.endswith(".pdf"):
        pdf_txt = extract_pdf_data(doc_bytes)
        combined = f"{prompt}\n\n[Текст из PDF {file_name}]:\n{pdf_txt}".strip()
        return None, combined or None
    if fn.endswith((".txt", ".md", ".py", ".json", ".csv", ".c", ".cpp", ".js", ".java")):
        txt = doc_bytes.decode("utf-8", errors="ignore")
        return None, f"{prompt}\n\n[Содержимое {file_name}]:\n{txt}".strip()
    return None, prompt or None


async def resolve_task_payload(tg_bot: Bot, task: dict) -> Tuple[Optional[bytes], Optional[str]]:
    """Скачивает и подготавливает медиа/текст задания для передачи в нейросеть."""
    file_id = task.get("file_id")
    prompt = task.get("prompt") or ""
    if not file_id:
        return None, prompt or None
    f_size = task.get("file_size") or 0
    raw_bytes = await download_file_bytes(tg_bot, file_id, f_size)
    if not raw_bytes:
        return None, prompt or None
    f_name = task.get("file_name") or "file"
    mime = task.get("mime_type")
    return await asyncio.to_thread(parse_file_payload, raw_bytes, f_name, mime, prompt)


async def send_solution_to_telegram(tg_bot: Bot, task: dict, doc_path: str) -> None:
    """Отправляет готовый .docx файл решения в топик готовых ДЗ."""
    chat_id = task.get("chat_id", config.TOPIC_CHAT_ID)
    msg_id = task.get("message_id", 0)
    orig_link = build_post_link(chat_id, msg_id)
    caption = f"✅ <b>Готовое решение ДЗ</b>\n\n📌 Ссылка на задание: {orig_link}"
    doc_file = FSInputFile(doc_path, filename=f"Решение_ДЗ_{msg_id}.docx")
    await tg_bot.send_document(
        chat_id=config.TOPIC_CHAT_ID,
        message_thread_id=config.HW_OUTPUT_TOPIC_THREAD_ID,
        document=doc_file,
        caption=caption,
        parse_mode="HTML"
    )


async def notify_task_error(tg_bot: Bot, task: dict) -> None:
    """Отправляет уведомление об ошибке решения в чат пользователя."""
    try:
        chat_id = task.get("chat_id")
        msg_id = task.get("message_id")
        thread_id = task.get("message_thread_id")
        text = "⚠️ <b>Не удалось решить ДЗ.</b>\nПроверьте читаемость файла или повторите позже."
        await tg_bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=msg_id,
            message_thread_id=thread_id
        )
    except Exception as e:
        log.debug(f"Не удалось отправить уведомление об ошибке: {e}")


async def execute_single_task(tg_bot: Bot, task: dict) -> None:
    """Обрабатывает одну задачу: решает ДЗ в DeepSeek и отправляет документ."""
    msg_id = task.get("message_id", 0)
    doc_path = f"/tmp/solution_{uuid.uuid4().hex[:8]}_{msg_id}.docx"
    try:
        img_bytes, prompt = await resolve_task_payload(tg_bot, task)
        solution = await solve_homework(image_bytes=img_bytes, text_prompt=prompt)
        await asyncio.to_thread(create_solution_docx, solution, output_path=doc_path)
        await send_solution_to_telegram(tg_bot, task, doc_path)
        await ack_hw_task(task)
        log.info(f"✅ Решение ДЗ msg_id={msg_id} успешно доставлено в топик решений!")
    except Exception as e:
        log.error(f"❌ Сбой обработки ДЗ msg_id={msg_id}: {e}")
        await notify_task_error(tg_bot, task)
        await ack_hw_task(task)
    finally:
        if os.path.exists(doc_path):
            os.remove(doc_path)


async def run_solver_loop() -> None:
    """Бесконечный цикл чтения очереди задач и запуска решений."""
    log.info("Запущен рабочий цикл очереди решений para-solver...")
    while True:
        try:
            task = await pop_hw_task(timeout=2)
            if task:
                log.info(f"📥 Получена задача ДЗ из очереди: msg_id={task.get('message_id')}")
                await execute_single_task(bot, task)
            else:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            log.info("Остановка цикла solver_loop.")
            break
        except Exception as e:
            log.error(f"Ошибка в цикле solver_loop: {e}")
            await asyncio.sleep(2)


async def main() -> None:
    """Инициализация ресурсов и запуск сервиса para-solver."""
    log.info("=" * 60)
    log.info("ЗАПУСК Сервиса AI-Решения ДЗ (para-solver)")
    log.info(f"  Модель DeepSeek: {config.DEEPSEEK_MODEL_NAME}")
    log.info(f"  Топик приема: {config.HW_INPUT_TOPIC_THREAD_ID}")
    log.info(f"  Топик решений: {config.HW_OUTPUT_TOPIC_THREAD_ID}")
    log.info("=" * 60)
    await init_redis()
    await recover_stale_hw_tasks()
    try:
        await run_solver_loop()
    finally:
        if redis_client:
            await redis_client.aclose()
        await bot.session.close()
        log.info("Воркер para-solver корректно остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
