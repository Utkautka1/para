"""
Тесты декомпозиции модулей сервиса para-solver (services/solver).

Проверяет корректность работы payload_extractor, telegram_reporter
и task_processor: извлечение вложений, генерацию ссылок и обработку ошибок.
"""

from unittest.mock import AsyncMock, patch

import pytest

import config
from services.solver.payload_extractor import (
    _read_code_file_payload,
    parse_file_payload,
)
from services.solver.task_processor import (
    _build_temp_doc_path,
    _cleanup_temp_file,
    _handle_task_failure,
)
from services.solver.telegram_reporter import build_post_link


def test_build_post_link_formats_clean_telegram_deep_link():
    """Проверяет корректное удаление префикса супергруппы -100 из ссылки."""
    link = build_post_link(-1001234567890, 42)
    assert link == "https://t.me/c/1234567890/42"


def test_build_post_link_handles_positive_chat_id():
    """Проверяет формирование ссылки при обычном chat_id."""
    link = build_post_link(123456789, 99)
    assert link == "https://t.me/c/123456789/99"


def test_read_code_file_payload_within_limit():
    """Проверяет добавление содержимого файла кода к промпту без обрезки."""
    code_bytes = b"print('hello world')"
    result = _read_code_file_payload(code_bytes, "test.py", "Реши задачу")
    assert "Реши задачу" in result
    assert "[Содержимое test.py]:" in result
    assert "print('hello world')" in result


def test_read_code_file_payload_truncates_excessive_length():
    """Проверяет обрезку кода, превышающего лимит длины промпта."""
    long_code = b"a" * (config.HW_MAX_PROMPT_TEXT_LENGTH + 500)
    result = _read_code_file_payload(long_code, "large.py", "Промпт")
    assert "...[Текст обрезан]..." in result


def test_parse_file_payload_handles_image_bytes():
    """Проверяет распознавание байтов изображения по расширению и MIME-типу."""
    fake_png = b"\x89PNG\r\n\x1a\n"
    img_bytes, prompt = parse_file_payload(fake_png, "screenshot.png", "image/png", "Задание 1")
    assert img_bytes == fake_png
    assert prompt == "Задание 1"


def test_parse_file_payload_handles_code_extension():
    """Проверяет обработку текстовых файлов исходного кода."""
    code = b"def foo(): return 42"
    img_bytes, prompt = parse_file_payload(code, "script.py", "text/x-python", "Вопрос")
    assert img_bytes is None
    assert "def foo(): return 42" in prompt


def test_parse_file_payload_fallback_on_unsupported_extension():
    """Проверяет возврат исходного промпта при неизвестном расширении."""
    doc = b"binary_blob"
    img_bytes, prompt = parse_file_payload(doc, "archive.bin", "application/octet-stream", "Промпт")
    assert img_bytes is None
    assert prompt == "Промпт"


def test_build_temp_doc_path_format():
    """Проверяет формат пути временного файла решения."""
    path = _build_temp_doc_path(100500)
    assert "solution_" in path
    assert "100500.docx" in path


def test_cleanup_temp_file_non_existent():
    """Проверяет безопасную обработку отсутствующего файла без исключений."""
    _cleanup_temp_file("/tmp/non_existent_para_test_file.docx")


@pytest.mark.asyncio
async def test_handle_task_failure_nack_and_notify():
    """Проверяет nack задачи и отправку уведомления при исчерпании попыток."""
    bot_mock = AsyncMock()
    task = {"chat_id": 123, "message_id": 456, "message_thread_id": 789}

    with patch("services.solver.task_processor.nack_hw_task", return_value=False) as nack_mock:
        await _handle_task_failure(bot_mock, task, 456, RuntimeError("Model timeout"))
        nack_mock.assert_awaited_once_with(task, max_retries=config.HW_MAX_TASK_RETRIES)
        bot_mock.send_message.assert_awaited_once()
