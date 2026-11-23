"""
Тесты сервиса интеграции Google Sheets и Google Drive API (integrations/google_sheets.py).

Проверяет:
  1. Алгоритмы трансляции номеров колонок в координаты A1 (col_to_letter)
  2. Нормализацию строковых ФИО и очистку неразрывных пробелов
  3. Сопоставление календарных месяцев и рабочих листов
  4. Формирование пакетных запросов batchUpdate для Google Sheets API
  5. Поиск колонок пар в 2D-сетках и книгах openpyxl
  6. Экспорт и скачивание книг .xlsx через Google Drive API
"""

import io
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import openpyxl
import pytest

from integrations.google_sheets import (
    _build_batch_data,
    col_to_letter,
    download_workbook,
    export_attendance_xlsx,
    fetch_students_from_google,
    find_date_column_start,
    find_lesson_column,
    find_lesson_column_in_grid,
    find_student_row,
    get_month_sheet,
    get_month_sheet_name,
    get_students_list,
    normalize_fio,
    parse_date_cell,
    write_lesson_marks,
    write_student_mark,
)


def _create_mock_sheet() -> openpyxl.worksheet.worksheet.Worksheet:
    """Создает тестовый рабочий лист openpyxl со структурой журнала посещаемости."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "НОЯБ"
    ws.cell(2, 3, datetime(2026, 11, 23, 0, 0))
    for p in range(1, 7):
        ws.cell(4, 2 + p, p)
    ws.cell(5, 2, "\xa0Иванов Иван Иванович")
    ws.cell(6, 2, "Петров Петр Петрович")
    ws.cell(7, 2, "Сидоров Сидор Сидорович")
    return ws


def test_col_to_letter() -> None:
    """Проверяет корректность генерации буквенных кодов столбцов A1."""
    assert col_to_letter(1) == "A"
    assert col_to_letter(2) == "B"
    assert col_to_letter(26) == "Z"
    assert col_to_letter(27) == "AA"
    assert col_to_letter(28) == "AB"
    assert col_to_letter(52) == "AZ"
    assert col_to_letter(53) == "BA"


def test_normalize_fio() -> None:
    """Проверяет очистку ФИО от неразрывных пробелов и краевых пробельных символов."""
    assert normalize_fio("\xa0Иванов Иван\xa0") == "Иванов Иван"
    assert normalize_fio("  Петров   ") == "Петров"
    assert normalize_fio("Сидоров\xa0Сидор") == "Сидоров Сидор"


def test_get_month_sheet_name() -> None:
    """Проверяет соответствие номера месяца короткому имени вкладки."""
    assert get_month_sheet_name(date(2026, 9, 1)) == "СЕНТ"
    assert get_month_sheet_name(date(2026, 10, 15)) == "ОКТ"
    assert get_month_sheet_name(date(2026, 11, 23)) == "НОЯБ"
    assert get_month_sheet_name(date(2026, 12, 31)) == "ДЕК"
    with pytest.raises(ValueError, match="Неизвестный месяц"):

        class FakeDate:
            month = 13

        get_month_sheet_name(FakeDate())  # type: ignore[arg-type]


def test_get_month_sheet() -> None:
    """Проверяет получение вкладки из openpyxl книги по дате."""
    wb = openpyxl.Workbook()
    wb.create_sheet("НОЯБ")
    ws = get_month_sheet(wb, date(2026, 11, 23))
    assert ws.title == "НОЯБ"
    with pytest.raises(ValueError, match="не найдена"):
        get_month_sheet(wb, date(2026, 1, 1))


def test_parse_date_cell() -> None:
    """Проверяет парсинг ячеек с датами различного типа."""
    assert parse_date_cell(datetime(2026, 11, 23, 10, 30)) == "23.11"
    assert parse_date_cell(date(2026, 9, 2)) == "02.09"
    assert parse_date_cell(" 05.10 ") == "05.10"
    assert parse_date_cell(None) is None


def test_find_date_column_start() -> None:
    """Проверяет нахождение начальной колонки блока пар в строке 2."""
    ws = _create_mock_sheet()
    assert find_date_column_start(ws, date(2026, 11, 23)) == 3
    assert find_date_column_start(ws, date(2026, 11, 24)) is None


def test_get_students_list_and_find_row() -> None:
    """Проверяет извлечение списка студентов и поиск по частичному имени."""
    ws = _create_mock_sheet()
    students = get_students_list(ws)
    assert len(students) == 3
    assert students[0] == (5, "Иванов Иван Иванович")
    assert find_student_row(ws, "петров") == 6
    assert find_student_row(ws, "Неизвестный") is None


def test_find_lesson_column() -> None:
    """Проверяет точное определение колонки учебной пары в openpyxl листе."""
    ws = _create_mock_sheet()
    assert find_lesson_column(ws, date(2026, 11, 23), 1) == 3
    assert find_lesson_column(ws, date(2026, 11, 23), 2) == 4
    assert find_lesson_column(ws, date(2026, 11, 23), 7) is None


def test_find_lesson_column_in_grid() -> None:
    """Проверяет поиск колонки пары в строках Google Sheets API."""
    dates = ["", "1-КПД-3", "23.11", "", "", "", "", ""]
    pairs = ["", "", "1", "2", "3", "4", "5", "6"]
    col = find_lesson_column_in_grid(dates, pairs, date(2026, 11, 23), 1)
    assert col == 3
    assert find_lesson_column_in_grid(dates, pairs, date(2026, 11, 23), 8) is None


def test_write_student_mark() -> None:
    """Проверяет запись и валидацию отметок посещаемости."""
    ws = _create_mock_sheet()
    write_student_mark(ws, 5, 3, "П")
    assert ws.cell(5, 3).value == "П"
    write_student_mark(ws, 6, 3, "")
    assert ws.cell(6, 3).value is None
    with pytest.raises(ValueError, match="Недопустимая отметка"):
        write_student_mark(ws, 7, 3, "INVALID")


def test_build_batch_data() -> None:
    """Проверяет структуру объектов для spreadsheets.values.batchUpdate."""
    marks = {"5": "П", "6": "О"}
    data = _build_batch_data("НОЯБ", "C", marks)
    assert len(data) == 2
    assert data[0] == {"range": "'НОЯБ'!C5", "values": [["П"]]}
    assert data[1] == {"range": "'НОЯБ'!C6", "values": [["О"]]}


@pytest.mark.asyncio
async def test_fetch_students_from_google() -> None:
    """Проверяет чтение списка студентов через mock HTTP API."""
    mock_res = MagicMock()
    mock_res.json.return_value = {"values": [["\xa0Иванов И.И."], ["Петров П.П."], [""]]}
    mock_res.raise_for_status = MagicMock()

    with (
        patch("integrations.google_sheets.get_access_token", new_callable=AsyncMock, return_value="token"),
        patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_res),
    ):
        students = await fetch_students_from_google(date(2026, 11, 23))
        assert len(students) == 2
        assert students[0] == (5, "Иванов И.И.")
        assert students[1] == (6, "Петров П.П.")


@pytest.mark.asyncio
async def test_write_lesson_marks() -> None:
    """Проверяет процедуру пакетной записи отметок в Google Sheets."""
    with (
        patch("integrations.google_sheets.get_access_token", new_callable=AsyncMock, return_value="token"),
        patch(
            "integrations.google_sheets._fetch_header_grid",
            new_callable=AsyncMock,
            return_value=(["", "1-КПД-3", "23.11"], ["", "", "1"]),
        ),
        patch("integrations.google_sheets._send_batch_update", new_callable=AsyncMock) as mock_send,
    ):
        ok = await write_lesson_marks(date(2026, 11, 23), 1, {"5": "П"})
        assert ok is True
        mock_send.assert_awaited_once()


@pytest.mark.asyncio
async def test_export_and_download_workbook() -> None:
    """Проверяет экспорт .xlsx байтов и их загрузку в openpyxl Workbook."""
    ws = _create_mock_sheet()
    bio = io.BytesIO()
    ws.parent.save(bio)
    xlsx_bytes = bio.getvalue()

    mock_res = MagicMock()
    mock_res.content = xlsx_bytes
    mock_res.raise_for_status = MagicMock()

    with (
        patch("integrations.google_sheets.get_access_token", new_callable=AsyncMock, return_value="token"),
        patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_res),
    ):
        raw = await export_attendance_xlsx()
        assert raw == xlsx_bytes

        wb = await download_workbook()
        assert "НОЯБ" in wb.sheetnames
