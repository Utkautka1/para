"""
Модуль стильного и информативного форматирования сообщений бота.

Формирует расписание с типом пары (Лек/Пр), точным адресом корпуса КТМУ
(Цветочная ул., 8 / Вознесенский пр., 44) и реквизитами подключений.
"""

from datetime import date
from typing import List, Tuple
from config import GROUP_NAME
from services.schedule_parser import Lesson

WEEKDAYS_RU = [
    "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
]


def format_lesson_card(lesson: Lesson) -> str:
    """
    Формирует подробную карточку пары с подгруппой.

    :param lesson: Объект пары
    :return: HTML-текст карточки
    """
    type_suffix = f" ({lesson.lesson_type})" if lesson.lesson_type else ""
    sg_suffix = f" • 👥 <b>Подгруппа {lesson.subgroup}</b>" if lesson.subgroup > 0 else ""
    if lesson.is_remote:
        loc_str = "🌐 Дистанционно"
    else:
        loc_str = f"📍 🏢 {lesson.address} (Каб. {lesson.room})"

    card = (
        f"▪️ <b>{lesson.period + 1} пара</b> (<code>{lesson.time_str}</code>){sg_suffix}\n"
        f"<b>{lesson.subject}</b>{type_suffix}\n"
        f"🏛 <i>{lesson.teacher}</i>\n"
        f"{loc_str}"
    )
    if lesson.is_remote and (lesson.remote_passcode or lesson.remote_meeting_id):
        if lesson.remote_meeting_id:
            card += f"\n🆔 <b>Идентификатор Zoom:</b> <code>{lesson.remote_meeting_id}</code>"
        if lesson.remote_passcode:
            card += f"\n🔐 <b>Код доступа:</b> <code>{lesson.remote_passcode}</code>"
    return card


def format_minutes(total_minutes: int) -> str:
    """
    Преобразует общее количество минут в читаемую строку (часы и минуты).

    :param total_minutes: Количество минут
    :return: Форматированная строка
    """
    hours = total_minutes // 60
    mins = total_minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours} ч {mins} мин"
    if hours > 0:
        return f"{hours} ч"
    return f"{mins} мин"


def get_lesson_status_banner(lessons: List[Lesson], target_date: date) -> str:
    """
    Рассчитывает и формирует статусный баннер пары для текущего дня.

    :param lessons: Список пар на день
    :param target_date: Дата
    :return: HTML фрагмент со статусом пары или пустая строка
    """
    from datetime import datetime
    from config import TIMEZONE
    now_dt = datetime.now(TIMEZONE)
    if target_date != now_dt.date() or not lessons:
        return ""

    now_t = now_dt.time()
    for l in lessons:
        try:
            parts = l.time_str.split("–")
            sh, sm = map(int, parts[0].strip().split(":"))
            eh, em = map(int, parts[1].strip().split(":"))
            s_min = sh * 60 + sm
            e_min = eh * 60 + em
            n_min = now_t.hour * 60 + now_t.minute
            if s_min <= n_min <= e_min:
                left_str = format_minutes(e_min - n_min)
                return f"⏳ <b>СЕЙЧАС ИДЁТ {l.period + 1} ПАРА</b> (осталось {left_str})\n\n"
            if n_min < s_min:
                before_str = format_minutes(s_min - n_min)
                return f"🔜 <b>СЛЕДУЮЩАЯ {l.period + 1} ПАРА</b> (через {before_str})\n\n"
        except Exception:
            continue
    return "✅ <b>Все пары на сегодня завершены!</b>\n\n"


def format_day_schedule(target_date: date, lessons: List[Lesson]) -> str:
    """
    Собирает расписание на день в чистый HTML-блок.

    :param target_date: Целевая дата
    :param lessons: Список пар
    :return: Итоговый HTML текст
    """
    weekday_str = WEEKDAYS_RU[target_date.weekday()]
    date_str = target_date.strftime("%d.%m")
    header = f"<b>{GROUP_NAME} • {weekday_str}, {date_str}</b>\n"
    banner = get_lesson_status_banner(lessons, target_date)
    header += banner

    if not lessons:
        return header + "<i>Занятий нет — свободный день!</i> ☕️"

    cards = [format_lesson_card(l) for l in lessons]
    return header + "\n\n".join(cards)


def format_week_day_block(day_date: date, lessons: List[Lesson]) -> str:
    """
    Формирует красивый блок одного дня для недельного просмотра.

    :param day_date: Дата дня
    :param lessons: Список пар на этот день
    :return: HTML фрагмент дня
    """
    w_str = WEEKDAYS_RU[day_date.weekday()]
    d_str = day_date.strftime("%d.%m")
    day_block = f"🗓 <b>{w_str}, {d_str}</b>\n"
    if not lessons:
        return day_block + "  <i>Пар нет</i>\n"

    cards = []
    for l in lessons:
        type_str = f" ({l.lesson_type})" if l.lesson_type else ""
        if l.is_remote:
            loc = "🌐 <i>Дистанционно</i>"
        else:
            loc = f"📍 <i>{l.address}</i> (Каб. {l.room})"
        card = (
            f"  ▪️ <b>{l.period + 1} пара</b> (<code>{l.time_str}</code>) • {loc}\n"
            f"  <b>{l.subject}</b>{type_str}\n"
            f"  👨‍🏫 <i>{l.teacher}</i>"
        )
        cards.append(card)
    return day_block + "\n\n".join(cards) + "\n"


def format_week_schedule(days_data: List[Tuple[date, List[Lesson]]]) -> str:
    """
    Формирует наглядное, красиво сверстанное расписание на неделю.

    :param days_data: Список кортежей (дата, пары)
    :return: Сводный HTML текст
    """
    header = f"🎓 <b>РАСПИСАНИЕ НА НЕДЕЛЮ ({GROUP_NAME})</b>\n{'━' * 28}\n\n"
    day_blocks = [format_week_day_block(d, l) for d, l in days_data]
    return header + "\n".join(day_blocks)


def format_reminder_text(lesson: Lesson) -> str:
    """
    Формирует сдержанное и точное сообщение-напоминание.

    :param lesson: Предстоящее занятие
    :return: HTML текст напоминания
    """
    card = format_lesson_card(lesson)
    return f"⏰ <b>Через 10 минут начинается пара!</b>\n\n{card}"
