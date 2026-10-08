"""
Роутер экзаменов — GET /exams.

Возвращает все аттестации (зачёты, контрольные, курсовые)
с привязкой к неделям семестра.
"""

from fastapi import APIRouter, Depends

from api.deps import verify_api_or_tester
from api.schemas.exams import ExamsResponse
from services.exam_parser import get_group_exams

router = APIRouter(tags=["Exams"], prefix="/exams", dependencies=[Depends(verify_api_or_tester)])


@router.get("", response_model=ExamsResponse)
async def list_exams() -> ExamsResponse:
    """Полный список аттестаций и экзаменов группы."""
    exams = await get_group_exams()
    return ExamsResponse(count=len(exams), exams=exams)
