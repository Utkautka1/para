"""
Чистые правила событийных ачивок: какое действие в какое время что открывает.

Хэндлеры бота передают сюда «что открыл пользователь» (вид расписания,
задание ДЗ, сообщение в чате) и текущее московское время, а получают набор id.
Сама выдача и счётчики — в achievement_events, здесь нет ни БД, ни Redis:
так каждое условие из описаний ачивок проверяется unit-тестом на фиксированном времени.

Виды расписания (ScheduleView):
  today     — /start, /today, «Сегодня», «Обновить»: только здесь есть пары
              СЕГОДНЯШНЕГО дня, поэтому «во время пары», «форточка» и «перемена»
              проверяются лишь для него
  tomorrow  — «Завтра»
  week      — «Эта неделя»
  week_next — «Следующая неделя»
"""

import re
from dataclasses import dataclass
from datetime import datetime, time
from enum import StrEnum
from itertools import pairwise
from pathlib import PurePath

from services.models import Lesson

# Перерыв между парами длиннее часа — это уже «форточка» (пропущенный слот пары),
# а не обычная перемена (10–25 минут по сетке КТМУ)
WINDOW_GAP_MINUTES = 60

# Длина промпта (символы), с которой задание считается подробным
DETAILED_PROMPT_CHARS = 200

# Расширения файлов, которые считаются кодом для «Чистого кода»
CODE_EXTENSIONS = frozenset(
    {".py", ".ipynb", ".c", ".h", ".cpp", ".hpp", ".cs", ".java", ".kt", ".js", ".ts", ".go", ".rs", ".php", ".rb"}
    | {".pas", ".swift", ".sql", ".sh"}
)

# «8:30–9:55», «08:30 - 09:55» — время начала и конца пары в любом из форматов сетки
_TIME_RANGE_RE = re.compile(r"(\d{1,2}):(\d{2})\D+(\d{1,2}):(\d{2})")

# Поздравление с днём рождения в свободной форме: «с днём рождения», «с др», «с днюхой»
BIRTHDAY_GREETING_RE = re.compile(r"\bс\s+(дн[её]м\s+рожд|др\b|днюх|днюшк)|happy\s+birthday", re.IGNORECASE)


class ScheduleView(StrEnum):
    """Какой вид расписания открыл пользователь."""

    TODAY = "today"
    TOMORROW = "tomorrow"
    WEEK = "week"
    WEEK_NEXT = "week_next"


def parse_lesson_slot(time_str: str) -> tuple[time, time] | None:
    """
    Разбирает строку времени пары в (начало, конец).

    Возвращает кортеж времени или None, если формат не распознан.
    """
    m = _TIME_RANGE_RE.search(time_str or "")
    if not m:
        return None
    h1, m1, h2, m2 = (int(x) for x in m.groups())
    if max(h1, h2) > 23 or max(m1, m2) > 59:
        return None
    return time(h1, m1), time(h2, m2)


def _day_slots(lessons: list[Lesson]) -> list[tuple[time, time]]:
    """Возвращает уникальные слоты пар дня по возрастанию (подгруппы дают дубли)."""
    slots = {slot for lesson in lessons if (slot := parse_lesson_slot(lesson.time_str))}
    return sorted(slots)


def _minutes(t: time) -> int:
    """Переводит время суток в минуты от полуночи."""
    return t.hour * 60 + t.minute


def lesson_moment_achievements(now: time, lessons: list[Lesson]) -> set[str]:
    """
    Проверяет, попал ли момент на пару, перемену или «форточку» сегодняшнего дня.

    Возвращает множество id: time_second_shift / egg_tea_break / life_window_chill.
    """
    slots = _day_slots(lessons)
    if any(start <= now < end for start, end in slots):
        return {"time_second_shift"}
    for (_, prev_end), (next_start, _) in pairwise(slots):
        if prev_end <= now < next_start:
            gap = _minutes(next_start) - _minutes(prev_end)
            return {"life_window_chill" if gap >= WINDOW_GAP_MINUTES else "egg_tea_break"}
    return set()


def time_of_day_achievements(now: datetime) -> set[str]:
    """Ачивки «открыл расписание в такое-то время», общие для всех видов."""
    result: set[str] = set()
    if now.hour < 8:
        result.add("time_early_bird")
    if 3 <= now.hour < 5:
        result.add("egg_insomnia")
    if now.weekday() == 0 and now.time() < time(8, 30):
        result.add("life_monday")
    return result


def _view_specific(view: ScheduleView, now: datetime) -> set[str]:
    """Ачивки, которые зависят от конкретной кнопки расписания."""
    weekday, hour = now.weekday(), now.hour
    checks: dict[ScheduleView, dict[str, bool]] = {
        ScheduleView.TOMORROW: {
            "bot_future_peek": True,
            "time_night_owl": hour >= 21 or hour < 5,
            # В воскресенье «Завтра» — это пары понедельника
            "time_sunday_scout": weekday == 6,
        },
        ScheduleView.WEEK_NEXT: {
            "bot_week_next": True,
            "time_sunday_scout": weekday >= 5,
            "life_friday": weekday == 4 and hour >= 15,
        },
        ScheduleView.WEEK: {"life_week_plan": True},
    }
    return {aid for aid, ok in checks.get(view, {}).items() if ok}


def schedule_view_achievements(view: ScheduleView, now: datetime, lessons: list[Lesson]) -> set[str]:
    """
    Собирает все ачивки за просмотр расписания.

    lessons — пары показанного дня (для недельных видов — пустой список).

    Возвращает множество id.
    """
    result = time_of_day_achievements(now) | _view_specific(view, now)
    if view is ScheduleView.TODAY:
        result |= lesson_moment_achievements(now.time(), lessons)
    if view in (ScheduleView.TODAY, ScheduleView.TOMORROW) and any(lesson.is_remote for lesson in lessons):
        result.add("life_remote")
    return result


@dataclass(frozen=True)
class HomeworkTask:
    """Что студент отправил в топик ДЗ — ровно то, что нужно ачивкам."""

    prompt: str
    # kind — формат задания: 'text', 'photo' или 'document'
    kind: str
    file_name: str | None
    # is_followup — уточнение реплаем на собственное задание
    is_followup: bool


def homework_kind(mime_type: str | None, has_file: bool) -> str:
    """Определяет формат задания по MIME-типу вложения."""
    if not has_file:
        return "text"
    return "photo" if (mime_type or "").startswith("image/") else "document"


def homework_achievements(task: HomeworkTask, now: datetime) -> set[str]:
    """
    Ачивки, которые даёт одно задание ДЗ независимо от истории студента.

    Счётчики (3/10 заданий, 5 дней, 3 формата) считает achievement_events.

    Возвращает множество id.
    """
    checks = {
        "ai_first_task": True,
        "ai_prompt_pro": len(task.prompt.strip()) >= DETAILED_PROMPT_CHARS,
        "ai_photo": task.kind == "photo",
        "ai_followup": task.is_followup,
        "ai_night_grind": now.hour >= 22 or now.hour < 6,
        "ai_clean_code": PurePath(task.file_name or "").suffix.lower() in CODE_EXTENSIONS,
    }
    return {aid for aid, ok in checks.items() if ok}
