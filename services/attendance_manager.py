"""
Менеджер интерактивной сессии отметки посещаемости.

Управляет состоянием опроса старосты в Redis:
  1. Создаёт сессию при начале опроса пары
  2. Фиксирует выбор статусов студентов (П, О, У, Н)
  3. Поддерживает шаг назад и пакетную отметку оставшихся (П)
  4. Сохраняет итоговые данные в Яндекс Документы через yandex_docs
"""

import json
from datetime import date
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from core.logger import get_logger
from core.redis import get_redis
from services.yandex_docs import (
    download_workbook, find_lesson_column, get_month_sheet,
    get_students_list, init_wopi_session, upload_workbook, write_student_mark
)

log = get_logger("attendance_manager")
REDIS_SESSION_KEY = "attendance:session"
SESSION_TTL_SECONDS = 7200  # 2 часа


class AttendanceSession(BaseModel):
    """Модель активной сессии отметки посещаемости пары."""
    target_date: str
    lesson_num: int
    lesson_title: str
    students: List[Tuple[int, str]]  # [(row_idx, fio)]
    marks: Dict[str, str] = Field(default_factory=dict)  # {"row_idx": "П"}
    current_idx: int = 0
    initiator_id: int
    msg_id: Optional[int] = None


async def save_session_to_redis(session: AttendanceSession) -> None:
    """Сохраняет состояние сессии в Redis с установленным TTL."""
    client = await get_redis()
    if not client:
        log.error("Redis недоступен для сохранения сессии")
        return
    data = session.model_dump_json()
    await client.set(REDIS_SESSION_KEY, data, ex=SESSION_TTL_SECONDS)
    log.info(f"Сессия посещаемости сохранена в Redis (пара {session.lesson_num}, студент {session.current_idx}/{len(session.students)})")


async def get_active_session() -> Optional[AttendanceSession]:
    """Извлекает активную сессию посещаемости из Redis."""
    client = await get_redis()
    if not client:
        log.error("Redis недоступен для чтения сессии")
        return None
    data = await client.get(REDIS_SESSION_KEY)
    if not data:
        log.warning(f"Активная сессия не найдена по ключу '{REDIS_SESSION_KEY}'")
        return None
    try:
        return AttendanceSession.model_validate_json(data)
    except Exception as e:
        log.error(f"Ошибка десериализации сессии: {e}")
        return None


async def clear_session() -> None:
    """Удаляет активную сессию посещаемости из Redis."""
    client = await get_redis()
    if client:
        await client.delete(REDIS_SESSION_KEY)
        log.info("Сессия посещаемости сброшена в Redis")


async def fetch_target_students(target_date: date) -> List[Tuple[int, str]]:
    """Скачивает таблицу и извлекает список студентов на указанную дату."""
    wopi = await init_wopi_session()
    wb = await download_workbook(wopi)
    sheet = get_month_sheet(wb, target_date)
    students = get_students_list(sheet)
    if not students:
        raise ValueError("В таблице не найдено ни одного студента")
    return students


async def create_attendance_session(
    target_date: date,
    lesson_num: int,
    lesson_title: str,
    initiator_id: int
) -> AttendanceSession:
    """Инициализирует новую сессию опроса и сохраняет в Redis."""
    students = await fetch_target_students(target_date)
    session = AttendanceSession(
        target_date=target_date.isoformat(),
        lesson_num=lesson_num,
        lesson_title=lesson_title,
        students=students,
        initiator_id=initiator_id
    )
    await save_session_to_redis(session)
    log.info(f"Создана сессия для пары {lesson_num} ({len(students)} студентов)")
    return session


async def record_student_mark(mark: str) -> Optional[AttendanceSession]:
    """
    Записывает отметку для текущего студента и сдвигает указатель на следующего.

    Возвращает обновленную сессию или None, если сессия не найдена.
    """
    session = await get_active_session()
    if not session or session.current_idx >= len(session.students):
        return None
    row_idx, _ = session.students[session.current_idx]
    session.marks[str(row_idx)] = mark
    session.current_idx += 1
    await save_session_to_redis(session)
    return session


async def step_back() -> Optional[AttendanceSession]:
    """
    Возвращает сессию на шаг назад для исправления предыдущей отметки.

    Уменьшает индекс текущего студента на 1, если он больше 0.
    """
    session = await get_active_session()
    if not session or session.current_idx == 0:
        return session
    session.current_idx -= 1
    prev_row, _ = session.students[session.current_idx]
    session.marks.pop(str(prev_row), None)
    await save_session_to_redis(session)
    return session


async def mark_all_remaining_present() -> Optional[AttendanceSession]:
    """
    Массово проставляет отметку 'П' всем оставшимся студентам.

    Устанавливает указатель в конец списка для перехода к сохранению.
    """
    session = await get_active_session()
    if not session:
        return None
    for idx in range(session.current_idx, len(session.students)):
        row_idx, _ = session.students[idx]
        session.marks[str(row_idx)] = "П"
    session.current_idx = len(session.students)
    await save_session_to_redis(session)
    log.info(f"Оставшиеся студенты отмечены как 'П' (всего {len(session.marks)})")
    return session


def ensure_summary_headers(sheet) -> None:
    """
    Гарантирует сохранение текстовых заголовков и кодов в сводных колонках.

    Предотвращает сброс формул кросс-листовых ссылок в пустые строки openpyxl.
    """
    mc = sheet.max_column
    if mc < 4:
        return
    sheet.cell(2, mc - 2, "Опоздавшие")
    sheet.cell(3, mc - 2, "О")
    sheet.cell(2, mc - 1, "отсутствие по уважительной причине")
    sheet.cell(3, mc - 1, "У")
    sheet.cell(2, mc, "отсутствие по неуважительной причине")
    sheet.cell(3, mc, "Н")


def apply_marks_to_sheet(sheet, session: AttendanceSession, col: int) -> None:
    """Применяет все собранные отметки сессии к рабочему листу openpyxl."""
    for row_str, mark in session.marks.items():
        write_student_mark(sheet, int(row_str), col, mark)


async def commit_session_to_table(session: AttendanceSession) -> bool:
    """
    Выгружает все зафиксированные отметки сессии в Яндекс Документы.

    Возвращает True в случае успешной записи и сбрасывает сессию.
    """
    log.info(f"Запись посещаемости пары {session.lesson_num} в таблицу...")
    wopi = await init_wopi_session()
    wb = await download_workbook(wopi)
    t_date = date.fromisoformat(session.target_date)
    sheet = get_month_sheet(wb, t_date)
    col = find_lesson_column(sheet, t_date, session.lesson_num)
    if not col:
        raise ValueError(f"Не найдена колонка для {t_date} пара {session.lesson_num}")
    apply_marks_to_sheet(sheet, session, col)
    ensure_summary_headers(sheet)
    success = await upload_workbook(wopi, wb)
    if success:
        await clear_session()
    return success


def calculate_summary_stats(marks: Dict[str, str]) -> Dict[str, int]:
    """Подсчитывает итоговые количества отметок по категориям (П, О, У, Н)."""
    stats = {"П": 0, "О": 0, "У": 0, "Н": 0}
    for m in marks.values():
        if m in stats:
            stats[m] += 1
    return stats
