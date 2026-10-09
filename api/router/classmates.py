"""
Роутер одногруппников — GET /classmates (список и карточка студента).
"""

from datetime import datetime
from typing import List, Optional

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
    """Конвертирует словарь студента в Pydantic модель."""
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
    """Полный реестр студентов учебной группы 1-КПД-3."""
    registry = load_classmates_registry()
    items = [_to_classmate_item(r) for r in registry]
    return ClassmatesListResponse(count=len(items), classmates=items)


def _find_student_in_registry(registry: List[dict], identifier: int) -> Optional[dict]:
    """Ищет студента по порядковому номеру в журнале либо Telegram ID."""
    for s in registry:
        if s.get("id") == identifier or s.get("tg_id") == identifier:
            return s
    return None


@router.get("/{student_id}", response_model=ClassmateDetailResponse)
async def get_classmate_detail(student_id: int) -> ClassmateDetailResponse:
    """Детальная информация о студенте по порядковому ID или Telegram ID."""
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
