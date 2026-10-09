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
from unittest.mock import AsyncMock, MagicMock, patch

import openpyxl
import pytest

from bot.filters.auth import AttendanceAuthFilter
from bot.templates.admin.attendance import (
    format_confirm_text,
    format_student_card,
    format_summary_text,
    get_lesson_confirm_kb,
    get_lesson_select_kb,
    get_student_poll_kb,
)
from config import ALLOWED_USER_ID, DEPUTY_USER_ID
from integrations.yandex_docs import (
    extract_client_config,
    find_date_column_start,
    find_lesson_column,
    find_student_row,
    get_month_sheet,
    get_students_list,
    get_yandex_cookie_header,
    normalize_fio,
    parse_date_cell,
    write_student_mark,
)
from services.attendance_manager import (
    AttendanceSession,
    apply_marks_to_sheet,
    calculate_summary_stats,
    clear_session,
    ensure_summary_headers,
    get_active_session,
    mark_all_remaining_present,
    record_student_mark,
    save_session_to_redis,
    step_back,
)
from services.models import Lesson


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


def test_get_yandex_cookie_header_variants():
    """Проверяет формирование заголовка Cookie из YANDEX_COOKIE или YANDEX_SESSION_ID."""
    with patch("config.YANDEX_COOKIE", "foo=bar; baz=qux"), patch("config.YANDEX_SESSION_ID", "123"):
        assert get_yandex_cookie_header() == "foo=bar; baz=qux"

    with patch("config.YANDEX_COOKIE", ""), patch("config.YANDEX_SESSION_ID", "3:123456"):
        assert get_yandex_cookie_header() == "Session_id=3:123456"

    with patch("config.YANDEX_COOKIE", ""), patch("config.YANDEX_SESSION_ID", ""):
        assert get_yandex_cookie_header() == ""


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


def test_get_days_select_kb():
    """Проверяет генерацию кнопок выбора дней."""
    from bot.templates.admin.attendance import get_days_select_kb
    kb = get_days_select_kb()
    assert len(kb.inline_keyboard) >= 2
    assert kb.inline_keyboard[0][0].callback_data.startswith("att:day:")


def test_lesson_model_number_property():
    """Проверяет свойство number модели Lesson (period + 1)."""
    l0 = Lesson(period=0, time_str="08:30", subject="Мат", lesson_type="Лек", teacher="", is_remote=False, room="", address="")
    l2 = Lesson(period=2, time_str="12:00", subject="Физ", lesson_type="Прак", teacher="", is_remote=False, room="", address="")
    assert l0.number == 1
    assert l2.number == 3


def test_get_lesson_select_kb_with_lesson_models():
    """Проверяет генерацию кнопок с объектами Lesson и дедупликацию подгрупп."""
    l1 = Lesson(period=0, time_str="08:30", subject="Информатика", lesson_type="Лаб", teacher="", is_remote=False, room="", address="", subgroup=1)
    l2 = Lesson(period=0, time_str="08:30", subject="Информатика", lesson_type="Лаб", teacher="", is_remote=False, room="", address="", subgroup=2)
    l3 = Lesson(period=1, time_str="10:00", subject="История", lesson_type="Лек", teacher="", is_remote=False, room="", address="")
    kb = get_lesson_select_kb([l1, l2, l3], chosen_date=date(2026, 9, 29))
    # 2 ряда пар (Пара 1 дедуплицирована, Пара 2) + 1 ряд навигации = 3 ряда
    assert len(kb.inline_keyboard) == 3
    assert kb.inline_keyboard[0][0].callback_data == "att:start:2026-09-29:1"
    assert kb.inline_keyboard[1][0].callback_data == "att:start:2026-09-29:2"


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


@pytest.mark.asyncio
async def test_redis_session_crud():
    """Проверяет сохранение, извлечение и удаление сессии посещаемости в Redis."""
    store = {}
    mock_redis = AsyncMock()
    mock_redis.set.side_effect = lambda k, v, ex=None: store.update({k: v})
    mock_redis.get.side_effect = lambda k: store.get(k)
    mock_redis.delete.side_effect = lambda k: store.pop(k, None)

    with patch("services.attendance_manager.get_redis", return_value=mock_redis):
        session = AttendanceSession(
            target_date="2026-09-29", lesson_num=1, lesson_title="Мат",
            students=[(5, "Иванов"), (6, "Петров")], initiator_id=123
        )
        await save_session_to_redis(session)
        assert "attendance:session" in store

        loaded = await get_active_session()
        assert loaded is not None
        assert loaded.lesson_num == 1
        assert len(loaded.students) == 2

        await clear_session()
        assert "attendance:session" not in store


@pytest.mark.asyncio
async def test_record_student_mark_and_step_back():
    """Проверяет выставление отметки студенту и шаг назад."""
    session = AttendanceSession(
        target_date="2026-09-29", lesson_num=1, lesson_title="Мат",
        students=[(5, "Иванов"), (6, "Петров")], initiator_id=123
    )
    with patch("services.attendance_manager.get_active_session", return_value=session), \
         patch("services.attendance_manager.save_session_to_redis", new_callable=AsyncMock):
        res = await record_student_mark("П")
        assert res.current_idx == 1
        assert res.marks["5"] == "П"

        back_res = await step_back()
        assert back_res.current_idx == 0
        assert "5" not in back_res.marks


@pytest.mark.asyncio
async def test_mark_all_remaining_present():
    """Проверяет массовую отметку 'П' всем оставшимся студентам."""
    session = AttendanceSession(
        target_date="2026-09-29", lesson_num=1, lesson_title="Мат",
        students=[(5, "Иванов"), (6, "Петров"), (7, "Сидоров")], initiator_id=123,
        current_idx=1, marks={"5": "Н"}
    )
    with patch("services.attendance_manager.get_active_session", return_value=session), \
         patch("services.attendance_manager.save_session_to_redis", new_callable=AsyncMock):
        res = await mark_all_remaining_present()
        assert res.current_idx == 3
        assert res.marks == {"5": "Н", "6": "П", "7": "П"}


@pytest.mark.asyncio
async def test_auto_close_attendance_session_protection():
    """Проверяет защиту активной сессии от удаления воркером."""
    from services.notifier import auto_close_attendance_session

    active_session = AttendanceSession(
        target_date="2026-09-29", lesson_num=2, lesson_title="Мат",
        students=[(5, "Иванов")], initiator_id=123, current_idx=1
    )
    with patch("services.notifier.get_active_session", return_value=active_session), \
         patch("services.notifier.clear_session", new_callable=AsyncMock) as mock_clear:
        await auto_close_attendance_session(2)
        mock_clear.assert_not_called()


def test_ensure_summary_headers():
    """Проверяет восстановление текстовых заголовков и кодов в сводных колонках."""
    wb = openpyxl.Workbook()
    ws = wb.active
    for c in range(1, 10):
        ws.cell(1, c, f"Col{c}")
    ensure_summary_headers(ws)
    assert ws.cell(2, 7).value == "Опоздавшие"
    assert ws.cell(3, 7).value == "О"
    assert ws.cell(2, 8).value == "отсутствие по уважительной причине"
    assert ws.cell(3, 8).value == "У"
    assert ws.cell(2, 9).value == "отсутствие по неуважительной причине"
    assert ws.cell(3, 9).value == "Н"


def test_find_sheet_rid():
    """Проверяет извлечение r:id листа из workbook.xml даже с xmlns атрибутами."""
    from integrations.yandex_docs import _find_sheet_rid
    xml = (
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheets><sheet xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'name="СЕНТ" sheetId="1" state="visible" r:id="rId1"/></sheets></workbook>'
    )
    assert _find_sheet_rid(xml, "СЕНТ") == "rId1"
    assert _find_sheet_rid(xml, "ОКТ") is None


def test_resolve_sheet_target_path():
    """Проверяет корректное разрешение пути листа по r:id с очисткой слэшей."""
    from integrations.yandex_docs import _resolve_sheet_target_path
    xml = (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Target="/xl/worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Target="worksheets/sheet2.xml"/>'
        '</Relationships>'
    )
    assert _resolve_sheet_target_path(xml, "rId1") == "xl/worksheets/sheet1.xml"
    assert _resolve_sheet_target_path(xml, "rId2") == "xl/worksheets/sheet2.xml"
    assert _resolve_sheet_target_path(xml, "rId3") is None


def test_cell_has_expected_mark_entities():
    """Проверяет распознавание отметок с HTML-сущностями и тегами <t> и <v>."""
    from integrations.yandex_docs import _cell_has_expected_mark
    assert _cell_has_expected_mark('<c r="D5" t="inlineStr"><is><t>&#1055;</t></is></c>', "П")
    assert _cell_has_expected_mark('<c r="D5" t="inlineStr"><is><t>О</t></is></c>', "О")
    assert _cell_has_expected_mark('<c r="D5"><v>Н</v></c>', "Н")
    assert not _cell_has_expected_mark('<c r="D5"><v>0</v></c>', "Н")
    assert not _cell_has_expected_mark('<c r="D5"/>', "П")


def test_extract_and_verify_marks_in_raw():
    """Проверяет извлечение листа и проверку отметок из реального xlsx-архива."""
    from integrations.yandex_docs import (
        _extract_sheet_xml,
        _verify_marks_in_raw,
        save_workbook_to_bytes,
    )
    wb = create_mock_workbook()
    ws = wb["СЕНТ"]
    ws.cell(5, 4, "П")
    ws.cell(6, 4, "Н")
    ws.cell(2, 20, "Опоздавшие")
    raw = save_workbook_to_bytes(wb)
    assert _extract_sheet_xml(raw, "СЕНТ") is not None
    assert _extract_sheet_xml(raw, "ДЕК") is None
    assert _verify_marks_in_raw(raw, date(2026, 9, 29), {"5": "П", "6": "Н"}) is True
    assert _verify_marks_in_raw(raw, date(2026, 9, 29), {"5": "О"}) is False


@pytest.mark.asyncio
async def test_verify_upload_with_mock_bytes():
    """Проверяет асинхронный вызов verify_upload при успешном скачивании байтов."""
    from integrations.yandex_docs import (
        WopiSession,
        save_workbook_to_bytes,
        verify_upload,
    )
    wb = create_mock_workbook()
    ws = wb["СЕНТ"]
    ws.cell(5, 4, "П")
    ws.cell(2, 20, "Опоздавшие")
    raw = save_workbook_to_bytes(wb)
    session = WopiSession("https://wopi.test/files/1", "token", "lock1")
    with patch("integrations.yandex_docs._download_raw_bytes", new_callable=AsyncMock, return_value=raw):
        res = await verify_upload(session, date(2026, 9, 29), 2, {"5": "П"})
        assert res is True


@pytest.mark.asyncio
async def test_try_commit_once_success_handling():
    """Проверяет успешное сохранение в _try_commit_once при HTTP 200 от WOPI."""
    from services.attendance_manager import _try_commit_once
    session = AttendanceSession(
        target_date="2026-09-29", lesson_num=2, lesson_title="Тест",
        students=[(5, "Иванов")], marks={"5": "П"}, initiator_id=123
    )
    with patch("services.attendance_manager.init_wopi_session", new_callable=AsyncMock), \
         patch("services.attendance_manager.download_workbook", new_callable=AsyncMock, return_value=create_mock_workbook()), \
         patch("services.attendance_manager.upload_workbook", new_callable=AsyncMock, return_value=True), \
         patch("services.attendance_manager.verify_upload", new_callable=AsyncMock, return_value=True):
        assert await _try_commit_once(session, date(2026, 9, 29)) is True


@pytest.mark.asyncio
async def test_commit_session_to_table_clears_on_success():
    """Проверяет сброс активной сессии в Redis после успешного сохранения."""
    from services.attendance_manager import commit_session_to_table
    session = AttendanceSession(
        target_date="2026-09-29", lesson_num=2, lesson_title="Тест",
        students=[(5, "Иванов")], marks={"5": "П"}, initiator_id=123
    )
    with patch("services.attendance_manager._try_commit_once", new_callable=AsyncMock, return_value=True), \
         patch("services.attendance_manager.clear_session", new_callable=AsyncMock) as mock_clear:
        ok = await commit_session_to_table(session)
        assert ok is True
        mock_clear.assert_called_once()

