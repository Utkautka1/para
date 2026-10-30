"""
Модуль загрузки и парсинга контактов преподавателей с Yandex Disk.

Скачивает файл .docx с Yandex Disk через публичный REST API Яндекс Диска,
извлекает из таблицы ФИО преподавателей и их персональные Zoom/Телемост ссылки.
"""

import asyncio
import io
import time
import zipfile
from typing import Any, TypedDict

import defusedxml.ElementTree as ET
import httpx

from config import (
    DOCX_CACHE_TTL_SECONDS,
    DOCX_MIN_REFRESH_INTERVAL_SECONDS,
    YANDEX_DOC_PUBLIC_URL,
)
from core.logger import get_logger

log = get_logger("docx_parser")

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


class TeacherData(TypedDict):
    """
    Типизированный словарь с контактной информацией преподавателя.

    full_name: Полное имя преподавателя (ФИО) в каноническом регистре.
    link_info: Ссылка на онлайн-конференцию (Zoom, Телемост) с паролем.
    """

    full_name: str
    link_info: str


# Кэш данных: (timestamp, dict_teachers)
_CACHE: tuple[float, dict[str, TeacherData]] = (0.0, {})
_DOCX_LOCK: asyncio.Lock | None = None


async def fetch_docx_bytes() -> bytes | None:
    """
    Загружает бинарные байты docx-файла с Яндекс Диска через публичный API.

    Разрешает публичный ключ в прямую ссылку на скачивание и скачивает контент
    с ограничением времени ожидания до 15 секунд.

    Возвращает сырые байты файла или None при сетевой ошибке.
    """
    api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={YANDEX_DOC_PUBLIC_URL}"
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            res = await client.get(api_url)
            if res.status_code != 200:
                log.error("Ошибка API Яндекс Диска: HTTP %s", res.status_code)
                return None
            file_url = res.json().get("file")
            if not file_url:
                log.error("API Яндекс Диска не вернул ссылку на скачивание")
                return None
            doc_res = await client.get(file_url)
            return doc_res.content
    except Exception as e:
        log.error("Исключение при скачивании файла с Яндекс Диска: %s", e)
        return None


def extract_row_texts(row_elem: Any) -> tuple[str, str]:
    """
    Извлекает нормализованное ФИО преподавателя и ссылку из XML-строки таблицы docx.

    Парсит дочерние ячейки w:tc с учетом пространства имен OpenXML, очищая
    лишние пробелы и неразрывные переносы строк.

    Возвращает кортеж (полное_имя, строка_ссылки) или ("", "") при неполной строке.
    """
    cells = row_elem.findall(".//w:tc", NS)
    if len(cells) < 3:
        return ("", "")
    name_texts = [t.text for t in cells[0].findall(".//w:t", NS) if t.text]
    name = " ".join(" ".join(name_texts).split()).strip()
    link_texts = [t.text for t in cells[2].findall(".//w:t", NS) if t.text]
    link_info = " ".join(link_texts).strip()
    return (name, link_info)


def parse_docx_teachers(content: bytes) -> dict[str, TeacherData]:
    """
    Распаковывает docx-архив в памяти и парсит таблицу контактов преподавателей.

    Использует безопасный defusedxml во избежание XML-уязвимостей (Billion Laughs),
    индексируя преподавателей по нижнему регистру фамилии для быстрого поиска.

    Возвращает словарь {фамилия_lowercased: TeacherData}.
    """
    teachers_map: dict[str, TeacherData] = {}
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            xml_data = z.read("word/document.xml")
        root = ET.fromstring(xml_data)
        for row in root.findall(".//w:tr", NS):
            name, link_info = extract_row_texts(row)
            if name:
                teachers_map[name.split()[0].lower()] = {"full_name": name, "link_info": link_info}
        log.info("Успешно распаршено %s преподавателей из docx", len(teachers_map))
    except Exception as e:
        log.error("Ошибка парсинга docx XML: %s", e)
    return teachers_map


def _get_docx_lock() -> asyncio.Lock:
    """
    Предоставляет лениво созданный мьютекс asyncio.Lock для синхронизации запросов.

    Обеспечивает привязку замка к текущему активному event loop в многопоточном окружении.

    Возвращает активный экземпляр asyncio.Lock.
    """
    global _DOCX_LOCK
    if _DOCX_LOCK is None:
        _DOCX_LOCK = asyncio.Lock()
    return _DOCX_LOCK


def _is_cache_fresh(now: float, force_refresh: bool) -> bool:
    """
    Проверяет валидность локального кэша преподавателей с защитой от спама.

    Принудительное обновление ограничивается лимитом DOCX_MIN_REFRESH_INTERVAL_SECONDS,
    защищая Яндекс Диск от rate limiting при частых кликах пользователей.

    Возвращает True, если кэш актуален, иначе False.
    """
    if not _CACHE[1]:
        return False
    age = now - _CACHE[0]
    if not force_refresh:
        return age < DOCX_CACHE_TTL_SECONDS
    return age < DOCX_MIN_REFRESH_INTERVAL_SECONDS


async def _fetch_and_cache_teachers(now: float) -> dict[str, TeacherData]:
    """
    Загружает документ с диска, парсит преподавателей и сливает с кастомным списком.

    Выносит тяжелый парсинг XML в фоновый пул потоков (asyncio.to_thread)
    для предотвращения блокировки основного цикла событий бота.

    Возвращает объединенный словарь актуальных контактов преподавателей.
    """
    global _CACHE
    from services.custom_teachers import load_custom_teachers

    log.info("Загрузка свежих данных с Яндекс Диска...")
    content = await fetch_docx_bytes()
    parsed = (await asyncio.to_thread(parse_docx_teachers, content)) if content else _CACHE[1].copy()
    custom = load_custom_teachers()
    parsed.update(custom)
    _CACHE = (now, parsed)
    return parsed


async def get_teacher_links(force_refresh: bool = False) -> dict[str, TeacherData]:
    """
    Предоставляет реестр контактов преподавателей с Singleflight-блокировкой.

    Объединяет параллельные запросы к одному вызову сетевого скачивания,
    исключая 'thundering herd' проблему при одновременном обращении студентов.

    Возвращает актуальный словарь преподавателей и их ссылок.
    """
    now = time.time()
    if _is_cache_fresh(now, force_refresh):
        return _CACHE[1]
    async with _get_docx_lock():
        now = time.time()
        if _is_cache_fresh(now, force_refresh):
            return _CACHE[1]
        return await _fetch_and_cache_teachers(now)
