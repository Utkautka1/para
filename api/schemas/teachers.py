"""
Pydantic-схемы ответов и запросов для роутера преподавателей.
"""

from pydantic import BaseModel, Field


class TeacherItem(BaseModel):
    """Данные преподавателя (ФИО и ссылка на видеоконференцию)."""
    full_name: str = Field(..., description="Полное ФИО преподавателя", examples=["Иванов Иван Иванович"])
    link_info: str = Field(..., description="Ссылка или инструкция подключения Zoom/Телемост")


class TeachersResponse(BaseModel):
    """Реестр преподавателей (ключ словаря — фамилия в нижнем регистре)."""
    count: int = Field(..., description="Общее число преподавателей в справочнике")
    teachers: dict[str, TeacherItem] = Field(..., description="Словарь преподавателей")


class TeacherSingleResponse(BaseModel):
    """Информация о конкретном найденном преподавателе."""
    key: str = Field(..., description="Идентификатор преподавателя (фамилия)")
    teacher: TeacherItem = Field(..., description="Данные преподавателя")


class TeacherSearchItem(BaseModel):
    """Элемент результата поиска преподавателей."""
    key: str = Field(..., description="Фамилия (ключ)")
    full_name: str = Field(..., description="ФИО преподавателя")
    link_info: str = Field(..., description="Ссылка для связи")


class TeacherSearchResponse(BaseModel):
    """Результаты поисковой выдачи преподавателей."""
    query: str = Field(..., description="Поисковый запрос")
    count: int = Field(..., description="Количество найденных записей")
    results: list[TeacherSearchItem] = Field(default_factory=list, description="Список совпадений")


class CustomTeacherCreateRequest(BaseModel):
    """Запрос на добавление или изменение кастомного преподавателя."""
    last_name: str = Field(..., min_length=2, max_length=50, description="Фамилия преподавателя", examples=["Петров"])
    full_name: str = Field(..., min_length=2, max_length=120, description="Полное ФИО", examples=["Петров Петр Петрович"])
    link_info: str = Field(..., min_length=1, max_length=500, description="Ссылка на занятие", examples=["https://telemost.yandex.ru/j/123456789"])


class TeachersRefreshResponse(BaseModel):
    """Результат обновления справочника с Яндекс Диска."""
    status: str = Field(..., description="Статус операции")
    count: int = Field(..., description="Количество загруженных преподавателей")
