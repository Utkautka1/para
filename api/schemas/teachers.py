"""
Pydantic-схемы ответов для роутера преподавателей.

Переиспользует TeacherData из docx_parser (TypedDict → Pydantic).
"""


from pydantic import BaseModel


class TeacherItem(BaseModel):
    """Данные одного преподавателя."""
    full_name: str
    link_info: str


class TeachersResponse(BaseModel):
    """Словарь контактов преподавателей (ключ — фамилия)."""
    count: int
    teachers: dict[str, TeacherItem]
