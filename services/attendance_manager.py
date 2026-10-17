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
# Пауза между retry — даёт WOPI серверу время сбросить кэш блокировок
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

    Устанавливает TTL (SESSION_TTL_SECONDS = 2 часа) для предотвращения
    утечек памяти при брошенных старостой опросах.

    Ничего не возвращает; при недоступности Redis логирует ошибку.
    """
    client = await get_redis()
    if not client:
        log.error("Redis недоступен для сохранения сессии")
        return

    data = session.model_dump_json()
    await client.set(REDIS_SESSION_KEY, data, ex=SESSION_TTL_SECONDS)
    log.info(f"Сессия посещаемости сохранена в Redis (пара {session.lesson_num}, студент {session.current_idx}/{len(session.students)})")


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
        log.warning(f"Активная сессия не найдена по ключу '{REDIS_SESSION_KEY}'")
        return None

    try:
        return AttendanceSession.model_validate_json(data)
    except Exception as e:
        log.error(f"Ошибка десериализации сессии: {e}")
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


async def fetch_target_students(target_date: date) -> list[tuple[int, str]]:
    """
    Возвращает список студентов с кэшированием в Redis для мгновенного отклика.

    Сначала опрашивает локальный кэш Redis (TTL 24 часа). При отсутствии данных
    обращается к WOPI Яндекс Документов и атомарно кэширует результат.

    Возвращает список кортежей [(row_idx, fio)].
    """
    client = await get_redis()

    # === Быстрое чтение из кэша Redis ===
    if client:
        cached = await client.get(REDIS_STUDENTS_CACHE_KEY)
        if cached:
            try:
                return [tuple(x) for x in json.loads(cached)]
            except Exception as e:
                log.debug(f"Сбой десериализации кэша студентов: {e}")

    # === Загрузка из Яндекс Документов и обновление кэша ===
    students = await _fetch_students_from_wopi(target_date)
    if client and students:
        await client.set(REDIS_STUDENTS_CACHE_KEY, json.dumps(students, ensure_ascii=False), ex=STUDENTS_CACHE_TTL_SECONDS)

    return students


async def create_attendance_session(
    target_date: date,
    lesson_num: int,
    lesson_title: str,
    initiator_id: int
) -> AttendanceSession:
    """
    Инициализирует новую сессию опроса посещаемости и фиксирует её в Redis.

    Проверяет отсутствие конфликта инициаторов (чтобы староста и замстаросты
    не перезаписывали сессии друг друга одновременно).

    Возвращает созданную модель AttendanceSession.
    """
    active = await get_active_session()
    if active and active.initiator_id != initiator_id:
        raise PermissionError(f"Сессия уже занята пользователем {active.initiator_id}")

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


async def record_student_mark(mark: str) -> AttendanceSession | None:
    """
    Записывает отметку для текущего студента и сдвигает указатель на следующего.

    Сохраняет выбор старосты ('П', 'О', 'У', 'Н') по индексу строки Excel
    и обновляет сессию в Redis.

    Возвращает обновленную модель AttendanceSession или None, если опрос завершён.
    """
    session = await get_active_session()
    if not session or session.current_idx >= len(session.students):
        return None

    # === Фиксация отметки текущего студента ===
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

    # === Откат указателя и удаление последней отметки ===
    session.current_idx -= 1
    prev_row, _ = session.students[session.current_idx]
    session.marks.pop(str(prev_row), None)

    await save_session_to_redis(session)
    return session


async def mark_all_remaining_present() -> AttendanceSession | None:
    """
    Массово проставляет статус 'П' (присутствует) всем оставшимся студентам.

    Ускоряет опрос в группах с высокой посещаемостью, избавляя старосту
    от многократного нажатия одной кнопки.

    Возвращает завершенную модель AttendanceSession или None при отсутствии сессии.
    """
    session = await get_active_session()
    if not session:
        return None

    # === Пакетная установка отметок присутствия ===
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
    """
    Записывает все собранные отметки сессии в колонку даты в рабочем листе Excel.

    Перебирает словарь marks {'row_idx': 'П'} и вызывает write_student_mark.

    Ничего не возвращает; модифицирует переданный лист openpyxl in-place.
    """
    for row_str, mark in session.marks.items():
        write_student_mark(sheet, int(row_str), col, mark)


async def _prepare_updated_workbook(
    wopi, t_date: date, session: AttendanceSession
):
    """Скачивает книгу и проставляет отметки сессии в колонку пары."""
    wb = await download_workbook(wopi)
    sheet = get_month_sheet(wb, t_date)
    col = find_lesson_column(sheet, t_date, session.lesson_num)
    if not col:
        raise ValueError(f"Не найдена колонка для {t_date} пара {session.lesson_num}")
    apply_marks_to_sheet(sheet, session, col)
    ensure_summary_headers(sheet)
    return wb


async def _try_commit_once(session: AttendanceSession, t_date: date) -> bool:
    """Одна попытка записи: скачать → применить отметки → загрузить → верифицировать."""
    wopi = await init_wopi_session()
    wb = await _prepare_updated_workbook(wopi, t_date, session)
    upload_ok = await upload_workbook(wopi, wb)
    del wb
    gc.collect()
    if not upload_ok:
        return False
    verified = await verify_upload(wopi, t_date, session.lesson_num, session.marks)
    if verified:
        log.info(f"✅ Посещаемость пары {session.lesson_num} подтверждена верификацией")
    else:
        log.warning("⚠️  WOPI PUT успешен (200 OK), но верификация чтения не подтвердила отметки")
    return True


async def _post_commit_sync() -> None:
    """Контрольная сверка реестра с Яндекс Документами после сохранения."""
    try:
        from services.attendance_stats import invalidate_attendance_stats_cache
        from services.attendance_topic_updater import sync_attendance_topic_message
        # 15 сек для сброса OnlyOffice буфера совместного редактирования на диск
        await asyncio.sleep(15)
        await invalidate_attendance_stats_cache()
        await sync_attendance_topic_message(force_refresh=True)
    except Exception as e:
        log.warning(f"Ошибка пост-коммит обновления топика посещаемости: {e}")


async def commit_session_to_table(session: AttendanceSession) -> bool:
    """
    Выгружает все зафиксированные отметки сессии в Яндекс Документы.

    До MAX_COMMIT_RETRIES попыток с пересозданием WOPI-сессии.
    После подтвержденного сохранения сбрасывает сессию и обновляет топик.
    """
    t_date = date.fromisoformat(session.target_date)
    for attempt in range(1, MAX_COMMIT_RETRIES + 1):
        log.info(f"Запись посещаемости пары {session.lesson_num} (попытка {attempt}/{MAX_COMMIT_RETRIES})...")
        try:
            if await _try_commit_once(session, t_date):
                log.info(f"✅ Посещаемость пары {session.lesson_num} зафиксирована")
                await clear_session()
                asyncio.create_task(_post_commit_sync())
                return True
        except Exception as e:
            log.error(f"Попытка {attempt} провалилась: {type(e).__name__}: {e}")
        if attempt < MAX_COMMIT_RETRIES:
            log.info(f"Повтор через {RETRY_DELAY_SECONDS} сек...")
            await asyncio.sleep(RETRY_DELAY_SECONDS)
    log.error(f"❌ Все {MAX_COMMIT_RETRIES} попытки записи пары {session.lesson_num} провалились")
    return False


def calculate_summary_stats(marks: dict[str, str]) -> dict[str, int]:
    """Подсчитывает итоговые количества отметок по категориям (П, О, У, Н)."""
    stats = {"П": 0, "О": 0, "У": 0, "Н": 0}
    for m in marks.values():
        if m in stats:
            stats[m] += 1
    return stats
