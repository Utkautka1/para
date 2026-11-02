"""
Шаблоны сообщений и клавиатур для модуля отметки посещаемости.

Содержит:
  - Инлайн-клавиатуры для подтверждения пары, выбора статуса (П, О, У, Н)
  - Кнопки быстрого завершения ('Все остальные П') и шага назад
  - Форматирование карточек студентов и итоговой сводки
"""

from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import TIMEZONE
from services.attendance_manager import AttendanceSession


def get_lesson_confirm_kb(lesson_num: int) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру подтверждения проведения пары.

    Предоставляет старосте выбор: начать опрос либо отметить отмену пары.
    Используется в диалоге напоминания старосте перед началом занятия.

    Возвращает объект InlineKeyboardMarkup с двумя кнопками выбора.
    """

    kb = [
        [
            InlineKeyboardButton(text="✅ Да, отметить", callback_data=f"att:start:{lesson_num}"),
            InlineKeyboardButton(text="❌ Пары нет / Отменена", callback_data=f"att:cancel:{lesson_num}"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_student_poll_kb(can_back: bool) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру выставления статуса студенту (П, О, У, Н).

    Включает кнопку быстрого завершения 'Все остальные П' и шаг назад.
    Кнопка 'Назад' динамически скрывается на первом студенте очереди.

    Возвращает InlineKeyboardMarkup с матрицей кнопок отметки.
    """

    kb = [
        [
            InlineKeyboardButton(text="🟢 П (Присутствует)", callback_data="att:mark:П"),
            InlineKeyboardButton(text="🟡 О (Опоздание)", callback_data="att:mark:О"),
        ],
        [
            InlineKeyboardButton(text="🔵 У (Уважительная)", callback_data="att:mark:У"),
            InlineKeyboardButton(text="🔴 Н (Неуважительная)", callback_data="att:mark:Н"),
        ],
        [InlineKeyboardButton(text="⚡️ Все остальные «П»", callback_data="att:all_p")],
    ]
    nav_row = []
    if can_back:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="att:back"))

    nav_row.append(InlineKeyboardButton(text="❌ Отменить", callback_data="att:abort"))
    kb.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=kb)


def format_confirm_text(lesson_num: int, title: str, teacher: str) -> str:
    """
    Формирует текст диалога подтверждения факта проведения занятия.

    Включает номер пары, название дисциплины и ФИО преподавателя.
    Используется ботом перед открытием формы пофамильного опроса.

    Возвращает валидную HTML-строку запроса подтверждения.
    """

    return (
        f"🔔 <b>Пара {lesson_num}</b>: {title}\n"
        f"👨‍🏫 Преподаватель: <i>{teacher}</i>\n\n"
        f"❓ <i>Пара сейчас проводится? Начать отметку посещаемости?</i>"
    )


def format_student_card(session: AttendanceSession) -> str:
    """
    Формирует текст карточки текущего студента с прогресс-индикатором.

    Отображает номер текущего студента [X/Y], название предмета и ФИО.
    Обеспечивает визуальный контекст во время быстрого опроса старостой.

    Возвращает HTML-текст карточки студента для Telegram.
    """

    total = len(session.students)
    idx = session.current_idx + 1
    _, fio = session.students[session.current_idx]

    return (
        f"📋 <b>Посещаемость: Пара {session.lesson_num}</b>\n"
        f"<i>{session.lesson_title}</i>\n\n"
        f"👤 <b>[{idx}/{total}]</b> <code>{fio}</code>\n\n"
        f"Выберите статус посещения:"
    )


def _format_absent_students(session: AttendanceSession) -> str:
    """
    Формирует список отсутствовавших и опоздавших студентов с их отметками.

    Сокращает имя до инициала (Фамилия И.) для компактного отображения.
    Используется в итоговых сводках старосты.

    Возвращает строку со списком отсутствующих или пустую строку.
    """

    absent_names: list[str] = []
    for row_idx, fio in session.students:
        mark = session.marks.get(str(row_idx))
        if mark in {"Н", "У", "О"}:
            parts = fio.split()
            short_name = f"{parts[0]} {parts[1][:1]}." if len(parts) > 1 else fio
            absent_names.append(f"{short_name} ({mark})")

    return "\n\nОтсутствующие / Опоздавшие:\n• " + "\n• ".join(absent_names) if absent_names else ""


def format_summary_text(session: AttendanceSession, stats: dict[str, int]) -> str:
    """
    Формирует итоговый текстовый отчет после успешной фиксации посещаемости.

    Выводит счетчики по каждому статусу (П, О, У, Н) и список пропустивших.
    Отправляется старосте после записи данных в Яндекс Документы.

    Возвращает итоговый HTML-текст отчета посещаемости пары.
    """

    absent_str = _format_absent_students(session)

    return (
        f"✅ <b>Посещаемость за пару {session.lesson_num} сохранена!</b>\n\n"
        f"🟢 Присутствуют (П): <b>{stats.get('П', 0)}</b>\n"
        f"🟡 Опоздали (О): <b>{stats.get('О', 0)}</b>\n"
        f"🔵 Уважительная (У): <b>{stats.get('У', 0)}</b>\n"
        f"🔴 Неуважительная (Н): <b>{stats.get('Н', 0)}</b>"
        f"{absent_str}"
    )


def format_partner_attendance_report(session: AttendanceSession, stats: dict[str, int], initiator_title: str) -> str:
    """
    Формирует уведомление о сохранении посещаемости для второго администратора.

    Указывает, кто именно из старост выполнил отметку, предмет и баланс меток.
    Обеспечивает прозрачность и предотвращает дублирование работы старост.

    Возвращает сводный HTML-текст уведомления для напарника.
    """

    base_summary = format_summary_text(session, stats)

    return (
        f"📋 <b>Уведомление о посещаемости</b>\n"
        f"👤 <b>Отметил:</b> {initiator_title}\n"
        f"📖 <b>Пара:</b> {session.lesson_title}\n\n"
        f"{base_summary}"
    )


def format_partner_cancel_report(lesson_num: int | str, initiator_title: str) -> str:
    """
    Формирует уведомление об отмене занятия для второго администратора.

    Информирует напарника о том, что пара отменена или не состоялась.
    Исключает необходимость повторного уточнения статуса пары.

    Возвращает короткий HTML-текст уведомления об отмене.
    """

    return (
        f"ℹ️ <b>Уведомление об отмене пары</b>\n\n"
        f"👤 <b>Инициатор:</b> {initiator_title}\n"
        f"❌ Отметка для пары <b>{lesson_num}</b> отменена (пары нет / отменена)."
    )


def get_days_select_kb() -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру выбора учебного дня за последнюю неделю.

    Исключает воскресенья как неучебные дни колледжа.
    Служит точкой входа для ретроспективного заполнения журнала старостой.

    Возвращает объект InlineKeyboardMarkup со списком дат.
    """

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
    """
    Генерирует кнопки выбора пар для конкретного учебного дня.

    Отображает реальные предметы из расписания дня либо дефолтные пары 1-6.
    Содержит кнопку возврата к выбору дня недели и отмену.

    Возвращает собранный объект InlineKeyboardMarkup.
    """

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

    kb.append(
        [
            InlineKeyboardButton(text="⬅️ Выбрать другой день", callback_data="att:menu"),
            InlineKeyboardButton(text="❌ Закрыть", callback_data="att:close"),
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=kb)
