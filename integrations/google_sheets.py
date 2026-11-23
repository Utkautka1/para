"""
Сервис интеграции с Google Sheets и Google Drive API для журнала посещаемости.

Обеспечивает чтение, запись и выгрузку журнала посещаемости учебной группы:
  1. Авторизация через сервисный аккаунт Google Cloud (без истекающих пользовательских куки)
  2. Атомарное обновление отметок посещаемости пары через spreadsheets.values.batchUpdate
  3. Чтение списка студентов академической группы из колонки B месяца
  4. Экспорт книги посещаемости в формате .xlsx через Google Drive API v3 files.export
"""

import asyncio
import io
import json
import urllib.parse
from datetime import date, datetime
from typing import Any

import httpx
import openpyxl
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from openpyxl.worksheet.worksheet import Worksheet

from config import (
    GOOGLE_SERVICE_ACCOUNT_JSON,
    GOOGLE_SERVICE_ACCOUNT_PATH,
    GOOGLE_SHEET_ID,
)
from core.logger import get_logger

log = get_logger("google_sheets")

# Соответствие порядкового номера месяца короткому имени вкладки таблицы
MONTH_SHEET_MAP: dict[int, str] = {
    1: "ЯНВ",
    2: "ФЕВР",
    3: "МАРТ",
    4: "АПР",
    5: "МАЙ",
    6: "ИЮН",
    7: "ИЮЛ",
    8: "АВГ",
    9: "СЕНТ",
    10: "ОКТ",
    11: "НОЯБ",
    12: "ДЕК",
}

# Области доступа: редактирование таблиц и чтение файлов Drive для экспорта
SCOPES: list[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _load_credentials() -> Any:
    """
    Загружает учетные данные сервисного аккаунта Google из JSON-строки или файла.

    Приоритет отдается GOOGLE_SERVICE_ACCOUNT_JSON (для CI/CD), при отсутствии
    загружается локальный файл ключа по пути GOOGLE_SERVICE_ACCOUNT_PATH.

    Возвращает объект Credentials с правами на Sheets и Drive API.
    """
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        data = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        return Credentials.from_service_account_info(data, scopes=SCOPES)
    return Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_PATH, scopes=SCOPES)


def _fetch_token_sync() -> str:
    """
    Синхронно обновляет и возвращает OAuth токен Google API.

    Вызывается внутри asyncio.to_thread для изоляции блокирующего сетевого вызова.

    Возвращает строковый токен доступа.
    """
    creds = _load_credentials()
    creds.refresh(Request())
    return str(creds.token)


async def get_access_token() -> str:
    """
    Асинхронно получает валидный токен авторизации для Google API.

    Выполняет синхронный запрос к OAuth-серверу в отдельном потоке execution pool.

    Возвращает строковый токен Bearer.
    """
    return await asyncio.to_thread(_fetch_token_sync)


def col_to_letter(col: int) -> str:
    """
    Преобразует 1-based числовой индекс колонки в буквенное обозначение формата A1.

    Используется для построения диапазонов ячеек Google Таблицы (напр. 1 -> 'A', 27 -> 'AA').

    Возвращает буквенный код колонки.
    """
    result: list[str] = []
    while col > 0:
        col, rem = divmod(col - 1, 26)
        result.append(chr(65 + rem))
    return "".join(reversed(result))


def normalize_fio(name: str) -> str:
    """
    Очищает строковое ФИО от неразрывных пробелов и краевых символов.

    Обеспечивает консистентное сопоставление студентов независимо от формата пробелов.

    Возвращает нормализованную строку ФИО.
    """
    return name.replace("\xa0", " ").strip()


def get_month_sheet_name(target_date: date) -> str:
    """
    Возвращает название листа месяца по дате.

    Сопоставляет номер месяца по календарному словарю MONTH_SHEET_MAP.

    Возвращает строковое имя вкладки (напр. 'НОЯБ') или выбрасывает ValueError.
    """
    name = MONTH_SHEET_MAP.get(target_date.month)
    if not name:
        raise ValueError(f"Неизвестный месяц: {target_date.month}")
    return name


def get_month_sheet(wb: openpyxl.Workbook, target_date: date) -> Worksheet:
    """
    Возвращает рабочий лист книги openpyxl, соответствующий месяцу даты.

    Используется для совместимости с сервисами статистики и анализа посещаемости.

    Возвращает экземпляр Worksheet или выбрасывает ValueError.
    """
    name = get_month_sheet_name(target_date)
    if name not in wb.sheetnames:
        raise ValueError(f"Вкладка '{name}' не найдена в книге")
    return wb[name]


async def export_attendance_xlsx() -> bytes:
    """
    Экспортирует Google Таблицу посещаемости целиком в бинарный формат .xlsx.

    Использует Google Drive API v3 files.export с авторизацией сервисного аккаунта.

    Возвращает сырые байты файла книги Excel (.xlsx).
    """
    token = await get_access_token()
    url = f"https://www.googleapis.com/drive/v3/files/{GOOGLE_SHEET_ID}/export"
    params = {"mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.get(url, params=params, headers=headers)
        res.raise_for_status()
        log.info("Экспортирован журнал посещаемости (%s байт)", len(res.content))
        return res.content


async def download_workbook() -> openpyxl.Workbook:
    """
    Скачивает всю Google Таблицу и преобразует её в книгу openpyxl в памяти.

    Используется сервисом сквозной аналитики и отчётов посещаемости (attendance_stats).

    Возвращает объект openpyxl.Workbook с вычисленными значениями ячеек (data_only=True).
    """
    raw_xlsx = await export_attendance_xlsx()
    return await asyncio.to_thread(openpyxl.load_workbook, io.BytesIO(raw_xlsx), data_only=True)


async def fetch_students_from_google(target_date: date) -> list[tuple[int, str]]:
    """
    Считывает список студентов академической группы из колонки B месяца.

    Запрашивает диапазон B5:B35 через Google Sheets API без скачивания всего файла.

    Возвращает список пар [(индекс_строки, ФИО_студента)].
    """
    sheet_name = get_month_sheet_name(target_date)
    token = await get_access_token()
    range_param = urllib.parse.quote(f"'{sheet_name}'!B5:B35")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{range_param}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        res.raise_for_status()
        rows = res.json().get("values", [])
    students = [(5 + idx, normalize_fio(row[0])) for idx, row in enumerate(rows) if row and row[0].strip()]
    log.info("Загружено %s студентов из листа '%s'", len(students), sheet_name)
    return students


def find_lesson_column_in_grid(
    dates_row: list[str], pairs_row: list[str], target_date: date, lesson_num: int
) -> int | None:
    """
    Находит 1-based номер колонки пары по строкам дат и номеров пар из таблицы.

    Сопоставляет дату 'ДД.ММ' и номер пары (1..6) в блоке дня.

    Возвращает 1-based индекс колонки или None при отсутствии совпадения.
    """
    target_str = target_date.strftime("%d.%m")
    lesson_str = str(lesson_num)
    for idx, d_val in enumerate(dates_row):
        if target_str in str(d_val):
            for offset in range(6):
                col_idx = idx + offset
                if col_idx < len(pairs_row) and pairs_row[col_idx].strip() == lesson_str:
                    return col_idx + 1
    return None


def parse_date_cell(cell_value: object) -> str | None:
    """
    Приводит значение ячейки даты к стандартизированной строке 'ДД.ММ'.

    Поддерживает парсинг объектов datetime, date и строковых представлений.

    Возвращает строковую дату 'ДД.ММ' или None при пустом значении.
    """
    if isinstance(cell_value, (datetime, date)):
        return cell_value.strftime("%d.%m")
    if cell_value:
        return str(cell_value).strip()
    return None


def find_date_column_start(sheet: Worksheet, target_date: date) -> int | None:
    """
    Находит начальную колонку даты во второй строке листа openpyxl.

    Ищет подстроку 'ДД.ММ' в шапке календаря месяца для определения блока дня.

    Возвращает 1-based номер начальной колонки или None при отсутствии даты.
    """
    target_str = target_date.strftime("%d.%m")
    for col in range(1, getattr(sheet, "max_column", 170) + 1):
        parsed = parse_date_cell(sheet.cell(2, col).value)
        if parsed and target_str in parsed:
            return col
    return None


def get_students_list(sheet: Worksheet) -> list[tuple[int, str]]:
    """
    Извлекает список студентов группы из колонки B листа openpyxl.

    Считывает строки с 5 по max_row, очищая имена и исключая пустые ячейки.

    Возвращает список кортежей (номер_строки, нормализованное_ФИО).
    """
    students: list[tuple[int, str]] = []
    for row in range(5, getattr(sheet, "max_row", 50) + 1):
        val = sheet.cell(row, 2).value
        if not val:
            continue
        cleaned = normalize_fio(str(val))
        if cleaned:
            students.append((row, cleaned))
    return students


def find_student_row(sheet: Worksheet, student_name: str) -> int | None:
    """
    Находит номер строки студента в листе openpyxl по имени или фамилии.

    Применяет нечувствительное к регистру частичное совпадение подстрок.

    Возвращает номер строки в таблице (5-36) или None, если студент не найден.
    """
    target = normalize_fio(student_name).lower()
    for row, name in get_students_list(sheet):
        if target in name.lower() or name.lower() in target:
            return row
    return None


def find_lesson_column(sheet: Any, target_date: date, lesson_num: int) -> int | None:
    """
    Находит номер колонки пары в openpyxl листе или переданной структуре.

    Сканирует 2-ю строку в поисках даты 'ДД.ММ' и 4-ю строку в поисках номера пары.

    Возвращает 1-based номер колонки или None.
    """
    start_col = find_date_column_start(sheet, target_date)
    if not start_col:
        return None
    lesson_str = str(lesson_num)
    for offset in range(6):
        c = start_col + offset
        if str(sheet.cell(4, c).value or "").strip() == lesson_str:
            return c
    return None


def write_student_mark(sheet: Worksheet, row: int, col: int, mark: str) -> None:
    """
    Записывает отметку посещаемости в ячейку листа openpyxl.

    Проверяет валидность символа ('П', 'О', 'У', 'Н', '') перед записью.

    Ничего не возвращает; модифицирует ячейку in-place.
    """
    valid_marks = {"П", "О", "У", "Н", ""}
    clean_mark = mark.strip().upper()
    if clean_mark not in valid_marks:
        raise ValueError(f"Недопустимая отметка посещаемости: {mark}")
    cell = sheet.cell(row, col)
    cell.value = clean_mark if clean_mark else None


async def _fetch_header_grid(sheet_name: str, token: str) -> tuple[list[str], list[str]]:
    """
    Считывает строки дат (строка 2) и пар (строка 4) из Google Таблицы.

    Запрашивает срез A2:ZZ4 листа месяца для поиска колонок текущего дня.

    Возвращает кортеж из двух списков значений (строка дат, строка пар).
    """
    range_enc = urllib.parse.quote(f"'{sheet_name}'!A2:ZZ4")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/{range_enc}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        res.raise_for_status()
        values = res.json().get("values", [])
    dates = values[0] if len(values) > 0 else []
    pairs = values[2] if len(values) > 2 else []
    return dates, pairs


def _build_batch_data(sheet_name: str, col_letter: str, marks: dict[str, str]) -> list[dict[str, Any]]:
    """
    Формирует массив обновлений ячеек для Google Sheets API batchUpdate.

    Каждому студенту сопоставляется координата ячейки A1 и нормализованная отметка.

    Возвращает список словарей формата ValueRange для Google Sheets API.
    """
    return [
        {
            "range": f"'{sheet_name}'!{col_letter}{row_idx}",
            "values": [[mark.strip().upper()]],
        }
        for row_idx, mark in marks.items()
    ]


async def _send_batch_update(token: str, payload: dict[str, Any]) -> None:
    """
    Отправляет POST-запрос пакетного обновления batchUpdate в Google Sheets API.

    Выбрасывает HTTPStatusError при ошибке сетевого запроса или неверном ответе.
    """
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values:batchUpdate"
    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(url, json=payload, headers={"Authorization": f"Bearer {token}"})
        res.raise_for_status()


async def write_lesson_marks(target_date: date, lesson_num: int, marks: dict[str, str]) -> bool:
    """
    Атомарно записывает отметки посещаемости пары в Google Таблицу через batchUpdate.

    Находит колонку даты/пары и отправляет пакетное обновление.

    Возвращает True в случае успешной записи, иначе False.
    """
    try:
        sheet_name = get_month_sheet_name(target_date)
        token = await get_access_token()
        dates, pairs = await _fetch_header_grid(sheet_name, token)
        col = find_lesson_column_in_grid(dates, pairs, target_date, lesson_num)
        if not col:
            log.error("Колонка %s пара %s не найдена на %s", target_date, lesson_num, sheet_name)
            return False
        payload = {"valueInputOption": "USER_ENTERED", "data": _build_batch_data(sheet_name, col_to_letter(col), marks)}
        await _send_batch_update(token, payload)
        log.info("✅ Успешно записано %s отметок для пары %s (%s)", len(marks), lesson_num, target_date)
        return True
    except Exception as e:
        log.error("Ошибка пакетной записи отметок в Google Sheets: %s", e)
        return False
