"""
Pydantic-схемы для реестра одногруппников учебной группы 1-КПД-3.
"""


from pydantic import BaseModel, Field


class ClassmateItem(BaseModel):
    """Данные студента группы."""
    id: int = Field(..., description="Порядковый номер в журнале", examples=[1])
    fio: str = Field(..., description="ФИО студента", examples=["Иванов Иван Иванович"])
    tg_id: int | None = Field(None, description="Привязанный Telegram ID", examples=[1000965210])
    username: str | None = Field(None, description="Telegram username без @", examples=["ivanov"])
    birth_date: str = Field(..., description="Дата рождения (ДД.ММ.ГГГГ)", examples=["15.05.2005"])


class ClassmatesListResponse(BaseModel):
    """Список всех студентов учебной группы."""
    count: int = Field(..., description="Количество студентов")
    classmates: list[ClassmateItem] = Field(default_factory=list, description="Список одногруппников")


class ClassmateDetailResponse(BaseModel):
    """Детальная информация о студенте."""
    student: ClassmateItem = Field(..., description="Данные студента")
    is_tg_linked: bool = Field(..., description="Привязан ли аккаунт Telegram")
    days_until_birthday: int = Field(..., description="Дней до следующего дня рождения")
    current_age: int = Field(..., description="Текущий возраст студента")
