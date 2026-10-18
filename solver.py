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
import tempfile
import uuid

from aiogram import Bot
from aiogram.types import FSInputFile

import config
from core.bot import bot
from core.logger import get_logger
from core.redis import init_redis, redis_client
from core.redis_cache import (
    ack_hw_task,
    nack_hw_task,
    pop_hw_task,
    recover_stale_hw_tasks,
)
from integrations.deepseek import close_deepseek_client, solve_homework
from utils.doc_generator import create_solution_docx

log = get_logger("solver_worker")
MAX_FILE_SIZE = config.HW_MAX_FILE_SIZE
_SOLVER_SEMAPHORE = asyncio.Semaphore(config.SOLVER_MAX_CONCURRENT_TASKS)


def build_post_link(chat_id: int, message_id: int) -> str:
    """
    Формирует прямую t.me-ссылку на оригинальное сообщение задания в Telegram.

    Очищает префикс супергруппы '-100' для построения валидного deep-link URL.
    Позволяет студентам в топике готовых решений перейти к исходному вопросу.

    Возвращает строку постоянной ссылки вида https://t.me/c/...
    """

    clean_id = str(chat_id).replace("-100", "")

    return f"https://t.me/c/{clean_id}/{message_id}"


async def download_file_bytes(tg_bot: Bot, file_id: str, file_size: int) -> bytes | None:
    """
    Безопасно скачивает байты файла из Telegram с контролем лимита размера.

    Отклоняет файлы свыше 20 МБ для предотвращения переполнения оперативной памяти.
    Изолирует сетевые сбои Bot API и логирует подробности ошибки.

    Возвращает байты содержимого файла или None при сбое.
    """

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


def _extract_docx_images(doc) -> list[bytes]:
    """
    Извлекает бинарные данные встроенных изображений из структуры docx.

    Фильтрует внешние связи и отбирает релейшены с MIME-типом картинок.
    Используется для нахождения условий задач, оформленных сканами и скриншотами.

    Возвращает список байтов изображений документа.
    """

    images = []
    for rel in doc.part.rels.values():
        if getattr(rel, "is_external", False):
            continue
        if "image" in rel.target_ref and hasattr(rel.target_part, "blob"):
            images.append(rel.target_part.blob)

    return images


def extract_docx_data(doc_bytes: bytes) -> tuple[str, list[bytes]]:
    """
    Извлекает весь текстовый контент и встроенные изображения из .docx документа.

    Парсит параграфы, ячейки таблиц и встроенные иллюстрации для передачи в модель.
    Объединяет текстовые блоки через перевод строки.

    Возвращает кортеж (объединенный текст документа, список байтов изображений).
    """

    import docx

    doc = docx.Document(io.BytesIO(doc_bytes))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            row_txt = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
            if row_txt:
                paragraphs.append(row_txt)

    return "\n".join(paragraphs), _extract_docx_images(doc)


def extract_pdf_data(doc_bytes: bytes) -> str:
    """
    Извлекает текстовые слои со всех страниц переданного PDF-документа.

    Использует pypdf для постраничного чтения и сборки текста учебных методичек.
    При ошибках поврежденного документа возвращает пустую строку и логирует сбой.

    Возвращает строку с извлеченным текстом или пустую строку.
    """

    try:
        import pypdf

        reader = pypdf.PdfReader(io.BytesIO(doc_bytes))
        pages = [p.extract_text() for p in reader.pages if p.extract_text()]
        return "\n\n".join(pages)
    except Exception as e:
        log.error(f"Ошибка парсинга PDF документа: {e}")
        return ""


def _read_code_file_payload(doc_bytes: bytes, file_name: str, prompt: str) -> str:
    """
    Декодирует текстовый файл исходного кода с контролем максимальной длины.

    Обрезает чрезмерно длинные файлы во избежание переполнения контекста модели.
    Добавляет метаданные имени исходного файла к промпту.

    Возвращает объединенную строку промпта с содержимым файла.
    """

    txt = doc_bytes.decode("utf-8", errors="ignore")
    if len(txt) > config.HW_MAX_PROMPT_TEXT_LENGTH:
        txt = txt[:config.HW_MAX_PROMPT_TEXT_LENGTH] + "\n...[Текст обрезан]..."

    return f"{prompt}\n\n[Содержимое {file_name}]:\n{txt}".strip()


def parse_file_payload(
    doc_bytes: bytes, file_name: str, mime: str | None, prompt: str
) -> tuple[bytes | None, str | None]:
    """
    Разбирает байты файла (изображение, docx, pdf, текст) в формат для DeepSeek.

    Определяет тип файла по расширению и MIME-типу, извлекая текст и картинки.
    Адаптирует входящий документ для отправки в мультимодальный API.

    Возвращает кортеж (байты изображения или None, текст промпта или None).
    """

    fn = file_name.lower()
    if (mime and mime.startswith("image")) or fn.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
        return doc_bytes, prompt or None

    if fn.endswith(".docx"):
        text, imgs = extract_docx_data(doc_bytes)
        return (imgs[0] if imgs else None), f"{prompt}\n\n[Текст из {file_name}]:\n{text}".strip() or None

    if fn.endswith(".pdf"):
        return None, f"{prompt}\n\n[Текст из PDF {file_name}]:\n{extract_pdf_data(doc_bytes)}".strip() or None

    if fn.endswith((".txt", ".md", ".py", ".json", ".csv", ".c", ".cpp", ".js", ".java")):
        return None, _read_code_file_payload(doc_bytes, file_name, prompt)

    return None, prompt or None


async def resolve_task_payload(tg_bot: Bot, task: dict) -> tuple[bytes | None, str | None]:
    """
    Скачивает и подготавливает медиа/текст задания для передачи в нейросеть.

    Выгружает вложенный файл через Telegram Bot API и парсит его в пуле потоков.
    При отсутствии файла возвращает исходный текстовый промпт.

    Возвращает кортеж (байты изображения или None, текст задания или None).
    """

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
    """
    Отправляет готовый .docx файл решения в топик готовых ДЗ.

    Формирует кликабельную подпись со ссылкой на исходное задание в группе.
    Публикует документ по ГОСТ в целевой топик готовых домашних заданий.

    Ничего не возвращает.
    """

    chat_id = task.get("chat_id", config.TOPIC_CHAT_ID)
    msg_id = task.get("message_id", 0)
    caption = f"✅ <b>Готовое решение ДЗ</b>\n\n📌 Ссылка на задание: {build_post_link(chat_id, msg_id)}"
    doc_file = FSInputFile(doc_path, filename=f"Решение_ДЗ_{msg_id}.docx")

    await tg_bot.send_document(
        chat_id=config.TOPIC_CHAT_ID,
        message_thread_id=config.HW_OUTPUT_TOPIC_THREAD_ID,
        document=doc_file,
        caption=caption,
        parse_mode="HTML",
    )


async def notify_task_error(tg_bot: Bot, task: dict) -> None:
    """
    Отправляет уведомление об ошибке решения в чат или топик пользователя.

    Срабатывает при исчерпании лимита повторных попыток обработки задания.
    Информирует студента о необходимости перепроверить читаемость файла.

    Ничего не возвращает.
    """

    try:
        await tg_bot.send_message(
            chat_id=task.get("chat_id"),
            text="⚠️ <b>Не удалось решить ДЗ.</b>\nПроверьте читаемость файла или повторите позже.",
            reply_to_message_id=task.get("message_id"),
            message_thread_id=task.get("message_thread_id"),
        )
    except Exception as e:
        log.debug(f"Не удалось отправить уведомление об ошибке: {e}")


async def execute_single_task(tg_bot: Bot, task: dict) -> None:
    """
    Обрабатывает одну задачу: решает ДЗ в DeepSeek и отправляет документ.

    Генерирует .docx документ, отправляет в топик решений и подтверждает задачу (ACK).
    При сбое инициирует повторную постановку в очередь (NACK) или шлет ошибку.

    Ничего не возвращает.
    """

    msg_id = task.get("message_id", 0)
    doc_path = os.path.join(tempfile.gettempdir(), f"solution_{uuid.uuid4().hex[:8]}_{msg_id}.docx")
    try:
        img_bytes, prompt = await resolve_task_payload(tg_bot, task)
        solution = await solve_homework(image_bytes=img_bytes, text_prompt=prompt)
        await asyncio.to_thread(create_solution_docx, solution, output_path=doc_path)
        await send_solution_to_telegram(tg_bot, task, doc_path)
        await ack_hw_task(task)
        log.info(f"✅ Решение ДЗ msg_id={msg_id} успешно доставлено в топик решений!")
    except Exception as e:
        log.error(f"❌ Сбой обработки ДЗ msg_id={msg_id}: {e}")
        if not await nack_hw_task(task, max_retries=config.HW_MAX_TASK_RETRIES):
            await notify_task_error(tg_bot, task)
    finally:
        if os.path.exists(doc_path):
            os.remove(doc_path)


async def _guarded_execute_task(tg_bot: Bot, task: dict) -> None:
    """
    Исполняет задачу под семафором параллелизма для защиты от перегрузки.

    Ограничивает число одновременно решаемых задач в DeepSeek API.
    Предотвращает исчерпание лимитов параллельных вызовов и локальных ресурсов.

    Ничего не возвращает.
    """

    async with _SOLVER_SEMAPHORE:
        await execute_single_task(tg_bot, task)


async def _drain_active_tasks(active_tasks: set[asyncio.Task]) -> None:
    """
    Корректно ожидает завершения всех запущенных задач при остановке сервиса.

    Предотвращает потерю выполняемых расчетов DeepSeek при перезапуске контейнера.
    Подавляет исключения через return_exceptions=True.

    Ничего не возвращает.
    """

    log.info("Остановка цикла solver_loop, ожидание активных задач...")
    if active_tasks:
        await asyncio.gather(*active_tasks, return_exceptions=True)


async def run_solver_loop() -> None:
    """
    Бесконечный цикл чтения очереди задач и параллельного запуска решений.

    Извлекает новые задачи из Redis и распределяет их по фоновым воркерам.
    Контролирует максимальное количество параллельных задач.

    Ничего не возвращает.
    """

    log.info("Запущен рабочий цикл очереди решений para-solver...")
    active_tasks: set[asyncio.Task] = set()
    while True:
        try:
            active_tasks = {t for t in active_tasks if not t.done()}
            if len(active_tasks) >= config.SOLVER_MAX_CONCURRENT_TASKS:
                await asyncio.sleep(0.5)
                continue

            task = await pop_hw_task(timeout=2)
            if task:
                active_tasks.add(asyncio.create_task(_guarded_execute_task(bot, task)))
        except asyncio.CancelledError:
            await _drain_active_tasks(active_tasks)
            break
        except Exception as e:
            log.error(f"Ошибка в цикле solver_loop: {e}")
            await asyncio.sleep(2)


async def main() -> None:
    """
    Инициализация системных ресурсов и запуск воркера решений para-solver.

    Восстанавливает зависшие задачи из очереди обработки при старте.
    В блоке finally гарантированно закрывает соединения с DeepSeek, Redis и Telegram.

    Ничего не возвращает.
    """

    log.info("=" * 60)
    log.info("ЗАПУСК Сервиса AI-Решения ДЗ (para-solver)")
    log.info(f"  Модель DeepSeek: {config.DEEPSEEK_MODEL_NAME}")
    log.info("=" * 60)
    await init_redis()
    await recover_stale_hw_tasks()

    try:
        await run_solver_loop()
    finally:
        await close_deepseek_client()
        if redis_client:
            await redis_client.aclose()

        await bot.session.close()
        log.info("Воркер para-solver корректно остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
