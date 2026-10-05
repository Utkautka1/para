"""
Тесты для сквозной аналитики посещаемости и авто-обновления топика Посещаемость.

Проверяет:
  - Инициализацию и подсчет отметок П/О/У/Н по строкам и листам
  - Поиск студента по ФИО в реестре
  - Форматирование сообщения топика и карточки /my_attendance
  - Сохранение и загрузку состояния STATE_FILE
  - Хэндлеры команд и инлайн-кнопок пользователя и администратора
"""

from unittest.mock import AsyncMock, MagicMock, patch
import openpyxl
import pytest
from aiogram.types import CallbackQuery, Chat, Message, User

from bot.handlers.admin.panel import cb_admin_force_att_topic, cb_admin_recreate_att_topic
from bot.handlers.user.attendance import (
    _calculate_attendance_percent,
    _format_personal_month_breakdown,
    cb_att_topic_refresh,
    cb_my_attendance_refresh,
    cmd_my_attendance,
    format_personal_attendance_card,
)
from services.attendance_stats import (
    _count_row_marks,
    _init_student_stat,
    find_student_attendance,
    parse_workbook_attendance,
)
from services.attendance_topic_updater import (
    format_attendance_topic_message,
    format_student_line,
    load_attendance_topic_state,
    save_attendance_topic_state,
)


def create_test_attendance_wb() -> openpyxl.Workbook:
    """Создает мок-книгу Excel с двумя месяцами для проверки агрегации."""
    wb = openpyxl.Workbook()
    ws_sep = wb.active
    ws_sep.title = "СЕНТ"
    ws_sep.cell(5, 2, "Базаров Аюр")
    ws_sep.cell(5, 3, "П")
    ws_sep.cell(5, 4, "Н")
    ws_sep.cell(5, 5, "=COUNTIF(C5:D5, E3)")

    ws_oct = wb.create_sheet(title="ОКТ")
    ws_oct.cell(5, 2, "Базаров Аюр")
    ws_oct.cell(5, 3, "П")
    ws_oct.cell(5, 4, "О")
    ws_oct.cell(5, 5, "У")
    ws_oct.cell(5, 6, "=COUNTIF(...)")
    return wb


def test_init_student_stat():
    """Проверяет начальную структуру счётчиков студента."""
    stat = _init_student_stat("Иванов Иван")
    assert stat["fio"] == "Иванов Иван"
    assert stat["total"] == {"П": 0, "О": 0, "У": 0, "Н": 0}
    assert stat["months"] == {}


def test_count_row_marks():
    """Проверяет подсчет отметок в строке без учета формул COUNTIF."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.cell(5, 3, "П")
    ws.cell(5, 4, "Н")
    ws.cell(5, 5, "О")
    ws.cell(5, 6, "=COUNTIF(...)")
    ws.cell(5, 7, "=COUNTIF(...)")
    ws.cell(5, 8, "=COUNTIF(...)")
    counts = _count_row_marks(ws, 5, ws.max_column)
    assert counts["П"] == 1
    assert counts["Н"] == 1
    assert counts["О"] == 1
    assert counts["У"] == 0


def test_parse_workbook_attendance():
    """Проверяет сквозную агрегацию по всем месячным листам."""
    wb = create_test_attendance_wb()
    stats = parse_workbook_attendance(wb)
    assert "Базаров Аюр" in stats
    tot = stats["Базаров Аюр"]["total"]
    assert tot["П"] == 2
    assert tot["О"] == 1
    assert tot["У"] == 1
    assert tot["Н"] == 1
    assert "СЕНТ" in stats["Базаров Аюр"]["months"]
    assert "ОКТ" in stats["Базаров Аюр"]["months"]


def test_find_student_attendance():
    """Проверяет поиск студента по полному имени и по фамилии."""
    stats = {
        "Базаров Аюр Этигэлович": {"total": {"П": 10}},
        "Барчугова Ева Алексеевна": {"total": {"П": 20}},
    }
    assert find_student_attendance(stats, "Базаров Аюр") is not None
    assert find_student_attendance(stats, "Барчугова") is not None
    assert find_student_attendance(stats, "Несуществующий") is None


def test_calculate_attendance_percent():
    """Проверяет вычисление процентов посещаемости."""
    assert _calculate_attendance_percent(0, 0) == "100.0%"
    assert _calculate_attendance_percent(8, 10) == "80.0%"
    assert _calculate_attendance_percent(9, 11) == "81.8%"


def test_format_personal_month_breakdown():
    """Проверяет отображение помесячного среза."""
    months = {
        "СЕНТ": {"П": 5, "О": 0, "У": 0, "Н": 1},
        "ОКТ": {"П": 10, "О": 1, "У": 2, "Н": 0},
    }
    text = _format_personal_month_breakdown(months)
    assert "СЕНТ:</b> ✅ 5" in text
    assert "ОКТ:</b> ✅ 10" in text


def test_format_personal_attendance_card():
    """Проверяет HTML-карточку персональной посещаемости студента."""
    data = {
        "fio": "Барчугова Ева",
        "total": {"П": 15, "О": 1, "У": 0, "Н": 2},
        "months": {"СЕНТ": {"П": 15, "О": 1, "У": 0, "Н": 2}},
    }
    card = format_personal_attendance_card("Барчугова Ева", data)
    assert "Барчугова Ева" in card
    assert "✅ 15" in card
    assert "83.3%" in card


def test_format_attendance_topic_message():
    """Проверяет форматирование общего сообщения реестра для топика."""
    empty_msg = format_attendance_topic_message({})
    assert "СВОДНЫЙ РЕЕСТР" in empty_msg
    assert "загружаются" in empty_msg

    stats = {
        "Базаров Аюр": {"total": {"П": 2, "О": 0, "У": 0, "Н": 11}},
        "Барчугова Ева": {"total": {"П": 9, "О": 1, "У": 0, "Н": 2}},
    }
    msg = format_attendance_topic_message(stats)
    assert "Базаров Аюр" in msg
    assert "Барчугова Ева" in msg
    assert "Студентов в реестре:</b> 2" in msg


def test_topic_state_storage(tmp_path):
    """Проверяет сохранение и загрузку ID сообщения топика."""
    fake_state = str(tmp_path / "att_state.json")
    with patch("services.attendance_topic_updater.STATE_FILE", fake_state):
        save_attendance_topic_state(12345)
        assert load_attendance_topic_state() == 12345


@pytest.mark.asyncio
async def test_cmd_my_attendance_in_group():
    """Проверяет отказ вывода персональной статистики в группе/топике."""
    msg = AsyncMock(spec=Message)
    msg.chat = Chat(id=-100123, type="supergroup")
    msg.reply = AsyncMock()
    await cmd_my_attendance(msg)
    msg.reply.assert_called_once()
    assert "только в личных сообщениях" in msg.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_cmd_my_attendance_authorized_private():
    """Проверяет успешный вывод персональной карточки в ЛС."""
    msg = AsyncMock(spec=Message)
    msg.chat = Chat(id=111, type="private")
    msg.from_user = User(id=111, is_bot=False, first_name="Ева", username="eva")
    msg.answer = AsyncMock()
    with patch("bot.handlers.user.attendance.process_user_auth", return_value=(True, False, {"full_name": "Барчугова Ева"})), \
         patch("bot.handlers.user.attendance.fetch_all_time_attendance", return_value={"Барчугова Ева": {"total": {"П": 10, "О": 0, "У": 0, "Н": 1}, "months": {}}}):
        await cmd_my_attendance(msg)
        msg.answer.assert_called_once()
        assert "Барчугова Ева" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_cb_att_topic_refresh():
    """Проверяет обработку клика 'Обновить' в топике посещаемости."""
    cb = AsyncMock(spec=CallbackQuery)
    cb.answer = AsyncMock()
    with patch("bot.handlers.user.attendance.sync_attendance_topic_message", return_value=True):
        await cb_att_topic_refresh(cb)
        assert cb.answer.call_count == 2
        assert "успешно обновлена" in cb.answer.call_args_list[1][0][0]


@pytest.mark.asyncio
async def test_admin_att_topic_callbacks():
    """Проверяет админские кнопки принудительного обновления и пересоздания."""
    cb = AsyncMock(spec=CallbackQuery)
    cb.message = AsyncMock(spec=Message)
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    with patch("services.attendance_topic_updater.sync_attendance_topic_message", return_value=True), \
         patch("services.attendance_topic_updater.recreate_attendance_topic_message", return_value=True):
        await cb_admin_force_att_topic(cb)
        await cb_admin_recreate_att_topic(cb)
        assert cb.message.edit_text.call_count == 2
