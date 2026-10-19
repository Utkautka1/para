"""
Pydantic-схемы ответов для роутера экзаменов.

Переиспользует ExamItem из exam_parser,
дополняет схемами выборки ближайших аттестаций и обновления данных.
"""

from pydantic import BaseModel, Field

from services.models import ExamItem


class ExamsResponse(BaseModel):
    """Полный список аттестаций и экзаменов группы."""

    count: int = Field(..., description="Общее количество аттестаций")
    exams: list[ExamItem] = Field(default_factory=list, description="Список экзаменов и зачётов")


class UpcomingExamsResponse(BaseModel):
    """Ближайшие предстоящие аттестации группы."""

    current_week: int = Field(..., description="Текущая неделя семестра")
    count: int = Field(..., description="Количество ближайших аттестаций")
    upcoming_exams: list[ExamItem] = Field(default_factory=list, description="Список предстоящих экзаменов")


class ExamsRefreshResponse(BaseModel):
    """Результат принудительного обновления расписания экзаменов."""

    status: str = Field(..., description="Статус операции")
    updated_count: int = Field(..., description="Количество обновлённых записей")
