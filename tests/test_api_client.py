"""
Unit-тесты для клиента para-api (core/api_client.py).

Проверяет:
  1. Десериализацию ответа API в Pydantic-модели Lesson и ExamItem
  2. Разбор структуры расписания недели
  3. Механизм повтора запроса (retry) при сбое соединения
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from core.api_client import (
    _api_get,
    get_api_exams,
    get_api_schedule_for_date,
)
from services.models import ExamItem, Lesson


@pytest.mark.asyncio
async def test_get_api_schedule_for_date_deserialization():
    """Проверяет десериализацию списка занятий из ответа /schedule/day."""
    fake_json = {
        "date": "2026-09-28",
        "lessons": [
            {
                "period": 0,
                "time_str": "08:30-10:00",
                "subject": "Физика",
                "lesson_type": "Лаб",
                "teacher": "Сидоров С.С.",
                "is_remote": False,
                "room": "205",
                "address": "Цветочная",
                "subgroup": 1,
                "is_stream": False,
            }
        ],
    }
    with patch("core.api_client.fetch_day_schedule", new=AsyncMock(return_value=fake_json)):
        lessons = await get_api_schedule_for_date(date(2026, 9, 28))
        assert len(lessons) == 1
        assert isinstance(lessons[0], Lesson)
        assert lessons[0].subject == "Физика"
        assert lessons[0].subgroup == 1


@pytest.mark.asyncio
async def test_get_api_exams_deserialization():
    """Проверяет десериализацию списка экзаменов из ответа /exams."""
    fake_json = {
        "count": 1,
        "exams": [
            {
                "subject": "Информатика",
                "exam_type": "Экзамен",
                "teacher": "Козлов К.К.",
                "room": "301",
                "address": "Вознесенский",
                "weeks": [16, 17],
                "subgroup": 0,
                "format_str": "Очно",
            }
        ],
    }
    with patch("core.api_client.fetch_exams", new=AsyncMock(return_value=fake_json)):
        exams = await get_api_exams()
        assert len(exams) == 1
        assert isinstance(exams[0], ExamItem)
        assert exams[0].weeks == [16, 17]


@pytest.mark.asyncio
async def test_api_get_retries_on_network_error():
    """Проверяет, что _api_get делает retry при TransportError и завершается успешно."""
    mock_client = AsyncMock()
    mock_res = MagicMock()
    mock_res.json.return_value = {"status": "ok"}
    mock_res.raise_for_status = MagicMock()

    # Первый вызов падает с ошибкой сети, второй успешен
    mock_client.get.side_effect = [
        httpx.ConnectError("Connection refused"),
        mock_res,
    ]

    with patch("core.api_client._get_client", return_value=mock_client):
        res = await _api_get("/health")
        assert res == {"status": "ok"}
        assert mock_client.get.call_count == 2
