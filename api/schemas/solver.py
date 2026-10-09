"""
Pydantic-схемы для роутера AI-решения домашних заданий (DeepSeek + очередь задач).
"""


from pydantic import BaseModel, Field


class SolverQueueStatusResponse(BaseModel):
    """Текущее состояние распределенной очереди задач ДЗ в Redis."""
    pending_tasks: int = Field(..., description="Задач в очереди на выполнение (hw:tasks:queue)")
    processing_tasks: int = Field(..., description="Задач в обработке воркером (hw:tasks:processing)")
    dlq_tasks: int = Field(..., description="Ошибочных задач в Dead Letter Queue (hw:tasks:dlq)")
    worker_online: bool = Field(..., description="Признак активности воркера para-solver")


class DirectSolveRequest(BaseModel):
    """Запрос на прямое решение учебной задачи через DeepSeek API."""
    prompt: str = Field(..., min_length=5, description="Текст условия задания или вопроса", examples=["Реши систему уравнений: 2x + 3y = 7, x - y = 1"])
    image_base64: str | None = Field(None, description="Опциональное изображение задачи в Base64")
    model: str | None = Field(None, description="Модель (по умолчанию deepseek-chat)")


class DirectSolveResponse(BaseModel):
    """Результат решения задачи нейросетью."""
    status: str = Field(..., description="Статус генерации (ok/error)")
    solution_text: str = Field(..., description="Подробный ответ с решением по ГОСТ")
    model: str = Field(..., description="Использованная языковая модель")


class TaskStatusResponse(BaseModel):
    """Статус обработки конкретного задания по Telegram Message ID."""
    message_id: int = Field(..., description="Telegram Message ID задания")
    is_processed: bool = Field(..., description="Выполнено ли задание")
    status_label: str = Field(..., description="Текстовый статус задачи")


class ClearQueueResponse(BaseModel):
    """Результат очистки очереди задач."""
    status: str = Field(..., description="Статус операции")
    deleted_count: int = Field(..., description="Количество удалённых элементов очереди")
