"""
Модуль стильного и информативного форматирования сообщений бота.

Формирует расписание с типом пары (Лек/Пр), точным адресом корпуса КТМУ
(Цветочная ул., 8 / Вознесенский пр., 44) и реквизитами подключений.
"""

from datetime import date
from typing import List, Optional, Tuple
from config import GROUP_NAME
from services.models import Lesson

WEEKDAYS_RU = [
    "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
]


def format_lesson_card(lesson: Lesson) -> str:
    """
    Формирует подробную карточку пары с подгруппой и бейджем потока.

    :param lesson: Объект пары
    :return: HTML-текст карточки
    """
    type_suffix = f" ({lesson.lesson_type})" if lesson.lesson_type else ""
    stream_suffix = " • 🔗 <b>поток</b>" if lesson.is_stream else ""
    sg_suffix = f" • 👥 <b>Подгруппа {lesson.subgroup}</b>" if lesson.subgroup > 0 else ""
    loc_str = "🌐 Дистанционно" if lesson.is_remote else f"📍 🏢 {lesson.address} (Каб. {lesson.room})"

    card = (
        f"▪️ <b>{lesson.period + 1} пара</b> (<code>{lesson.time_str}</code>){sg_suffix}{stream_suffix}\n"
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


def _parse_time_interval_minutes(time_str: str) -> Optional[Tuple[int, int]]:
    """Извлекает время начала и конца пары в минутах от начала суток."""
    import re
    matches = re.findall(r"(\d{1,2})[:\.](\d{2})", time_str)
    if len(matches) >= 2:
        s_min = int(matches[0][0]) * 60 + int(matches[0][1])
        e_min = int(matches[1][0]) * 60 + int(matches[1][1])
        return s_min, e_min
    return None


def _check_single_lesson_status(lesson: Lesson, n_min: int) -> Tuple[bool, str]:
    """
    Проверяет статус одной пары относительно текущего времени в минутах.

    :param lesson: Объект пары
    :param n_min: Текущее время в минутах от начала суток
    :return: Кортеж (найдено_ли_состояние, HTML_баннер)
    """
    interval = _parse_time_interval_minutes(lesson.time_str)
    if not interval:
        return False, ""
    s_min, e_min = interval
    if s_min <= n_min <= e_min:
        left_str = format_minutes(e_min - n_min)
        return True, f"⏳ <b>СЕЙЧАС ИДЁТ {lesson.period + 1} ПАРА</b> (осталось {left_str})\n\n"
    if n_min < s_min:
        before_str = format_minutes(s_min - n_min)
        return True, f"🔜 <b>СЛЕДУЮЩАЯ {lesson.period + 1} ПАРА</b> (через {before_str})\n\n"
    return False, ""


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

    n_min = now_dt.time().hour * 60 + now_dt.time().minute
    for l in lessons:
        found, banner = _check_single_lesson_status(l, n_min)
        if found:
            return banner
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


def format_week_lesson_loc(lesson: Lesson) -> str:
    """Формирует компактную строку локации для недельного обзора."""
    if lesson.is_remote:
        return "🌐 Дистанционно"
    if "вознесен" in lesson.address.lower():
        campus = "Вознесенский"
    else:
        campus = "Цветочная"
    return f"📍 Каб. {lesson.room} ({campus})"


def format_week_lesson_card(lesson: Lesson) -> str:
    """Формирует отдельную карточку пары в блоке цитаты blockquote."""
    type_suffix = f" ({lesson.lesson_type})" if lesson.lesson_type else ""
    stream_badge = " • 🔗 поток" if lesson.is_stream else ""
    sg_badge = f" • 👥 {lesson.subgroup} п/г" if lesson.subgroup > 0 else ""
    loc = format_week_lesson_loc(lesson)
    return (
        f"<blockquote>▪️ <b>{lesson.period + 1} пара</b> (<code>{lesson.time_str}</code>){stream_badge}{sg_badge}\n"
        f"<b>{lesson.subject}</b>{type_suffix}\n"
        f"🏛 <i>{lesson.teacher}</i> • {loc}</blockquote>"
    )


def format_week_day_block(day_date: date, lessons: List[Lesson]) -> str:
    """Формирует блок одного учебного дня для недельного расписания."""
    w_str = WEEKDAYS_RU[day_date.weekday()]
    d_str = day_date.strftime("%d.%m")
    header = f"🗓 <b>{w_str}, {d_str}</b>\n"
    if not lessons:
        return f"{header}<blockquote><i>Занятий нет — свободный день! ☕️</i></blockquote>"
    cards = [format_week_lesson_card(l) for l in lessons]
    return f"{header}" + "\n".join(cards)


def format_week_schedule(days_data: List[Tuple[date, List[Lesson]]]) -> str:
    """Формирует аккуратное, структурированное расписание на неделю."""
    header = f"🎓 <b>РАСПИСАНИЕ НА НЕДЕЛЮ ({GROUP_NAME})</b>\n────────────────────────────\n\n"
    day_blocks = [format_week_day_block(d, l) for d, l in days_data]
    return header + "\n\n".join(day_blocks)


def format_reminder_text(lesson: Lesson) -> str:
    """
    Формирует сдержанное и точное сообщение-напоминание.

    :param lesson: Предстоящее занятие
    :return: HTML текст напоминания
    """
    card = format_lesson_card(lesson)
    return f"⏰ <b>Через 10 минут начинается пара!</b>\n\n{card}"
