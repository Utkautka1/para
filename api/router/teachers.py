"""
Роутер преподавателей — GET /teachers, search, custom, refresh.

Предоставляет контакты и ссылки видеосвязи (Zoom, Яндекс Телемост)
из официального документа Яндекс Диска и пользовательских настроек.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.teachers import (
    CustomTeacherCreateRequest,
    TeacherItem,
    TeacherSearchItem,
    TeacherSearchResponse,
    TeacherSingleResponse,
    TeachersRefreshResponse,
    TeachersResponse,
)
from integrations.docx_parser import get_teacher_links
from services.custom_teachers import delete_custom_teacher, save_custom_teacher

router = APIRouter(tags=["Teachers"], prefix="/teachers", dependencies=[Depends(verify_api_or_tester)])


@router.get("", response_model=TeachersResponse)
async def list_teachers(force_refresh: bool = Query(default=False)) -> TeachersResponse:
    """
    Возвращает полный реестр преподавателей и их ссылок видеосвязи.

    Объединяет официальные ссылки из Яндекс Документа и пользовательские оверрайды.
    Использует кэширование в памяти и Redis для быстрого ответа.

    Возвращает TeachersResponse со словарем всех преподавателей.
    """

    raw = await get_teacher_links(force_refresh=force_refresh)
    teachers = {k: TeacherItem(**v) for k, v in raw.items()}

    return TeachersResponse(count=len(teachers), teachers=teachers)


@router.get("/search", response_model=TeacherSearchResponse)
async def search_teachers(
    q: str = Query(..., min_length=2, description="Поисковый запрос (часть фамилии)"),
) -> TeacherSearchResponse:
    """
    Выполняет регистронезависимый поиск преподавателей по фрагменту ФИО.

    Фильтрует реестр по вхождению подстроки в фамилию или полное имя.
    Требует минимум 2 символа для снижения нагрузки на сериализацию.

    Возвращает TeacherSearchResponse с совпавшими преподавателями.
    """

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
    """
    Возвращает контактную карточку преподавателя по его фамилии.

    Нормализует переданную фамилию к нижнему регистру для точного совпадения.
    Выбрасывает HTTP 404, если преподаватель не найден в общем реестре.

    Возвращает TeacherSingleResponse с объектом преподавателя.
    """

    raw = await get_teacher_links(force_refresh=False)
    key = last_name.strip().lower()
    if key not in raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    item = TeacherItem(**raw[key])

    return TeacherSingleResponse(key=key, teacher=item)


@router.post("/custom", response_model=TeacherSingleResponse, dependencies=[Depends(verify_admin_access)])
async def add_custom_teacher(payload: CustomTeacherCreateRequest) -> TeacherSingleResponse:
    """
    Добавляет или обновляет персональную ссылку преподавателя (Admin only).

    Позволяет переопределить неактуальную ссылку из официального документа.
    Сохраняет запись в локальное JSON-хранилище и сбрасывает кэш.

    Возвращает TeacherSingleResponse с обновленными данными.
    """

    key = payload.last_name.strip().lower()
    save_custom_teacher(key, payload.full_name, payload.link_info)
    item = TeacherItem(full_name=payload.full_name, link_info=payload.link_info)

    return TeacherSingleResponse(key=key, teacher=item)


@router.delete("/custom/{last_name}", dependencies=[Depends(verify_admin_access)])
async def remove_custom_teacher(last_name: str) -> dict[str, str]:
    """
    Удаляет пользовательское переопределение преподавателя (Admin only).

    Возвращает поведение ссылки к значению по умолчанию из документа Яндекс Диска.
    Защищён verify_admin_access.

    Возвращает словарь со статусом 'ok' и удаленной фамилией.
    """

    delete_custom_teacher(last_name.strip().lower())

    return {"status": "ok", "deleted": last_name}


@router.post("/refresh", response_model=TeachersRefreshResponse, dependencies=[Depends(verify_admin_access)])
async def refresh_teachers() -> TeachersRefreshResponse:
    """
    Выполняет принудительную перепроверку документа на Яндекс Диске (Admin only).

    Загружает актуальный .docx файл по публичной ссылке и перестраивает таблицу ссылок.
    Инвалидирует промежуточный Redis-кэш.

    Возвращает TeachersRefreshResponse со статусом 'ok' и количеством записей.
    """

    raw = await get_teacher_links(force_refresh=True)

    return TeachersRefreshResponse(status="ok", count=len(raw))
