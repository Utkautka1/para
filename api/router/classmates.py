"""
Роутер одногруппников — GET /classmates (список и карточка студента).
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import verify_api_or_tester
from api.schemas.classmates import (
    ClassmateDetailResponse,
    ClassmateItem,
    ClassmatesListResponse,
)
from config import TIMEZONE
from services.birthday_manager import calculate_days_and_age
from services.classmates_auth import load_classmates_registry

router = APIRouter(tags=["Classmates"], prefix="/classmates", dependencies=[Depends(verify_api_or_tester)])


def _to_classmate_item(raw: dict) -> ClassmateItem:
    """
    Конвертирует сырой словарь студента из JSON в Pydantic модель ClassmateItem.

    Форматирует дату рождения в формат ДД.ММ.ГГГГ и подставляет дефолтные значения.
    Служит фабричным методом для унификации структур в ответах API.

    Возвращает объект ClassmateItem.
    """

    b_day = f"{raw.get('day', 1):02d}.{raw.get('month', 1):02d}.{raw.get('year', 2005)}"

    return ClassmateItem(
        id=raw.get("id", 0),
        fio=raw.get("fio", "Неизвестно"),
        tg_id=raw.get("tg_id"),
        username=raw.get("username"),
        birth_date=b_day,
    )


@router.get("", response_model=ClassmatesListResponse)
async def list_classmates() -> ClassmatesListResponse:
    """
    Возвращает полный реестр одногруппников группы 1-КПД-3.

    Считывает локальный статический реестр студентов с метаданными Telegram.
    Используется для автодополнения и формирования списков старосты.

    Возвращает ClassmatesListResponse со списком всех студентов.
    """

    registry = load_classmates_registry()
    items = [_to_classmate_item(r) for r in registry]

    return ClassmatesListResponse(count=len(items), classmates=items)


def _find_student_in_registry(registry: list[dict], identifier: int) -> dict | None:
    """
    Ищет запись студента по порядковому номеру или по Telegram ID.

    Обеспечивает универсальный поиск как по ID в журнале (1..30), так и по Telegram ID.
    Защищает от дублирования логики поиска в хэндлерах.

    Возвращает найденный словарь студента или None.
    """

    for s in registry:
        if s.get("id") == identifier or s.get("tg_id") == identifier:
            return s

    return None


@router.get("/{student_id}", response_model=ClassmateDetailResponse)
async def get_classmate_detail(student_id: int) -> ClassmateDetailResponse:
    """
    Возвращает детальную карточку студента по его порядковому ID или Telegram ID.

    Рассчитывает текущий возраст и количество дней до дня рождения.
    Выбрасывает HTTP 404, если студент с данным идентификатором не найден.

    Возвращает ClassmateDetailResponse с детальной информацией.
    """

    registry = load_classmates_registry()
    student = _find_student_in_registry(registry, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    today = datetime.now(TIMEZONE).date()
    calc = calculate_days_and_age(student, today)
    item = _to_classmate_item(student)

    return ClassmateDetailResponse(
        student=item,
        is_tg_linked=student.get("tg_id") is not None,
        days_until_birthday=calc["days_until"],
        current_age=calc["turning_age"] - (0 if calc["is_today"] else 1),
    )
