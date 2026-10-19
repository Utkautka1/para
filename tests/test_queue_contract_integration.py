"""
Контрактные и интеграционные тесты очереди задач para-solver.

Проверяют соответствие схемы payload задачи контракту очереди,
сериализацию/десериализацию, переход состояний (queue -> processing -> ack/nack),
а также защиту от ядовитых сообщений (poison pill) и DLQ-политику.
"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from core.redis_cache import (
    HW_DLQ_KEY,
    HW_PROCESSING_KEY,
    HW_QUEUE_KEY,
    ack_hw_task,
    nack_hw_task,
)
from services.solver.task_processor import execute_single_task


def build_valid_task_contract() -> dict:
    """Формирует эталонный payload задачи в соответствии с контрактом очереди."""
    return {
        "chat_id": 123456789,
        "message_id": 42,
        "message_thread_id": 100,
        "user_id": 987654321,
        "raw_text": "Реши задачу по математике № 4",
        "media_paths": ["/tmp/test.jpg"],
    }


def test_task_payload_schema_contract() -> None:
    """Проверяет обязательные поля контракта задачи для воркера solver."""
    payload = build_valid_task_contract()
    required_keys = {"chat_id", "message_id", "user_id"}
    assert required_keys.issubset(payload.keys())
    assert isinstance(payload["chat_id"], int)
    assert isinstance(payload["message_id"], int)
    assert isinstance(payload["user_id"], int)


def test_task_payload_json_serialization_roundtrip() -> None:
    """Проверяет корректность JSON-сериализации и десериализации payload."""
    payload = build_valid_task_contract()
    serialized = json.dumps(payload, ensure_ascii=False)
    deserialized = json.loads(serialized)
    assert deserialized == payload
    assert deserialized["raw_text"] == payload["raw_text"]


@pytest.mark.asyncio
async def test_ack_hw_task_removes_from_processing() -> None:
    """Проверяет, что ack_hw_task удаляет задачу из processing через LREM."""
    payload = build_valid_task_contract()
    mock_redis = AsyncMock()

    with patch("core.redis_cache.init_redis", return_value=mock_redis):
        await ack_hw_task(payload)

    serialized = json.dumps(payload, ensure_ascii=False)
    mock_redis.lrem.assert_awaited_once_with(HW_PROCESSING_KEY, 1, serialized)


@pytest.mark.asyncio
async def test_nack_hw_task_retry_vs_dlq() -> None:
    """Проверяет повторную постановку в очередь и эскалацию в DLQ при превышении лимита."""
    task = build_valid_task_contract()
    mock_redis = AsyncMock()

    with patch("core.redis_cache.init_redis", return_value=mock_redis):
        # 1. Попытка 1 (retries=0 -> 1 <= 3) -> возврат в очередь
        retried = await nack_hw_task(task, max_retries=3)
        assert retried is True
        assert task["retries"] == 1
        assert mock_redis.rpush.call_args[0][0] == HW_QUEUE_KEY

        # 2. Попытка 4 (retries=3 -> 4 > 3) -> отправка в DLQ
        task["retries"] = 3
        retried_dlq = await nack_hw_task(task, max_retries=3)
        assert retried_dlq is False
        assert task["retries"] == 4
        assert mock_redis.rpush.call_args[0][0] == HW_DLQ_KEY


@pytest.mark.asyncio
async def test_execute_single_task_success_calls_ack() -> None:
    """Проверяет успешное решение задачи и вызов ack_hw_task."""
    payload = build_valid_task_contract()
    mock_bot = AsyncMock()

    with (
        patch("services.solver.task_processor.resolve_task_payload", return_value=(b"image", "prompt")),
        patch("services.solver.task_processor.solve_homework", return_value="ГОСТ Решение"),
        patch("services.solver.task_processor.create_solution_docx"),
        patch("services.solver.task_processor.send_solution_to_telegram", return_value=True),
        patch("services.solver.task_processor.ack_hw_task") as mock_ack,
    ):
        await execute_single_task(mock_bot, payload)

    mock_ack.assert_awaited_once_with(payload)
