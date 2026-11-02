"""
Контрактные и интеграционные тесты очереди задач para-solver.

Проверяют соответствие схемы payload задачи контракту очереди,
сериализацию/десериализацию, переход состояний (queue -> processing -> ack/nack),
а также защиту от ядовитых сообщений (poison pill) и DLQ-политику.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import HW_DLQ_KEY, HW_PROCESSING_KEY, HW_QUEUE_KEY
from core.hw_queue import ack_hw_task, nack_hw_task
from core.redis_cache import allow_request
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

    with patch("core.hw_queue.init_redis", return_value=mock_redis):
        await ack_hw_task(payload)

    serialized = json.dumps(payload, ensure_ascii=False)
    mock_redis.lrem.assert_awaited_once_with(HW_PROCESSING_KEY, 1, serialized)


@pytest.mark.asyncio
async def test_nack_hw_task_retry_vs_dlq() -> None:
    """Проверяет повторную постановку в очередь и эскалацию в DLQ при превышении лимита."""
    task = build_valid_task_contract()
    mock_redis = AsyncMock()

    with patch("core.hw_queue.init_redis", return_value=mock_redis):
        # 1. Попытка 1 (retries=0 -> 1 <= 3) -> возврат в очередь
        retried = await nack_hw_task(task, max_retries=3)
        assert retried is True
        assert task["retries"] == 1
        assert mock_redis.eval.call_args[0][3] == HW_QUEUE_KEY

        # 2. Попытка 4 (retries=3 -> 4 > 3) -> отправка в DLQ
        task["retries"] = 3
        retried_dlq = await nack_hw_task(task, max_retries=3)
        assert retried_dlq is False
        assert task["retries"] == 4
        assert mock_redis.eval.call_args[0][3] == HW_DLQ_KEY


@pytest.mark.asyncio
async def test_nack_removes_original_payload_from_processing() -> None:
    """LREM снимает строку до инкремента retries — иначе оригинал остаётся в processing."""
    task = build_valid_task_contract()
    original = json.dumps(task, ensure_ascii=False)
    mock_redis = AsyncMock()

    with patch("core.hw_queue.init_redis", return_value=mock_redis):
        await nack_hw_task(task, max_retries=3)

    _, numkeys, processing, _, removed, pushed = mock_redis.eval.call_args[0]
    assert (numkeys, processing, removed) == (2, HW_PROCESSING_KEY, original)
    assert json.loads(pushed)["retries"] == 1


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


# === Атомарный лимит запросов ===


def _redis_with_pipeline(count: int) -> MagicMock:
    """Мок Redis, чья транзакция SET NX + INCR возвращает count."""
    pipe = MagicMock()
    pipe.execute = AsyncMock(return_value=[True, count])
    pipe.__aenter__ = AsyncMock(return_value=pipe)
    pipe.__aexit__ = AsyncMock(return_value=None)
    redis = MagicMock()
    redis.pipeline.return_value = pipe
    return redis


@pytest.mark.asyncio
async def test_allow_request_sets_ttl_in_same_transaction() -> None:
    """TTL выставляется в той же транзакции, что и инкремент."""
    redis = _redis_with_pipeline(1)
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=redis)):
        assert await allow_request("k", limit=3, window_seconds=60) is True
    redis.pipeline.assert_called_once_with(transaction=True)
    redis.pipeline.return_value.set.assert_called_once_with("k", 0, ex=60, nx=True)


@pytest.mark.asyncio
async def test_allow_request_over_limit() -> None:
    """Запрос сверх лимита отклоняется."""
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=_redis_with_pipeline(4))):
        assert await allow_request("k", limit=3, window_seconds=60) is False


@pytest.mark.asyncio
async def test_allow_request_denies_without_redis() -> None:
    """Без Redis лимит не открывает доступ к DeepSeek."""
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=None)):
        assert await allow_request("k", limit=3, window_seconds=60) is False
