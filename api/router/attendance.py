"""
Роутер посещаемости — GET /attendance/stats, student, session, mark, commit.

Предоставляет аналитику пропусков и управление сессией отметки старосты.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.attendance import (
    ActiveSessionResponse,
    AttendanceStatsResponse,
    CommitAttendanceResponse,
    MarkStudentRequest,
    StartSessionRequest,
    StudentPersonalStatsResponse,
    StudentStatItem,
)
from services.attendance_manager import (
    clear_session,
    commit_session_to_table,
    create_attendance_session,
    get_active_session,
    mark_all_remaining_present,
    record_student_mark,
)
from services.attendance_stats import (
    fetch_all_time_attendance,
    find_student_attendance,
)

router = APIRouter(tags=["Attendance"], prefix="/attendance", dependencies=[Depends(verify_api_or_tester)])


@router.get("/stats", response_model=AttendanceStatsResponse)
async def get_attendance_stats(force_refresh: bool = Query(default=False)) -> AttendanceStatsResponse:
    """
    Возвращает агрегированную годовую статистику посещаемости всех студентов.

    Считывает данные журнала из онлайн-таблицы Яндекс Документов.
    Использует кэширование в Redis для ускорения повторных запросов.

    Возвращает AttendanceStatsResponse со списком статистики по каждому студенту.
    """

    data = await fetch_all_time_attendance(force_refresh=force_refresh)
    items = [StudentStatItem(fio=v["fio"], total=v["total"], months=v.get("months", {})) for v in data.values()]

    return AttendanceStatsResponse(count=len(items), students=items)


def _calculate_attendance_rate(total_marks: dict) -> float:
    """
    Вычисляет процент посещаемости студента по сумме меток 'П' и 'О'.

    Считает сумму всех отметок (П, О, У, Н) и делит присутствие на общее число.
    Защищает от деления на 0 при отсутствии отметок, возвращая 100.0%.

    Возвращает процент посещаемости от 0.0 до 100.0.
    """

    p = total_marks.get("П", 0)
    o = total_marks.get("О", 0)
    total = p + o + total_marks.get("У", 0) + total_marks.get("Н", 0)

    return round((p + o) / total * 100, 1) if total > 0 else 100.0


@router.get("/student/{fio}", response_model=StudentPersonalStatsResponse)
async def get_student_attendance(fio: str) -> StudentPersonalStatsResponse:
    """
    Возвращает детальную статистику посещаемости конкретного студента по ФИО.

    Ищет запись в агрегированной сводке и рассчитывает итоговый процент посещаемости.
    Выбрасывает HTTP 404, если студент не найден в журнале.

    Возвращает StudentPersonalStatsResponse с помесячной и суммарной аналитикой.
    """

    data = await fetch_all_time_attendance(force_refresh=False)
    stat = find_student_attendance(data, fio)
    if not stat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student attendance not found")

    tot = stat.get("total", {})
    pct = _calculate_attendance_rate(tot)

    return StudentPersonalStatsResponse(
        fio=stat["fio"],
        total=tot,
        attendance_rate_percent=pct,
        months=stat.get("months", {}),
    )


def _build_session_response(s) -> ActiveSessionResponse:
    """
    Преобразует состояние доменной сессии старосты в Pydantic DTO ответа.

    Извлекает имя текущего студента по индексу очереди опроса.
    Корректно обрабатывает пустые или завершённые сессии (is_active=False).

    Возвращает сформированный объект ActiveSessionResponse.
    """

    if not s:
        return ActiveSessionResponse(is_active=False)

    cur_name = s.students[s.current_idx][1] if s.current_idx < len(s.students) else None

    return ActiveSessionResponse(
        is_active=True,
        target_date=s.target_date,
        lesson_num=s.lesson_num,
        lesson_title=s.lesson_title,
        current_idx=s.current_idx,
        total_students=len(s.students),
        current_student=cur_name,
        marks=s.marks,
    )


@router.get("/session", response_model=ActiveSessionResponse)
async def get_current_session() -> ActiveSessionResponse:
    """
    Возвращает текущее состояние интерактивной сессии отметки старосты.

    Считывает состояние сессии из постоянного хранилища Redis.
    Используется интерфейсом Telegram Mini App для синхронизации кнопок отметки.

    Возвращает ActiveSessionResponse с данными активной сессии.
    """

    session = await get_active_session()

    return _build_session_response(session)


@router.post("/session/start", response_model=ActiveSessionResponse, dependencies=[Depends(verify_admin_access)])
async def start_session(payload: StartSessionRequest) -> ActiveSessionResponse:
    """
    Инициализирует новую сессию опроса посещаемости пары старостой (Admin only).

    Загружает актуальный список студентов группы и обнуляет промежуточные метки.
    Выбрасывает HTTP 400 в случае ошибки парсинга или пустого списка студентов.

    Возвращает ActiveSessionResponse с инициализированным состоянием.
    """

    t_date = date.fromisoformat(payload.target_date)
    session = await create_attendance_session(t_date, payload.lesson_num, payload.lesson_title, initiator_id=0)
    if not session:
        raise HTTPException(status_code=400, detail="Failed to create session (empty students or error)")

    return _build_session_response(session)


@router.post("/session/mark", response_model=ActiveSessionResponse, dependencies=[Depends(verify_admin_access)])
async def mark_student(payload: MarkStudentRequest) -> ActiveSessionResponse:
    """
    Записывает статус посещаемости для текущего студента в очереди (Admin only).

    Поддерживает валидные статусы 'П', 'О', 'У', 'Н' и продвигает указатель дальше.
    Выбрасывает HTTP 400, если активная сессия опроса отсутствует.

    Возвращает обновлённый ActiveSessionResponse.
    """

    session = await record_student_mark(payload.mark)
    if not session:
        raise HTTPException(status_code=400, detail="No active session to mark")

    return _build_session_response(session)


@router.post(
    "/session/batch_present", response_model=ActiveSessionResponse, dependencies=[Depends(verify_admin_access)]
)
async def batch_present() -> ActiveSessionResponse:
    """
    Массово проставляет статус 'П' (присутствует) всем оставшимся студентам (Admin only).

    Ускоряет завершение опроса старостой, когда все оставшиеся на паре.
    Выбрасывает HTTP 400, если активная сессия отсутствует.

    Возвращает ActiveSessionResponse с заполненными отметками.
    """

    session = await mark_all_remaining_present()
    if not session:
        raise HTTPException(status_code=400, detail="No active session")

    return _build_session_response(session)


@router.post("/session/commit", response_model=CommitAttendanceResponse, dependencies=[Depends(verify_admin_access)])
async def commit_session() -> CommitAttendanceResponse:
    """
    Фиксирует результаты сессии опроса в таблицу Яндекс Документов (Admin only).

    Отправляет пакет изменений в онлайн-таблицу через API Яндекс Документов.
    Выбрасывает HTTP 400/500 при отсутствии сессии или сетевых сбоях.

    Возвращает CommitAttendanceResponse с числом записанных отметок.
    """

    session = await get_active_session()
    if not session:
        raise HTTPException(status_code=400, detail="No active session to commit")

    count = len(session.marks)
    ok = await commit_session_to_table(session)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to commit marks to Yandex Docs")

    return CommitAttendanceResponse(status="ok", message="Marks saved to Yandex Docs", marks_committed=count)


@router.delete("/session", dependencies=[Depends(verify_admin_access)])
async def cancel_session() -> dict:
    """
    Сбрасывает и отменяет текущую незавершённую сессию старосты (Admin only).

    Очищает ключ сессии в Redis без сохранения данных в Яндекс Таблицу.
    Защищён verify_admin_access.

    Возвращает словарь подтверждения сброса сессии.
    """

    await clear_session()

    return {"status": "ok", "message": "Attendance session cleared"}
