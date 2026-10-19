"""
Пакет сервиса решения домашних заданий (para-solver).

Декомпозирует логику обработки очереди задач на три специализированных слоя:
  - payload_extractor: извлечение медиа, PDF, DOCX и исходного кода
  - telegram_reporter: доставка готовых решений и уведомлений в Telegram
  - task_processor: параллельная обработка задач под семафором с ACK/NACK
"""

from services.solver.payload_extractor import (
    download_file_bytes,
    extract_docx_data,
    extract_pdf_data,
    parse_file_payload,
    resolve_task_payload,
)
from services.solver.task_processor import (
    execute_single_task,
    run_solver_loop,
)
from services.solver.telegram_reporter import (
    build_post_link,
    notify_task_error,
    send_solution_to_telegram,
)

__all__ = [
    "build_post_link",
    "download_file_bytes",
    "execute_single_task",
    "extract_docx_data",
    "extract_pdf_data",
    "notify_task_error",
    "parse_file_payload",
    "resolve_task_payload",
    "run_solver_loop",
    "send_solution_to_telegram",
]
