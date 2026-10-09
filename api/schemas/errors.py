"""
Pydantic-схемы стандартизированных ответов об ошибках para-api.

Зачем существует этот модуль:
Обеспечивает строго типизированное и унифицированное описание всех HTTP-ошибок
(4xx и 5xx) для OpenAPI/Swagger UI и централизованных exception handlers.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Стандартный ответ с ошибкой para-api."""
    detail: str = Field(..., description="Понятное человеку описание ошибки")
    code: Optional[str] = Field(None, description="Специфический строковый код ошибки")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Время возникновения ошибки в формате ISO 8601"
    )


class ValidationErrorItem(BaseModel):
    """Детали одной ошибки валидации Pydantic."""
    loc: List[str | int] = Field(..., description="Путь к невалидному полю")
    msg: str = Field(..., description="Сообщение валидатора")
    type: str = Field(..., description="Тип нарушения валидации")


class ValidationErrorResponse(BaseModel):
    """Стандартный ответ при ошибке 422 Unprocessable Entity."""
    detail: List[ValidationErrorItem] = Field(..., description="Список полей с ошибками валидации")
    code: str = Field(default="VALIDATION_ERROR", description="Код ошибки")


# Полная карта всех кодов ошибок для нативной регистрации в FastAPI(responses=...)
COMMON_API_RESPONSES: Dict[int | str, Dict[str, Any]] = {
    400: {"model": ErrorDetail, "description": "Некорректный запрос (Bad Request)"},
    401: {"model": ErrorDetail, "description": "Неавторизован: отсутствует/неверен API-ключ или сессия"},
    403: {"model": ErrorDetail, "description": "Доступ запрещен: требуются права администратора или старосты"},
    404: {"model": ErrorDetail, "description": "Запрашиваемый ресурс не найден (Not Found)"},
    405: {"model": ErrorDetail, "description": "Метод HTTP не поддерживается (Method Not Allowed)"},
    422: {"model": ValidationErrorResponse, "description": "Ошибка валидации параметров запроса"},
    429: {"model": ErrorDetail, "description": "Превышен лимит запросов (Too Many Requests / Rate Limit)"},
    500: {"model": ErrorDetail, "description": "Внутренняя ошибка сервера (Internal Server Error)"},
    502: {"model": ErrorDetail, "description": "Ошибочный шлюз: внешний сервис или туннель недоступен"},
    503: {"model": ErrorDetail, "description": "Сервис временно недоступен: сбой Redis / БД"},
    504: {"model": ErrorDetail, "description": "Таймаут шлюза при ожидании внешнего сервиса"},
}
