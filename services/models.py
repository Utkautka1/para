"""
Общие Pydantic-модели данных, используемые всеми сервисами.

Вынесены из парсеров, чтобы бот мог десериализовать JSON из API
без импорта тяжёлых модулей парсинга (httpx, docx, etc).
"""


from pydantic import BaseModel


class Lesson(BaseModel):
    """Модель данных одного занятия в расписании."""
    period: int
    time_str: str
    subject: str
    lesson_type: str
    teacher: str
    is_remote: bool
    room: str
    address: str
    subgroup: int = 0
    is_stream: bool = False
    remote_link: str | None = None
    remote_passcode: str | None = None
    remote_meeting_id: str | None = None

    @property
    def number(self) -> int:
        """Номер пары от 1 до 6 (period + 1)."""
        return self.period + 1


class ExamItem(BaseModel):
    """Модель контрольного мероприятия/экзамена."""
    subject: str
    exam_type: str
    teacher: str
    room: str
    address: str
    weeks: list[int]
    subgroup: int = 0
    format_str: str = "Очно"
