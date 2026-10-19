"""
Модуль извлечения и парсинга полезной нагрузки задач ДЗ.

Скачивает вложения через Telegram Bot API и преобразует файлы
различных форматов (изображения, DOCX, PDF, код) в мультимодальный
формат запроса для модели DeepSeek.
"""

import asyncio
import io

from aiogram import Bot

import config
from core.logger import get_logger

log = get_logger("solver_payload")
MAX_FILE_SIZE = config.HW_MAX_FILE_SIZE


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
        txt = txt[: config.HW_MAX_PROMPT_TEXT_LENGTH] + "\n...[Текст обрезан]..."

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
