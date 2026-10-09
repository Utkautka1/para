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
    """Агрегированная сводка посещаемости группы за весь учебный год."""
    data = await fetch_all_time_attendance(force_refresh=force_refresh)
    items = [StudentStatItem(fio=v["fio"], total=v["total"], months=v.get("months", {})) for v in data.values()]
    return AttendanceStatsResponse(count=len(items), students=items)


@router.get("/student/{fio}", response_model=StudentPersonalStatsResponse)
async def get_student_attendance(fio: str) -> StudentPersonalStatsResponse:
    """Персональная аналитика посещаемости по ФИО студента."""
    data = await fetch_all_time_attendance(force_refresh=False)
    stat = find_student_attendance(data, fio)
    if not stat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student attendance not found")
    tot = stat.get("total", {})
    p, o, u, n = tot.get("П", 0), tot.get("О", 0), tot.get("У", 0), tot.get("Н", 0)
    all_lessons = p + o + u + n
    pct = round((p + o) / all_lessons * 100, 1) if all_lessons > 0 else 100.0
    return StudentPersonalStatsResponse(fio=stat["fio"], total=tot, attendance_rate_percent=pct, months=stat.get("months", {}))


def _build_session_response(s) -> ActiveSessionResponse:
    """Собирает DTO активной сессии отметки пары."""
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
    """Текущее состояние активного опроса пары старостой."""
    session = await get_active_session()
    return _build_session_response(session)


@router.post("/session/start", response_model=ActiveSessionResponse, dependencies=[Depends(verify_admin_access)])
async def start_session(payload: StartSessionRequest) -> ActiveSessionResponse:
    """Инициализация новой сессии опроса посещаемости (Admin only)."""
    t_date = date.fromisoformat(payload.target_date)
    session = await create_attendance_session(t_date, payload.lesson_num, payload.lesson_title, initiator_id=0)
    if not session:
        raise HTTPException(status_code=400, detail="Failed to create session (empty students or error)")
    return _build_session_response(session)


@router.post("/session/mark", response_model=ActiveSessionResponse, dependencies=[Depends(verify_admin_access)])
async def mark_student(payload: MarkStudentRequest) -> ActiveSessionResponse:
    """Выставление статуса текущему студенту (П, О, У, Н) (Admin only)."""
    session = await record_student_mark(payload.mark)
    if not session:
        raise HTTPException(status_code=400, detail="No active session to mark")
    return _build_session_response(session)


@router.post("/session/batch_present", response_model=ActiveSessionResponse, dependencies=[Depends(verify_admin_access)])
async def batch_present() -> ActiveSessionResponse:
    """Массовая отметка всех оставшихся студентов как присутствующих (П) (Admin only)."""
    session = await mark_all_remaining_present()
    if not session:
        raise HTTPException(status_code=400, detail="No active session")
    return _build_session_response(session)


@router.post("/session/commit", response_model=CommitAttendanceResponse, dependencies=[Depends(verify_admin_access)])
async def commit_session() -> CommitAttendanceResponse:
    """Сохранение результатов сессии в онлайн-таблицу Яндекс Документов (Admin only)."""
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
    """Сброс и отмена текущей незавершённой сессии (Admin only)."""
    await clear_session()
    return {"status": "ok", "message": "Attendance session cleared"}
