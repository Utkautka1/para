"""
Pydantic-схемы ответов для роутера экзаменов.

Переиспользует ExamItem из exam_parser (уже Pydantic BaseModel).
"""


from pydantic import BaseModel

from services.models import ExamItem


class ExamsResponse(BaseModel):
    """Список аттестаций/экзаменов группы."""
    count: int
    exams: list[ExamItem]
