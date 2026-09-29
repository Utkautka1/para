"""
Модуль модульных тестов для подсистемы отметки посещаемости.

Проверяет:
  - Парсинг и манипуляцию ячейками Excel (yandex_docs)
  - Выбор листа месяца, поиск колонок дат и пар
  - Сессии и подсчет статистики посещаемости (attendance_manager)
  - Генерацию клавиатур и форматирование текстов (attendance templates)
  - Фильтрацию прав доступа (AttendanceAuthFilter)
"""

from datetime import date, datetime
import openpyxl
import pytest
from unittest.mock import MagicMock

from bot.filters.auth import AttendanceAuthFilter
from bot.templates.admin.attendance import (
    format_confirm_text, format_student_card, format_summary_text,
    get_lesson_confirm_kb, get_lesson_select_kb, get_student_poll_kb
)
from config import ALLOWED_USER_ID, DEPUTY_USER_ID
from services.attendance_manager import (
    AttendanceSession, apply_marks_to_sheet, calculate_summary_stats
)
from services.models import Lesson
from services.yandex_docs import (
    extract_client_config, find_date_column_start, find_lesson_column,
    find_student_row, get_month_sheet, get_students_list, normalize_fio,
    parse_date_cell, write_student_mark
)


def create_mock_workbook() -> openpyxl.Workbook:
    """Создает тестовую книгу openpyxl со структурой таблицы посещаемости."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "СЕНТ"
    ws.cell(2, 3, datetime(2026, 9, 29, 0, 0))
    for p in range(1, 7):
        ws.cell(4, 2 + p, p)
    ws.cell(5, 2, "\xa0Иванов Иван Иванович")
    ws.cell(6, 2, "Петров Петр Петрович")
    ws.cell(7, 2, "Сидоров Сидор Сидорович")
    return wb


def test_extract_client_config_success():
    """Проверяет успешное извлечение JSON конфигурации из HTML."""
    html = '<html><script id="client-config">{"officeActionData": {"rights": ["write"]}}</script></html>'
    cfg = extract_client_config(html)
    assert cfg["officeActionData"]["rights"] == ["write"]


def test_extract_client_config_missing():
    """Проверяет выброс исключения при отсутствии тега client-config."""
    with pytest.raises(ValueError, match="не найден"):
        extract_client_config("<html><body>No config</body></html>")


def test_get_month_sheet():
    """Проверяет корректный выбор листа месяца по дате."""
    wb = openpyxl.Workbook()
    wb.create_sheet("СЕНТ")
    wb.create_sheet("ОКТ")
    s_sep = get_month_sheet(wb, date(2026, 9, 29))
    assert s_sep.title == "СЕНТ"
    s_oct = get_month_sheet(wb, date(2026, 10, 5))
    assert s_oct.title == "ОКТ"


def test_get_month_sheet_not_found():
    """Проверяет ошибку при отсутствии нужного месяца."""
    wb = openpyxl.Workbook()
    with pytest.raises(ValueError, match="не найдена"):
        get_month_sheet(wb, date(2026, 11, 1))


def test_parse_date_cell_variants():
    """Проверяет парсинг даты из различных типов значений ячейки."""
    assert parse_date_cell(datetime(2026, 9, 29)) == "29.09"
    assert parse_date_cell(date(2026, 9, 29)) == "29.09"
    assert parse_date_cell(" 29.09 ") == "29.09"
    assert parse_date_cell(None) is None


def test_find_date_column_start():
    """Проверяет поиск начальной колонки дня во 2-й строке."""
    wb = create_mock_workbook()
    sheet = wb["СЕНТ"]
    col = find_date_column_start(sheet, date(2026, 9, 29))
    assert col == 3


def test_find_lesson_column():
    """Проверяет точное определение колонки пары."""
    wb = create_mock_workbook()
    sheet = wb["СЕНТ"]
    assert find_lesson_column(sheet, date(2026, 9, 29), 1) == 3
    assert find_lesson_column(sheet, date(2026, 9, 29), 2) == 4
    assert find_lesson_column(sheet, date(2026, 9, 29), 6) == 8
    assert find_lesson_column(sheet, date(2026, 9, 29), 7) is None


def test_normalize_fio():
    """Проверяет удаление неразрывных пробелов из ФИО."""
    assert normalize_fio("\xa0Иванов   Иван\xa0") == "Иванов   Иван"


def test_get_students_list():
    """Проверяет извлечение списка студентов со строки 5."""
    wb = create_mock_workbook()
    sheet = wb["СЕНТ"]
    students = get_students_list(sheet)
    assert len(students) == 3
    assert students[0] == (5, "Иванов Иван Иванович")
    assert students[1] == (6, "Петров Петр Петрович")


def test_find_student_row():
    """Проверяет поиск строки студента по части ФИО."""
    wb = create_mock_workbook()
    sheet = wb["СЕНТ"]
    assert find_student_row(sheet, "Иванов Иван") == 5
    assert find_student_row(sheet, "Петров") == 6
    assert find_student_row(sheet, "Неизвестный") is None


def test_write_student_mark():
    """Проверяет запись допустимых и запрет недопустимых отметок."""
    wb = create_mock_workbook()
    sheet = wb["СЕНТ"]
    write_student_mark(sheet, 5, 3, "П")
    assert sheet.cell(5, 3).value == "П"
    write_student_mark(sheet, 5, 3, "")
    assert sheet.cell(5, 3).value is None
    with pytest.raises(ValueError, match="Недопустимая"):
        write_student_mark(sheet, 5, 3, "Х")


def test_calculate_summary_stats():
    """Проверяет подсчет сводных данных посещаемости."""
    marks = {"5": "П", "6": "О", "7": "Н", "8": "П", "9": "У"}
    stats = calculate_summary_stats(marks)
    assert stats["П"] == 2
    assert stats["О"] == 1
    assert stats["У"] == 1
    assert stats["Н"] == 1


def test_apply_marks_to_sheet():
    """Проверяет пакетное применение отметок к таблице."""
    wb = create_mock_workbook()
    sheet = wb["СЕНТ"]
    session = AttendanceSession(
        target_date="2026-09-29",
        lesson_num=1,
        lesson_title="Тест",
        students=[(5, "Иванов"), (6, "Петров")],
        marks={"5": "П", "6": "Н"},
        initiator_id=123
    )
    apply_marks_to_sheet(sheet, session, col=3)
    assert sheet.cell(5, 3).value == "П"
    assert sheet.cell(6, 3).value == "Н"


def test_get_lesson_confirm_kb():
    """Проверяет кнопки подтверждения проведения пары."""
    kb = get_lesson_confirm_kb(2)
    assert len(kb.inline_keyboard) == 1
    assert len(kb.inline_keyboard[0]) == 2
    assert kb.inline_keyboard[0][0].callback_data == "att:start:2"
    assert kb.inline_keyboard[0][1].callback_data == "att:cancel:2"


def test_get_student_poll_kb():
    """Проверяет состав инлайн-кнопок опроса студента."""
    kb_no_back = get_student_poll_kb(can_back=False)
    # 3 ряда кнопок (П/О, У/Н, Все остальные П, Отменить)
    assert len(kb_no_back.inline_keyboard) == 4
    assert kb_no_back.inline_keyboard[0][0].callback_data == "att:mark:П"
    assert kb_no_back.inline_keyboard[0][1].callback_data == "att:mark:О"
    assert kb_no_back.inline_keyboard[1][0].callback_data == "att:mark:У"
    assert kb_no_back.inline_keyboard[1][1].callback_data == "att:mark:Н"
    assert kb_no_back.inline_keyboard[2][0].callback_data == "att:all_p"
    assert kb_no_back.inline_keyboard[3][0].callback_data == "att:abort"

    kb_back = get_student_poll_kb(can_back=True)
    assert kb_back.inline_keyboard[3][0].callback_data == "att:back"


def test_format_confirm_text():
    """Проверяет форматирование текста запроса пары."""
    text = format_confirm_text(1, "Математика", "Иванов И.И.")
    assert "Пара 1" in text
    assert "Математика" in text
    assert "Иванов И.И." in text


def test_format_student_card():
    """Проверяет текст карточки студента с прогрессом."""
    session = AttendanceSession(
        target_date="2026-09-29",
        lesson_num=1,
        lesson_title="Математика",
        students=[(5, "Иванов Иван"), (6, "Петров Петр")],
        initiator_id=123
    )
    text = format_student_card(session)
    assert "[1/2]" in text
    assert "Иванов Иван" in text


def test_format_summary_text():
    """Проверяет форматирование итогового отчета посещаемости."""
    session = AttendanceSession(
        target_date="2026-09-29",
        lesson_num=2,
        lesson_title="Физика",
        students=[(5, "Иванов Иван"), (6, "Петров Петр")],
        marks={"5": "П", "6": "Н"},
        initiator_id=123
    )
    stats = {"П": 1, "О": 0, "У": 0, "Н": 1}
    summary = format_summary_text(session, stats)
    assert "пару 2" in summary
    assert "Присутствуют (П): <b>1</b>" in summary
    assert "Петров П. (Н)" in summary


def test_get_lesson_select_kb():
    """Проверяет список пар для ручного выбора /attendance."""
    mock_l1 = MagicMock(number=1, subject="Информатика")
    mock_l2 = MagicMock(number=2, subject="История")
    kb = get_lesson_select_kb([mock_l1, mock_l2])
    assert len(kb.inline_keyboard) == 3
    assert kb.inline_keyboard[0][0].callback_data == "att:start:1"
    assert kb.inline_keyboard[1][0].callback_data == "att:start:2"


@pytest.mark.asyncio
async def test_attendance_auth_filter():
    """Проверяет доступ для старосты, замстаросты и отказ остальным."""
    filter_ = AttendanceAuthFilter()
    user_admin = MagicMock(id=ALLOWED_USER_ID)
    msg_admin = MagicMock(from_user=user_admin)
    assert await filter_(msg_admin) is True

    user_deputy = MagicMock(id=DEPUTY_USER_ID)
    msg_deputy = MagicMock(from_user=user_deputy)
    assert await filter_(msg_deputy) is True

    user_stranger = MagicMock(id=999999999)
    msg_stranger = MagicMock(from_user=user_stranger)
    assert await filter_(msg_stranger) is False
