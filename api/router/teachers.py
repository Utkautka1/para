"""
Роутер преподавателей — GET /teachers.

Возвращает актуальные ФИО и ссылки Zoom/Телемоста из Yandex Disk docx.
"""

from fastapi import APIRouter, Depends, Query

from api.deps import verify_api_key
from api.schemas.teachers import TeacherItem, TeachersResponse
from integrations.docx_parser import get_teacher_links

router = APIRouter(tags=["Teachers"], prefix="/teachers", dependencies=[Depends(verify_api_key)])


@router.get("", response_model=TeachersResponse)
async def list_teachers(
    force_refresh: bool = Query(default=False),
) -> TeachersResponse:
    """Контакты всех преподавателей (ФИО + Zoom/Телемост)."""
    raw = await get_teacher_links(force_refresh=force_refresh)
    teachers = {k: TeacherItem(**v) for k, v in raw.items()}
    return TeachersResponse(count=len(teachers), teachers=teachers)
