"""
Сервис интеграции с Яндекс Документами через протокол WOPI.

Обеспечивает чтение и запись посещаемости в таблицу .xlsx на Яндекс Диске.
Поскольку прямая публичная веб-ссылка docs.yandex.ru защищена капчей,
сессионный токен доступа WOPI извлекается через headless Chromium.
Запись в файл выполняется по стандарту WOPI (HTTP POST с X-WOPI-Override: PUT)
с соблюдением активной блокировки X-WOPI-Lock.
"""

import asyncio
import io
import json
import re
import zipfile
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
import httpx
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from config import ATTENDANCE_DOC_URL
from core.logger import get_logger

log = get_logger("yandex_docs")

# Соответствие порядкового номера месяца короткому имени вкладки
MONTH_SHEET_MAP: Dict[int, str] = {
    1: "ЯНВ", 2: "ФЕВР", 3: "МАРТ", 4: "АПР", 5: "МАЙ", 6: "ИЮН",
    7: "ИЮЛ", 8: "АВГ", 9: "СЕНТ", 10: "ОКТ", 11: "НОЯБ", 12: "ДЕК"
}


class WopiSession:
    """Сессия авторизованного доступа к документу по протоколу WOPI."""

    def __init__(self, resource_url: str, access_token: str, lock_id: str):
        # resource_url — базовый URL документа в WOPI сервисе Яндекса
        # access_token — временный токен с правами на запись (UserCanWrite=True)
        # lock_id — идентификатор активной сессионной блокировки редактора
        self.resource_url = resource_url
        self.access_token = access_token
        self.lock_id = lock_id


def extract_client_config(html_content: str) -> Dict:
    """
    Извлекает JSON конфигурации редактора из HTML страницы.

    На странице docs.yandex.ru параметры сессии зашиты в тег
    <script id="client-config">.
    """
    match = re.search(r'<script[^>]*id="client-config"[^>]*>(.*?)</script>', html_content)
    if not match:
        raise ValueError("Тег client-config не найден в DOM Яндекс Документов")
    return json.loads(match.group(1))


def get_yandex_cookie_header() -> str:
    """Формирует строку заголовка Cookie для авторизованного доступа к Яндекс Документам."""
    from config import YANDEX_COOKIE, YANDEX_SESSION_ID
    if YANDEX_COOKIE:
        return YANDEX_COOKIE.strip()
    if YANDEX_SESSION_ID:
        return f"Session_id={YANDEX_SESSION_ID.strip()}"
    return ""


async def fetch_page_dom(doc_url: str) -> str:
    """
    Загружает HTML страницы редактора через HTTP с авторизационной сессией.

    Используем прямой HTTP-запрос с Cookie вместо тяжелого Chromium,
    что исключает смарт-капчу и обеспечивает мгновенный ответ за 0.1 сек.
    """
    cookie_hdr = get_yandex_cookie_header()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
    }
    if cookie_hdr:
        headers["Cookie"] = cookie_hdr
    else:
        log.warning("YANDEX_SESSION_ID не задан в .env — возможна смарт-капча Яндекса")
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        res = await client.get(doc_url, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(f"Ошибка загрузки страницы документа: HTTP {res.status_code}")
        return res.text


async def get_active_wopi_lock(resource_url: str, token: str) -> str:
    """
    Определяет активный идентификатор блокировки файла.

    Отправляет пустой PUT-запрос, чтобы сервер вернул 409 с заголовком x-wopi-lock.
    """
    url = f"{resource_url}/contents?access_token={token}"
    headers = {"X-WOPI-Override": "PUT", "Content-Type": "application/octet-stream"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(url, headers=headers, content=b"")
        lock = res.headers.get("x-wopi-lock", "volga:prod-35")
        log.debug(f"Получен активный WOPI lock: {lock}")
        return lock


async def init_wopi_session(doc_url: str = ATTENDANCE_DOC_URL) -> WopiSession:
    """
    Инициализирует WOPI-сессию для чтения и сохранения таблицы.

    Возвращает объект WopiSession с валидным токеном и блокировкой.
    """
    log.debug("Инициализация WOPI сессии через Chromium...")
    html = await fetch_page_dom(doc_url)
    config = extract_client_config(html)
    action_data = config.get("officeActionData", {})
    res_url = action_data.get("resource_url")
    token = action_data.get("access_token")
    if not res_url or not token:
        raise RuntimeError("Не удалось извлечь resource_url или access_token")
    lock_id = await get_active_wopi_lock(res_url, token)
    log.info("WOPI-сессия успешно инициализирована")
    return WopiSession(res_url, token, lock_id)


def load_workbook_from_bytes(content: bytes) -> openpyxl.Workbook:
    """Синхронно парсит байты книги openpyxl в отдельном потоке без логов предупреждений."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return openpyxl.load_workbook(io.BytesIO(content))


def compute_sheet_summary_counts(sheet: Worksheet) -> Dict[Tuple[str, int], int]:
    """Подсчитывает количество отметок О, У, Н для каждой строки студента."""
    mc = sheet.max_column
    if mc < 4:
        return {}
    c_o, c_u, c_n = mc - 2, mc - 1, mc
    l_o = openpyxl.utils.get_column_letter(c_o)
    l_u = openpyxl.utils.get_column_letter(c_u)
    l_n = openpyxl.utils.get_column_letter(c_n)
    counts = {}
    for r in range(5, 37):
        row_vals = [sheet.cell(r, c).value for c in range(3, mc - 2)]
        counts[(l_o, r)] = sum(1 for v in row_vals if v == "О")
        counts[(l_u, r)] = sum(1 for v in row_vals if v == "У")
        counts[(l_n, r)] = sum(1 for v in row_vals if v == "Н")
    return counts


def patch_sheet_xml_counts(xml_text: str, counts: Dict[Tuple[str, int], int]) -> str:
    """Заменяет пустые значения <v></v> на вычисленные количества в XML листа."""
    def repl(m):
        col, r = m.group(1), int(m.group(2))
        if (col, r) not in counts:
            return m.group(0)
        count = counts[(col, r)]
        tag = m.group(0)
        if re.search(r"<(?:\w+:)?v>", tag):
            return re.sub(r"(<(?:\w+:)?v>)[^<]*(</(?:\w+:)?v>)", rf"\g<1>{count}\g<2>", tag)
        return re.sub(r"</(?:\w+:)?c>", f"<v>{count}</v></c>", tag)

    pattern = (
        r"<(?:\w+:)?c\s+r=\"([A-Z]+)(\d+)\"[^>]*>"
        r"<(?:\w+:)?f[^>]*>[^<]+</(?:\w+:)?f>"
        r"(?:<(?:\w+:)?v>[^<]*</(?:\w+:)?v>)?"
        r"</(?:\w+:)?c>"
    )
    return re.sub(pattern, repl, xml_text)


def ensure_all_summary_headers(wb: openpyxl.Workbook) -> None:
    """Гарантирует текстовые заголовки и коды О, У, Н во всех листах месяцев."""
    for name in wb.sheetnames:
        if name in MONTH_SHEET_MAP.values():
            sheet = wb[name]
            mc = sheet.max_column
            if mc >= 4:
                sheet.cell(2, mc - 2, "Опоздавшие")
                sheet.cell(3, mc - 2, "О")
                sheet.cell(2, mc - 1, "отсутствие по уважительной причине")
                sheet.cell(3, mc - 1, "У")
                sheet.cell(2, mc, "отсутствие по неуважительной причине")
                sheet.cell(3, mc, "Н")


def inject_summary_cache(raw_bytes: bytes, wb: openpyxl.Workbook) -> bytes:
    """Инжектирует кэшированные значения формул COUNTIF в zip-архив xlsx."""
    sheet_map = {f"xl/worksheets/sheet{i+1}.xml": name for i, name in enumerate(wb.sheetnames)}
    in_zip = zipfile.ZipFile(io.BytesIO(raw_bytes))
    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out_zip:
        for item in in_zip.infolist():
            content = in_zip.read(item.filename)
            sh_name = sheet_map.get(item.filename)
            if sh_name and sh_name in MONTH_SHEET_MAP.values():
                counts = compute_sheet_summary_counts(wb[sh_name])
                content = patch_sheet_xml_counts(content.decode("utf-8"), counts).encode("utf-8")
            out_zip.writestr(item, content)
    return out_buf.getvalue()


def save_workbook_to_bytes(wb: openpyxl.Workbook) -> bytes:
    """Синхронно сохраняет книгу openpyxl в байты с инжекцией кэша формул."""
    ensure_all_summary_headers(wb)
    buf = io.BytesIO()
    wb.save(buf)
    return inject_summary_cache(buf.getvalue(), wb)


async def download_workbook(session: WopiSession) -> openpyxl.Workbook:
    """
    Скачивает бинарный контент таблицы и загружает в openpyxl.

    Возвращает объект книги Excel с сохранением валидаций данных.
    """
    url = f"{session.resource_url}/contents?access_token={session.access_token}"
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        res = await client.get(url)
        if res.status_code != 200:
            raise RuntimeError(f"Ошибка скачивания таблицы: HTTP {res.status_code}")
        wb = await asyncio.to_thread(load_workbook_from_bytes, res.content)
        log.info(f"Таблица успешно скачана ({len(res.content)} байт)")
        return wb


async def upload_workbook(session: WopiSession, wb: openpyxl.Workbook) -> bool:
    """
    Сохраняет книгу openpyxl и выгружает байты на сервер по WOPI.

    Возвращает True в случае успешного сохранения (HTTP 200).
    """
    data = await asyncio.to_thread(save_workbook_to_bytes, wb)
    url = f"{session.resource_url}/contents?access_token={session.access_token}"
    headers = {
        "X-WOPI-Override": "PUT",
        "Content-Type": "application/octet-stream",
        "X-WOPI-Lock": session.lock_id
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(url, headers=headers, content=data)
        if res.status_code == 200:
            log.info(f"✅ Таблица успешно сохранена в Яндекс Документах ({len(data)} байт)")
            return True
        log.error(f"❌ Ошибка загрузки таблицы: HTTP {res.status_code} {res.text}")
        return False


def get_month_sheet(wb: openpyxl.Workbook, target_date: date) -> Worksheet:
    """
    Находит рабочий лист для указанной даты по номеру месяца.

    Выбрасывает ValueError, если вкладка отсутствует в таблице.
    """
    sheet_name = MONTH_SHEET_MAP.get(target_date.month)
    if not sheet_name or sheet_name not in wb.sheetnames:
        raise ValueError(f"Вкладка '{sheet_name}' для месяца {target_date.month} не найдена")
    return wb[sheet_name]


def parse_date_cell(cell_value: object) -> Optional[str]:
    """Приводит значение ячейки даты к строковому формату ДД.ММ."""
    if isinstance(cell_value, (datetime, date)):
        return cell_value.strftime("%d.%m")
    if cell_value:
        return str(cell_value).strip()
    return None


def find_date_column_start(sheet: Worksheet, target_date: date) -> Optional[int]:
    """
    Ищет начальную колонку даты во 2-й строке таблицы.

    Возвращает 1-based индекс первой колонки дня или None.
    """
    target_str = target_date.strftime("%d.%m")
    for col in range(1, sheet.max_column + 1):
        parsed = parse_date_cell(sheet.cell(2, col).value)
        if parsed and target_str in parsed:
            log.debug(f"Найдена дата {target_str} в колонке {col}")
            return col
    return None


def find_lesson_column(sheet: Worksheet, target_date: date, lesson_num: int) -> Optional[int]:
    """
    Определяет точную колонку для указанной даты и номера пары.

    Ищет дату во 2-й строке, затем номер пары (1-6) в 4-й строке.
    """
    start_col = find_date_column_start(sheet, target_date)
    if not start_col:
        return None
    # Пары дня расположены в блоке до 6 колонок
    for offset in range(6):
        col = start_col + offset
        pair_val = sheet.cell(4, col).value
        if pair_val == lesson_num or str(pair_val) == str(lesson_num):
            log.debug(f"Найдена пара {lesson_num} в колонке {col}")
            return col
    return None


def normalize_fio(name: str) -> str:
    """Очищает строку ФИО от неразрывных пробелов и лишних знаков."""
    return name.replace("\xa0", " ").strip()


def get_students_list(sheet: Worksheet) -> List[Tuple[int, str]]:
    """
    Извлекает список студентов из колонки B, начиная с 5-й строки.

    Возвращает список кортежей (номер_строки, ФИО).
    """
    students: List[Tuple[int, str]] = []
    for row in range(5, sheet.max_row + 1):
        val = sheet.cell(row, 2).value
        if not val:
            continue
        cleaned = normalize_fio(str(val))
        if cleaned:
            students.append((row, cleaned))
    return students


def find_student_row(sheet: Worksheet, student_name: str) -> Optional[int]:
    """
    Находит номер строки студента в колонке B по ФИО.

    Использует частичное совпадение фамилии и имени для надёжности.
    """
    target = normalize_fio(student_name).lower()
    for row, name in get_students_list(sheet):
        if target in name.lower() or name.lower() in target:
            return row
    return None


def write_student_mark(
    sheet: Worksheet,
    row: int,
    col: int,
    mark: str
) -> None:
    """
    Записывает символ посещаемости (П, О, У, Н) в ячейку таблицы.

    Проверяет валидность символа перед записью.
    """
    valid_marks = {"П", "О", "У", "Н", ""}
    clean_mark = mark.strip().upper()
    if clean_mark not in valid_marks:
        raise ValueError(f"Недопустимая отметка посещаемости: {mark}")
    cell = sheet.cell(row, col)
    cell.value = clean_mark if clean_mark else None
    log.debug(f"Записана отметка '{clean_mark}' в ячейку R{row}C{col}")
