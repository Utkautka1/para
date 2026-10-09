"""
Роутер преподавателей — GET /teachers, search, custom, refresh.

Предоставляет контакты и ссылки видеосвязи (Zoom, Яндекс Телемост)
из официального документа Яндекс Диска и пользовательских настроек.
"""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.teachers import (
    CustomTeacherCreateRequest,
    TeacherItem,
    TeacherSearchItem,
    TeacherSearchResponse,
    TeachersRefreshResponse,
    TeachersResponse,
    TeacherSingleResponse,
)
from integrations.docx_parser import get_teacher_links
from services.custom_teachers import delete_custom_teacher, save_custom_teacher

router = APIRouter(tags=["Teachers"], prefix="/teachers", dependencies=[Depends(verify_api_or_tester)])


@router.get("", response_model=TeachersResponse)
async def list_teachers(force_refresh: bool = Query(default=False)) -> TeachersResponse:
    """Полный реестр преподавателей (ФИО + ссылка на занятие)."""
    raw = await get_teacher_links(force_refresh=force_refresh)
    teachers = {k: TeacherItem(**v) for k, v in raw.items()}
    return TeachersResponse(count=len(teachers), teachers=teachers)


@router.get("/search", response_model=TeacherSearchResponse)
async def search_teachers(q: str = Query(..., min_length=2, description="Поисковый запрос (часть фамилии)")) -> TeacherSearchResponse:
    """Поиск преподавателей по фрагменту фамилии или имени."""
    raw = await get_teacher_links(force_refresh=False)
    query_lower = q.strip().lower()
    matches = [
        TeacherSearchItem(key=k, full_name=v["full_name"], link_info=v["link_info"])
        for k, v in raw.items()
        if query_lower in k or query_lower in v["full_name"].lower()
    ]
    return TeacherSearchResponse(query=q, count=len(matches), results=matches)


@router.get("/{last_name}", response_model=TeacherSingleResponse)
async def get_teacher(last_name: str) -> TeacherSingleResponse:
    """Получение контакта конкретного преподавателя по фамилии."""
    raw = await get_teacher_links(force_refresh=False)
    key = last_name.strip().lower()
    if key not in raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    item = TeacherItem(**raw[key])
    return TeacherSingleResponse(key=key, teacher=item)


@router.post("/custom", response_model=TeacherSingleResponse)
async def add_custom_teacher(payload: CustomTeacherCreateRequest) -> TeacherSingleResponse:
    """Добавление или обновление персональной ссылки преподавателя."""
    key = payload.last_name.strip().lower()
    save_custom_teacher(key, payload.full_name, payload.link_info)
    item = TeacherItem(full_name=payload.full_name, link_info=payload.link_info)
    return TeacherSingleResponse(key=key, teacher=item)


@router.delete("/custom/{last_name}", dependencies=[Depends(verify_admin_access)])
async def remove_custom_teacher(last_name: str) -> Dict[str, str]:
    """Удаление кастомного преподавателя (Admin only)."""
    delete_custom_teacher(last_name.strip().lower())
    return {"status": "ok", "deleted": last_name}


@router.post("/refresh", response_model=TeachersRefreshResponse, dependencies=[Depends(verify_admin_access)])
async def refresh_teachers() -> TeachersRefreshResponse:
    """Принудительная загрузка актуального .docx с Яндекс Диска (Admin only)."""
    raw = await get_teacher_links(force_refresh=True)
    return TeachersRefreshResponse(status="ok", count=len(raw))
