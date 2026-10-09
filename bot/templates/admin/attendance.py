"""
Шаблоны сообщений и клавиатур для модуля отметки посещаемости.

Содержит:
  - Инлайн-клавиатуры для подтверждения пары, выбора статуса (П, О, У, Н)
  - Кнопки быстрого завершения ('Все остальные П') и шага назад
  - Форматирование карточек студентов и итоговой сводки
"""


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from services.attendance_manager import AttendanceSession


def get_lesson_confirm_kb(lesson_num: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения факта проведения пары."""
    kb = [
        [
            InlineKeyboardButton(text="✅ Да, отметить", callback_data=f"att:start:{lesson_num}"),
            InlineKeyboardButton(text="❌ Пары нет / Отменена", callback_data=f"att:cancel:{lesson_num}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_student_poll_kb(can_back: bool) -> InlineKeyboardMarkup:
    """Генерирует 4 инлайн-кнопки статусов и кнопки навигации."""
    kb = [
        [
            InlineKeyboardButton(text="🟢 П (Присутствует)", callback_data="att:mark:П"),
            InlineKeyboardButton(text="🟡 О (Опоздание)", callback_data="att:mark:О")
        ],
        [
            InlineKeyboardButton(text="🔵 У (Уважительная)", callback_data="att:mark:У"),
            InlineKeyboardButton(text="🔴 Н (Неуважительная)", callback_data="att:mark:Н")
        ],
        [
            InlineKeyboardButton(text="⚡️ Все остальные «П»", callback_data="att:all_p")
        ]
    ]
    nav_row = []
    if can_back:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="att:back"))
    nav_row.append(InlineKeyboardButton(text="❌ Отменить", callback_data="att:abort"))
    kb.append(nav_row)
    return InlineKeyboardMarkup(inline_keyboard=kb)


def format_confirm_text(lesson_num: int, title: str, teacher: str) -> str:
    """Формирует текст запроса подтверждения проведения пары."""
    return (
        f"🔔 <b>Пара {lesson_num}</b>: {title}\n"
        f"👨‍🏫 Преподаватель: <i>{teacher}</i>\n\n"
        f"❓ <i>Пара сейчас проводится? Начать отметку посещаемости?</i>"
    )


def format_student_card(session: AttendanceSession) -> str:
    """Формирует текст карточки текущего студента с прогресс-баром."""
    total = len(session.students)
    idx = session.current_idx + 1
    _, fio = session.students[session.current_idx]
    return (
        f"📋 <b>Посещаемость: Пара {session.lesson_num}</b>\n"
        f"<i>{session.lesson_title}</i>\n\n"
        f"👤 <b>[{idx}/{total}]</b> <code>{fio}</code>\n\n"
        f"Выберите статус посещения:"
    )


def format_summary_text(session: AttendanceSession, stats: dict[str, int]) -> str:
    """Формирует финальный отчёт после сохранения посещаемости."""
    absent_names: list[str] = []
    for row_idx, fio in session.students:
        mark = session.marks.get(str(row_idx))
        if mark in {"Н", "У", "О"}:
            short_name = fio.split()[0] + " " + fio.split()[1][:1] + "."
            absent_names.append(f"{short_name} ({mark})")
    absent_str = "\n\nОтсутствующие / Опоздавшие:\n• " + "\n• ".join(absent_names) if absent_names else ""
    return (
        f"✅ <b>Посещаемость за пару {session.lesson_num} сохранена!</b>\n\n"
        f"🟢 Присутствуют (П): <b>{stats.get('П', 0)}</b>\n"
        f"🟡 Опоздали (О): <b>{stats.get('О', 0)}</b>\n"
        f"🔵 Уважительная (У): <b>{stats.get('У', 0)}</b>\n"
        f"🔴 Неуважительная (Н): <b>{stats.get('Н', 0)}</b>"
        f"{absent_str}"
    )


def get_days_select_kb() -> InlineKeyboardMarkup:
    """Генерирует инлайн-кнопки выбора учебных дней для отметки посещаемости."""
    from datetime import datetime, timedelta

    from config import TIMEZONE
    today = datetime.now(TIMEZONE).date()
    weekdays_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    kb = []
    for offset in range(7):
        d = today - timedelta(days=offset)
        if d.weekday() == 6:
            continue
        wd = weekdays_ru[d.weekday()]
        label = f"📅 Сегодня ({d.strftime('%d.%m')}, {wd})" if offset == 0 else f"📆 {d.strftime('%d.%m')} ({wd})"
        kb.append([InlineKeyboardButton(text=label, callback_data=f"att:day:{d.isoformat()}")])
    kb.append([InlineKeyboardButton(text="❌ Закрыть", callback_data="att:close")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_lesson_select_kb(lessons: list, chosen_date=None) -> InlineKeyboardMarkup:
    """Формирует список пар на выбор для указанной даты."""
    from datetime import datetime

    from config import TIMEZONE
    d_obj = chosen_date or datetime.now(TIMEZONE).date()
    d_str = d_obj.isoformat()
    kb, seen = [], set()
    for les in lessons:
        num = getattr(les, "number", getattr(les, "period", 0) + 1)
        if num not in seen:
            seen.add(num)
            subj = getattr(les, "subject", "")[:20]
            kb.append([InlineKeyboardButton(text=f"Пара {num}: {subj}", callback_data=f"att:start:{d_str}:{num}")])
    if not kb:
        for num in range(1, 7):
            kb.append([InlineKeyboardButton(text=f"Пара {num}", callback_data=f"att:start:{d_str}:{num}")])
    kb.append([
        InlineKeyboardButton(text="⬅️ Выбрать другой день", callback_data="att:menu"),
        InlineKeyboardButton(text="❌ Закрыть", callback_data="att:close")
    ])
    return InlineKeyboardMarkup(inline_keyboard=kb)
