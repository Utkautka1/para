"""
Менеджер интерактивной сессии отметки посещаемости.

Управляет состоянием опроса старосты в Redis:
  1. Создаёт сессию при начале опроса пары
  2. Фиксирует выбор статусов студентов (П, О, У, Н)
  3. Поддерживает шаг назад и пакетную отметку оставшихся (П)
  4. Сохраняет итоговые данные в Яндекс Документы через yandex_docs
"""

import asyncio
import gc
import json
from datetime import date

from pydantic import BaseModel, Field

from config import (
    ATTENDANCE_COMMIT_RETRY_DELAY_SECONDS,
    ATTENDANCE_MAX_COMMIT_RETRIES,
    ATTENDANCE_REDIS_SESSION_KEY,
    ATTENDANCE_SESSION_TTL_SECONDS,
    REDIS_STUDENTS_CACHE_KEY,
    STUDENTS_CACHE_TTL_SECONDS,
)
from core.background import spawn
from core.logger import get_logger
from core.redis import get_redis
from integrations.yandex_docs import (
    download_workbook,
    find_lesson_column,
    get_month_sheet,
    get_students_list,
    init_wopi_session,
    upload_workbook,
    verify_upload,
    write_student_mark,
)

log = get_logger("attendance_manager")
REDIS_SESSION_KEY = ATTENDANCE_REDIS_SESSION_KEY
SESSION_TTL_SECONDS = ATTENDANCE_SESSION_TTL_SECONDS
MAX_COMMIT_RETRIES = ATTENDANCE_MAX_COMMIT_RETRIES
RETRY_DELAY_SECONDS = ATTENDANCE_COMMIT_RETRY_DELAY_SECONDS


class AttendanceSession(BaseModel):
    """Модель активной сессии отметки посещаемости пары."""

    target_date: str
    lesson_num: int
    lesson_title: str
    students: list[tuple[int, str]]  # [(row_idx, fio)]
    marks: dict[str, str] = Field(default_factory=dict)  # {"row_idx": "П"}
    current_idx: int = 0
    initiator_id: int
    msg_id: int | None = None


async def save_session_to_redis(session: AttendanceSession) -> None:
    """
    Сериализует и сохраняет состояние активной сессии опроса в Redis.

    Устанавливает TTL (SESSION_TTL_SECONDS) для предотвращения утечек памяти.

    Ничего не возвращает; при недоступности Redis логирует ошибку.
    """
    client = await get_redis()
    if not client:
        log.error("Redis недоступен для сохранения сессии")
        return

    data = session.model_dump_json()
    await client.set(REDIS_SESSION_KEY, data, ex=SESSION_TTL_SECONDS)
    log.info(
        "Сессия посещаемости сохранена в Redis (пара %s, студент %s/%s)",
        session.lesson_num,
        session.current_idx,
        len(session.students),
    )


async def get_active_session() -> AttendanceSession | None:
    """
    Считывает и десериализует активную сессию опроса из Redis.

    Используется клавиатурами и хэндлерами для пошагового продвижения опроса.

    Возвращает экземпляр AttendanceSession или None, если сессия отсутствует/битая.
    """
    client = await get_redis()
    if not client:
        log.error("Redis недоступен для чтения сессии")
        return None

    data = await client.get(REDIS_SESSION_KEY)
    if not data:
        log.warning("Активная сессия не найдена по ключу '%s'", REDIS_SESSION_KEY)
        return None

    try:
        return AttendanceSession.model_validate_json(data)
    except Exception as e:
        log.error("Ошибка десериализации сессии: %s", e)
        return None


async def clear_session() -> None:
    """
    Удаляет активную сессию опроса посещаемости из Redis.

    Вызывается после успешного коммита в Яндекс Документы или при сбросе.

    Ничего не возвращает.
    """
    client = await get_redis()
    if client:
        await client.delete(REDIS_SESSION_KEY)
        log.info("Сессия посещаемости сброшена в Redis")


async def _fetch_students_from_wopi(target_date: date) -> list[tuple[int, str]]:
    """
    Скачивает таблицу через WOPI протокол и считывает список студентов.

    Используется как fallback при промахе кэша Redis для первичной загрузки.

    Возвращает список пар (индекс строки в Excel, ФИО студента).
    """
    wopi = await init_wopi_session()
    wb = await download_workbook(wopi)
    sheet = get_month_sheet(wb, target_date)
    students = get_students_list(sheet)

    if not students:
        raise ValueError("В таблице не найдено ни одного студента")

    return students


async def _read_cached_students(client) -> list[tuple[int, str]] | None:
    """
    Считывает список студентов из кэша Redis.

    Возвращает список кортежей (row_idx, fio) или None при промахе.
    """
    if not client:
        return None

    cached = await client.get(REDIS_STUDENTS_CACHE_KEY)
    if cached:
        try:
            return [tuple(x) for x in json.loads(cached)]
        except Exception as e:
            log.debug("Сбой десериализации кэша студентов: %s", e)

    return None


async def fetch_target_students(target_date: date) -> list[tuple[int, str]]:
    """
    Возвращает список студентов с кэшированием в Redis для мгновенного отклика.

    Сначала опрашивает кэш Redis (24 ч), при промахе обращается к WOPI таблице.

    Возвращает список кортежей [(row_idx, fio)].
    """
    client = await get_redis()
    cached_students = await _read_cached_students(client)

    if cached_students:
        return cached_students

    students = await _fetch_students_from_wopi(target_date)
    if client and students:
        payload = json.dumps(students, ensure_ascii=False)
        await client.set(REDIS_STUDENTS_CACHE_KEY, payload, ex=STUDENTS_CACHE_TTL_SECONDS)

    return students


async def _assert_no_initiator_conflict(initiator_id: int) -> None:
    """
    Проверяет отсутствие конфликта параллельных инициаторов опроса.

    Возбуждает PermissionError при попытке перехватить чужую активную сессию.
    """
    active = await get_active_session()
    if active and active.initiator_id != initiator_id:
        raise PermissionError(f"Сессия уже занята пользователем {active.initiator_id}")


async def create_attendance_session(
    target_date: date, lesson_num: int, lesson_title: str, initiator_id: int
) -> AttendanceSession:
    """
    Инициализирует новую сессию опроса посещаемости и фиксирует её в Redis.

    Проверяет отсутствие конфликта параллельных инициаторов старостата.

    Возвращает созданную модель AttendanceSession.
    """
    await _assert_no_initiator_conflict(initiator_id)

    students = await fetch_target_students(target_date)
    session = AttendanceSession(
        target_date=target_date.isoformat(),
        lesson_num=lesson_num,
        lesson_title=lesson_title,
        students=students,
        initiator_id=initiator_id,
    )

    await save_session_to_redis(session)
    log.info("Создана сессия для пары %s (%s студентов)", lesson_num, len(students))

    return session


async def record_student_mark(mark: str) -> AttendanceSession | None:
    """
    Записывает отметку для текущего студента и сдвигает указатель на следующего.

    Сохраняет выбор старосты ('П', 'О', 'У', 'Н') и обновляет сессию в Redis.

    Возвращает обновленную модель AttendanceSession или None, если опрос завершён.
    """
    session = await get_active_session()
    if not session or session.current_idx >= len(session.students):
        return None

    row_idx, _ = session.students[session.current_idx]
    session.marks[str(row_idx)] = mark
    session.current_idx += 1

    await save_session_to_redis(session)
    return session


async def step_back() -> AttendanceSession | None:
    """
    Возвращает опрос на один шаг назад для исправления ошибочной отметки.

    Уменьшает указатель current_idx и удаляет последнюю поставленную отметку.

    Возвращает обновленную модель AttendanceSession или текущую сессию.
    """
    session = await get_active_session()
    if not session or session.current_idx == 0:
        return session

    session.current_idx -= 1
    prev_row, _ = session.students[session.current_idx]
    session.marks.pop(str(prev_row), None)

    await save_session_to_redis(session)
    return session


async def mark_all_remaining_present() -> AttendanceSession | None:
    """
    Массово проставляет статус 'П' (присутствует) всем оставшимся студентам.

    Ускоряет опрос в группах с высокой явкой, избавляя от повторных кликов.

    Возвращает завершенную модель AttendanceSession или None при отсутствии сессии.
    """
    session = await get_active_session()
    if not session:
        return None

    for idx in range(session.current_idx, len(session.students)):
        row_idx, _ = session.students[idx]
        session.marks[str(row_idx)] = "П"

    session.current_idx = len(session.students)
    await save_session_to_redis(session)
    log.info("Оставшиеся студенты отмечены как 'П' (всего %s)", len(session.marks))

    return session


def ensure_summary_headers(sheet) -> None:
    """
    Гарантирует сохранение текстовых заголовков и кодов в сводных колонках.

    Защищает от сброса формул и метаданных сводной ведомости в Excel.

    Ничего не возвращает; модифицирует переданный лист openpyxl in-place.
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
    """
    Записывает все собранные отметки сессии в колонку даты в рабочем листе Excel.

    Перебирает словарь marks {'row_idx': 'П'} и вызывает write_student_mark.

    Ничего не возвращает; модифицирует переданный лист openpyxl in-place.
    """
    for row_str, mark in session.marks.items():
        write_student_mark(sheet, int(row_str), col, mark)


async def _prepare_updated_workbook(
    wopi,
    t_date: date,
    session: AttendanceSession,
):
    """
    Скачивает книгу и проставляет отметки сессии в колонку пары.

    Возвращает модифицированный объект openpyxl.Workbook.
    """
    wb = await download_workbook(wopi)
    sheet = get_month_sheet(wb, t_date)
    col = find_lesson_column(sheet, t_date, session.lesson_num)

    if not col:
        raise ValueError(f"Не найдена колонка для {t_date} пара {session.lesson_num}")

    apply_marks_to_sheet(sheet, session, col)
    ensure_summary_headers(sheet)

    return wb


async def _try_commit_once(session: AttendanceSession, t_date: date) -> bool:
    """
    Выполняет одну итерацию сохранения: скачать -> применить -> залить -> проверить.

    Возвращает True в случае успешной верификации сохранения, иначе False.
    """
    wopi = await init_wopi_session()
    wb = await _prepare_updated_workbook(wopi, t_date, session)
    upload_ok = await upload_workbook(wopi, wb)

    del wb
    gc.collect()

    if not upload_ok:
        return False

    verified = await verify_upload(wopi, t_date, session.lesson_num, session.marks)
    if verified:
        log.info("✅ Посещаемость пары %s подтверждена верификацией", session.lesson_num)
    else:
        log.warning("⚠️  WOPI PUT успешен (200 OK), но верификация чтения не подтвердила отметки")

    return True


async def _post_commit_sync() -> None:
    """
    Выполняет контрольную сверку реестра с Яндекс Документами после сохранения.

    Ожидает сброс буфера OnlyOffice на диск, сбрасывает кэш и обновляет топик.

    Ничего не возвращает.
    """
    try:
        from services.attendance_stats import invalidate_attendance_stats_cache
        from services.attendance_topic_updater import sync_attendance_topic_message

        # Пауза 15 сек для сброса OnlyOffice буфера совместного редактирования на диск
        await asyncio.sleep(15)
        await invalidate_attendance_stats_cache()
        await sync_attendance_topic_message(force_refresh=True)
    except Exception as e:
        log.warning("Ошибка пост-коммит обновления топика посещаемости: %s", e)


async def _execute_commit_attempts(session: AttendanceSession, t_date: date) -> bool:
    """
    Выполняет цикл повторных попыток выгрузки журнала с экспоненциальной паузой.

    Возвращает True в случае успеха любой из попыток, иначе False.
    """
    for attempt in range(1, MAX_COMMIT_RETRIES + 1):
        log.info("Запись посещаемости пары %s (попытка %s/%s)...", session.lesson_num, attempt, MAX_COMMIT_RETRIES)
        try:
            if await _try_commit_once(session, t_date):
                return True
        except Exception as e:
            log.error("Попытка %s провалилась: %s: %s", attempt, type(e).__name__, e)

        if attempt < MAX_COMMIT_RETRIES:
            log.info("Повтор через %s сек...", RETRY_DELAY_SECONDS)
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    return False


async def commit_session_to_table(session: AttendanceSession) -> bool:
    """
    Выгружает все зафиксированные отметки сессии в Яндекс Документы.

    Выполняет до MAX_COMMIT_RETRIES попыток, очищает сессию и инициирует пост-синк.

    Возвращает True при успешной фиксации данных, иначе False.
    """
    t_date = date.fromisoformat(session.target_date)
    success = await _execute_commit_attempts(session, t_date)

    if success:
        log.info("✅ Посещаемость пары %s зафиксирована", session.lesson_num)
        await clear_session()
        spawn(_post_commit_sync())
        return True

    log.error("❌ Все %s попытки записи пары %s провалились", MAX_COMMIT_RETRIES, session.lesson_num)
    return False


def calculate_summary_stats(marks: dict[str, str]) -> dict[str, int]:
    """
    Подсчитывает итоговые количества отметок по категориям (П, О, У, Н).

    Используется для итоговой сводки перед подтверждением старостой.

    Возвращает словарь счетчиков {'П': int, 'О': int, 'У': int, 'Н': int}.
    """
    stats = {"П": 0, "О": 0, "У": 0, "Н": 0}

    for m in marks.values():
        if m in stats:
            stats[m] += 1

    return stats
