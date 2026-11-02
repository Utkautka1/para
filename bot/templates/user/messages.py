"""
Модуль стильного и информативного форматирования сообщений бота.

Формирует расписание с типом пары (Лек/Пр), точным адресом корпуса КТМУ
(Цветочная ул., 8 / Вознесенский пр., 44) и реквизитами подключений.
"""

import html
import re
from datetime import date, datetime

from config import GROUP_NAME, TIMEZONE
from services.models import Lesson

WEEKDAYS_RU = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


def _format_remote_credentials(lesson: Lesson) -> str:
    """
    Форматирует идентификатор конференции и пароль Zoom/Телемост в HTML.

    Экранирует спецсимволы Telegram HTML и оборачивает коды в тег <code>.
    Возвращает пустую строку, если занятие очное или реквизиты не указаны.

    Возвращает сформированный HTML блок с реквизитами подключения.
    """

    if not lesson.is_remote or not (lesson.remote_passcode or lesson.remote_meeting_id):
        return ""

    lines: list[str] = []
    if lesson.remote_meeting_id:
        m_id = html.escape(lesson.remote_meeting_id)
        lines.append(f"\n🆔 <b>Идентификатор Zoom:</b> <code>{m_id}</code>")

    if lesson.remote_passcode:
        p_code = html.escape(lesson.remote_passcode)
        lines.append(f"\n🔐 <b>Код доступа:</b> <code>{p_code}</code>")

    return "".join(lines)


def format_lesson_card(lesson: Lesson) -> str:
    """
    Формирует подробную информационную карточку пары для Telegram-сообщения.

    Включает номер, время, предмет, тип, преподавателя, корпус и кабинет.
    Экранирует потенциально опасные HTML-символы во всех строковых полях.

    Возвращает красивый отформатированный HTML-текст карточки занятия.
    """

    subj = html.escape(lesson.subject)
    teacher = html.escape(lesson.teacher)
    l_type = f" ({html.escape(lesson.lesson_type)})" if lesson.lesson_type else ""
    stream = " • 🔗 <b>поток</b>" if lesson.is_stream else ""
    sg = f" • 👥 <b>Подгруппа {lesson.subgroup}</b>" if lesson.subgroup > 0 else ""
    loc = (
        "🌐 Дистанционно"
        if lesson.is_remote
        else f"📍 🏢 {html.escape(lesson.address)} (Каб. {html.escape(lesson.room)})"
    )
    creds = _format_remote_credentials(lesson)

    card = (
        f"▪️ <b>{lesson.period + 1} пара</b> (<code>{lesson.time_str}</code>){sg}{stream}\n"
        f"<b>{subj}</b>{l_type}\n"
        f"🏛 <i>{teacher}</i>\n"
        f"{loc}{creds}"
    )

    return card


def format_minutes(total_minutes: int) -> str:
    """
    Преобразует общее количество минут в человекочитаемую строку часов и минут.

    Форматирует остаток времени (например, '1 ч 20 мин', '45 мин' или '2 ч').
    Используется в статусах оставшегося времени до начала или конца пары.

    Возвращает строку с русскими сокращениями времени.
    """

    hours = total_minutes // 60
    mins = total_minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours} ч {mins} мин"

    if hours > 0:
        return f"{hours} ч"

    return f"{mins} мин"


def _parse_time_interval_minutes(time_str: str) -> tuple[int, int] | None:
    """
    Извлекает границы времени начала и конца пары в минутах от начала суток.

    Использует регулярное выражение для поддержки разделителей ':' и '.'.
    Защищает от сбоев при нестандартном написании времени в расписании.

    Возвращает кортеж (start_min, end_min) или None при ошибке парсинга.
    """

    matches = re.findall(r"(\d{1,2})[:\.](\d{2})", time_str)
    if len(matches) < 2:
        return None

    s_min = int(matches[0][0]) * 60 + int(matches[0][1])
    e_min = int(matches[1][0]) * 60 + int(matches[1][1])

    return s_min, e_min


def _check_single_lesson_status(lesson: Lesson, n_min: int) -> tuple[bool, str]:
    """
    Проверяет статус конкретной пары относительно текущей минуты суток.

    Определяет, идёт ли занятие сейчас или является ближайшим следующим.
    Рассчитывает остаток времени до события и формирует HTML-баннер.

    Возвращает кортеж (найдено_состояние, HTML_баннер).
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


def get_lesson_status_banner(lessons: list[Lesson], target_date: date) -> str:
    """
    Рассчитывает динамический баннер статуса пар для сегодняшнего дня.

    Определяет текущую пару или время до следующей, либо сообщает о завершении пар.
    Для прошедших или будущих дат возвращает пустую строку.

    Возвращает HTML-строку баннера статуса или пустую строку.
    """

    now_dt = datetime.now(TIMEZONE)
    if target_date != now_dt.date() or not lessons:
        return ""

    n_min = now_dt.time().hour * 60 + now_dt.time().minute
    for lesson in lessons:
        found, banner = _check_single_lesson_status(lesson, n_min)
        if found:
            return banner

    return "✅ <b>Все пары на сегодня завершены!</b>\n\n"


def format_day_schedule(target_date: date, lessons: list[Lesson]) -> str:
    """
    Форматирует расписание на конкретный учебный день в итоговый HTML-блок.

    Добавляет заголовок дня, динамический баннер статуса и список карточек пар.
    В случае отсутствия пар выводит дружелюбное сообщение об отдыхе.

    Возвращает готовый HTML-текст расписания для отправки в Telegram.
    """

    weekday_str = WEEKDAYS_RU[target_date.weekday()]
    date_str = target_date.strftime("%d.%m")
    header = f"<b>{GROUP_NAME} • {weekday_str}, {date_str}</b>\n"
    header += get_lesson_status_banner(lessons, target_date)

    if not lessons:
        return header + "<i>Занятий нет — свободный день!</i> ☕️"

    cards = [format_lesson_card(lesson) for lesson in lessons]

    return header + "\n\n".join(cards)


def format_week_lesson_loc(lesson: Lesson) -> str:
    """
    Формирует лаконичную строку локации для недельного дайджеста расписания.

    Определяет корпус (Цветочная или Вознесенский) по подстроке адреса.
    Экранирует номер кабинета для защиты от спецсимволов HTML.

    Возвращает строку с эмодзи локации и корпусом.
    """

    if lesson.is_remote:
        return "🌐 Дистанционно"

    campus = "Вознесенский" if "вознесен" in lesson.address.lower() else "Цветочная"

    return f"📍 Каб. {html.escape(lesson.room)} ({campus})"


def format_week_lesson_card(lesson: Lesson) -> str:
    """
    Формирует компактную цитатную карточку пары для недельного обзора.

    Оборачивает текст в тег blockquote Telegram для аккуратного визуального разделения.
    Экранирует название предмета и ФИО преподавателя.

    Возвращает HTML-текст цитатной карточки пары.
    """

    subj = html.escape(lesson.subject)
    teacher = html.escape(lesson.teacher)
    type_suffix = f" ({html.escape(lesson.lesson_type)})" if lesson.lesson_type else ""
    stream_badge = " • 🔗 поток" if lesson.is_stream else ""
    sg_badge = f" • 👥 {lesson.subgroup} п/г" if lesson.subgroup > 0 else ""
    loc = format_week_lesson_loc(lesson)

    return (
        f"<blockquote>▪️ <b>{lesson.period + 1} пара</b> (<code>{lesson.time_str}</code>){stream_badge}{sg_badge}\n"
        f"<b>{subj}</b>{type_suffix}\n"
        f"🏛 <i>{teacher}</i> • {loc}</blockquote>"
    )


def format_week_day_block(day_date: date, lessons: list[Lesson]) -> str:
    """
    Формирует визуальный блок одного учебного дня для недельного дайджеста.

    Включает дату, день недели и список карточек пар или статус выходного дня.
    Использует блочную разметку для комфортного чтения в мобильном клиенте.

    Возвращает HTML-фрагмент одного учебного дня.
    """

    w_str = WEEKDAYS_RU[day_date.weekday()]
    d_str = day_date.strftime("%d.%m")
    header = f"🗓 <b>{w_str}, {d_str}</b>\n"

    if not lessons:
        return f"{header}<blockquote><i>Занятий нет — свободный день! ☕️</i></blockquote>"

    cards = [format_week_lesson_card(lesson) for lesson in lessons]

    return f"{header}" + "\n".join(cards)


def format_week_schedule(days_data: list[tuple[date, list[Lesson]]]) -> str:
    """
    Формирует полное недельное расписание с пн по сб единым сообщением.

    Объединяет блоки всех учебных дней недели под общим заголовком группы.
    Используется в недельной кнопке бота и веб-интерфейсе.

    Возвращает итоговый HTML-текст расписания на неделю.
    """

    header = f"🎓 <b>РАСПИСАНИЕ НА НЕДЕЛЮ ({GROUP_NAME})</b>\n────────────────────────────\n\n"
    day_blocks = [format_week_day_block(day, day_lessons) for day, day_lessons in days_data]

    return header + "\n\n".join(day_blocks)


def format_reminder_text(lesson: Lesson) -> str:
    """
    Формирует текст персонального напоминания за 10 минут до начала пары.

    Включает предупреждающий заголовок и подробную карточку предстоящего занятия.
    Отправляется подписчикам в личные сообщения бота.

    Возвращает готовый HTML-текст напоминания.
    """

    card = format_lesson_card(lesson)

    return f"⏰ <b>Через 10 минут начинается пара!</b>\n\n{card}"


def format_notice_settings_text(is_subscribed: bool) -> str:
    """
    Формирует информационный текст экрана управления личными уведомлениями.

    Отображает текущий статус подписки пользователя и подсказку о топике группы.
    Используется в диалоге команды /notice.

    Возвращает HTML-текст экрана настроек уведомлений.
    """

    status_icon = "🔔" if is_subscribed else "🔕"
    status_text = "<b>ВКЛЮЧЕНЫ</b>" if is_subscribed else "<b>ОТКЛЮЧЕНЫ</b>"
    desc = (
        "Ты получаешь напоминания в ЛС за 10 минут до начала каждой пары."
        if is_subscribed
        else "Напоминания в ЛС отключены. Ты не получаешь уведомления перед парами."
    )

    return (
        f"⚙️ <b>НАСТРОЙКИ УВЕДОМЛЕНИЙ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Текущий статус:</b> {status_icon} {status_text}\n\n"
        f"<i>{desc}</i>\n\n"
        f"💡 <i>Расписание в общем топике группы обновляется независимо от этих настроек.</i>"
    )
