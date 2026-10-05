"""
Модели данных для интеграционных шлюзов.

Описывает структуры входных и выходных данных для обмена
с внешними сервисами (AI генерация решений, WOPI сессии, Яндекс Диск).
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class IntegrationResponse:
    """Стандартизированный ответ вызова внешней интеграции."""

    success: bool
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class DeepSeekTaskRequest:
    """Запрос на генерацию решения домашнего задания в DeepSeek."""

    task_id: str
    task_text: str
    image_base64: Optional[str] = None
