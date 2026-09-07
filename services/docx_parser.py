"""
Модуль загрузки и парсинга контактов преподавателей с Yandex Disk.

Скачивает файл .docx с Yandex Disk через публичный REST API Яндекс Диска,
извлекает из таблицы ФИО преподавателей и их персональные Zoom/Телемост ссылки.
"""

import io
import time
import xml.etree.ElementTree as ET
import zipfile
from typing import Dict, Optional, Tuple, TypedDict
import httpx

from config import DOCX_CACHE_TTL_SECONDS, YANDEX_DOC_PUBLIC_URL
from core.logger import get_logger

log = get_logger("docx_parser")

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


class TeacherData(TypedDict):
    """Тип данных элемента преподавателя."""
    full_name: str
    link_info: str


# Кэш данных: (timestamp, dict_teachers)
_CACHE: Tuple[float, Dict[str, TeacherData]] = (0.0, {})


async def fetch_docx_bytes() -> Optional[bytes]:
    """
    Загружает сырые байты docx файла с Yandex Disk через публичный API.

    :return: Байты файла docx или None при ошибке
    """
    api_url = f"https://cloud-api.yandex.net/v1/disk/public/resources?public_key={YANDEX_DOC_PUBLIC_URL}"
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            res = await client.get(api_url)
            if res.status_code != 200:
                log.error(f"Ошибка API Яндекс Диска: HTTP {res.status_code}")
                return None
            file_url = res.json().get("file")
            if not file_url:
                log.error("API Яндекс Диска не вернул ссылку на скачивание")
                return None
            doc_res = await client.get(file_url)
            return doc_res.content
    except Exception as e:
        log.error(f"Исключение при скачивании файла с Яндекс Диска: {e}")
        return None


def extract_row_texts(row_elem: ET.Element) -> Tuple[str, str]:
    """
    Извлекает полное имя преподавателя и строку ссылок из таблицы docx.

    :param row_elem: XML элемент w:tr
    :return: Кортеж (ФИО, Ссылка_и_данные)
    """
    cells = row_elem.findall(".//w:tc", NS)
    if len(cells) < 3:
        return ("", "")
    name_texts = [t.text for t in cells[0].findall(".//w:t", NS) if t.text]
    name = " ".join(" ".join(name_texts).split()).strip()
    link_texts = [t.text for t in cells[2].findall(".//w:t", NS) if t.text]
    link_info = " ".join(link_texts).strip()
    return (name, link_info)


def parse_docx_teachers(content: bytes) -> Dict[str, TeacherData]:
    """
    Распаковывает docx и парсит таблицу контактов преподавателей.

    :param content: Байты docx файла
    :return: Словарь вида {фамилия: TeacherData}
    """
    teachers_map: Dict[str, TeacherData] = {}
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            xml_data = z.read("word/document.xml")
        root = ET.fromstring(xml_data)
        for row in root.findall(".//w:tr", NS):
            name, link_info = extract_row_texts(row)
            if name:
                last_name = name.split()[0].lower()
                teachers_map[last_name] = {
                    "full_name": name,
                    "link_info": link_info
                }
        log.info(f"Успешно распаршено {len(teachers_map)} преподавателей из docx")
    except Exception as e:
        log.error(f"Ошибка парсинга docx XML: {e}")
    return teachers_map


async def get_teacher_links(force_refresh: bool = False) -> Dict[str, TeacherData]:
    """
    Возвращает карту контактов преподавателей (Docx + Custom JSON).

    :param force_refresh: Принудительное обновление кэша
    :return: Словарь контактов преподавателей
    """
    global _CACHE
    now = time.time()
    if not force_refresh and (now - _CACHE[0] < DOCX_CACHE_TTL_SECONDS) and _CACHE[1]:
        return _CACHE[1]

    from services.custom_teachers import load_custom_teachers
    log.info("Загрузка свежих данных с Яндекс Диска...")
    content = await fetch_docx_bytes()
    parsed = parse_docx_teachers(content) if content else _CACHE[1].copy()
    custom = load_custom_teachers()
    # Сначала применяем данные из docx, затем перекрываем кастомными
    parsed.update(custom)
    _CACHE = (now, parsed)
    return parsed
