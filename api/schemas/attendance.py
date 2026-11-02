"""
Pydantic-схемы для роутера посещаемости студентов (статистика и сессии старосты).
"""

from pydantic import BaseModel, Field


class AttendanceTotals(BaseModel):
    """Суммарные отметки посещаемости студента."""

    present: int = Field(0, description="Присутствовал (П)", alias="П")
    absent_valid: int = Field(0, description="Уважительная причина (У)", alias="У")
    absent_invalid: int = Field(0, description="Неуважительная причина (Н)", alias="Н")
    late: int = Field(0, description="Опоздал (О)", alias="О")

    model_config = {"populate_by_name": True}


class StudentStatItem(BaseModel):
    """Статистика посещаемости одного студента."""

    fio: str = Field(..., description="ФИО студента", examples=["Иванов Иван"])
    total: dict[str, int] = Field(..., description="Итоги за все месяцы: П, О, У, Н")
    months: dict[str, dict[str, int]] = Field(default_factory=dict, description="Разбивка по месяцам")


class AttendanceStatsResponse(BaseModel):
    """Агрегированная ведомость посещаемости всей группы."""

    count: int = Field(..., description="Количество студентов в ведомости")
    students: list[StudentStatItem] = Field(default_factory=list, description="Список статистики по студентам")


class StudentPersonalStatsResponse(BaseModel):
    """Персональная аналитика посещаемости конкретного студента."""

    fio: str = Field(..., description="ФИО студента")
    total: dict[str, int] = Field(..., description="Общие отметки: П, О, У, Н")
    attendance_rate_percent: float = Field(..., description="Процент посещаемости занятий")
    months: dict[str, dict[str, int]] = Field(default_factory=dict, description="Отметки по месяцам")


class ActiveSessionResponse(BaseModel):
    """Состояние активной сессии отметки пары старостой."""

    is_active: bool = Field(..., description="Существует ли активная сессия")
    target_date: str | None = Field(None, description="Дата пары (YYYY-MM-DD)")
    lesson_num: int | None = Field(None, description="Номер пары (1..6)")
    lesson_title: str | None = Field(None, description="Название предмета")
    current_idx: int | None = Field(None, description="Индекс текущего студента")
    total_students: int | None = Field(None, description="Всего студентов в списке")
    current_student: str | None = Field(None, description="ФИО текущего опрашиваемого студента")
    marks: dict[str, str] | None = Field(None, description="Выставленные отметки")


class StartSessionRequest(BaseModel):
    """Запрос на старт сессии отметки посещаемости."""

    target_date: str = Field(..., description="Дата занятия (YYYY-MM-DD)", examples=["2026-10-09"])
    lesson_num: int = Field(..., ge=1, le=6, description="Номер пары", examples=[1])
    lesson_title: str = Field(..., min_length=2, description="Название предмета", examples=["Программирование"])


class MarkStudentRequest(BaseModel):
    """Запрос на выставление отметки студенту."""

    mark: str = Field(
        ..., pattern="^(П|О|У|Н)$", description="Отметка (П - присутствовал, О - опоздал, У - уваж., Н - неявка)"
    )


class CancelSessionResponse(BaseModel):
    """Результат сброса активной сессии отметки без сохранения."""

    status: str = Field(..., description="Статус операции")
    message: str = Field(..., description="Информационное сообщение")


class CommitAttendanceResponse(BaseModel):
    """Результат сохранения отметок в Яндекс Документы."""

    status: str = Field(..., description="Статус операции")
    message: str = Field(..., description="Информационное сообщение")
    marks_committed: int = Field(..., description="Количество зафиксированных отметок")
