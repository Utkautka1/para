"""
Тесты очереди распознавания речи между ботом и сервисом stt (services/stt_queue.py).

Проверяет:
  1. Бот кладёт задание в очередь и возвращает текст из ключа результата.
  2. Ошибка распознавания в stt превращается в SttUnavailableError у бота.
  3. Отсутствие ответа до TRANSCRIBE_TIMEOUT даёт SttUnavailableError.
  4. Обработчик stt публикует текст или ошибку в ключ результата с TTL.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services import stt_queue


def _redis_with_result(payload: dict | None) -> AsyncMock:
    """Фейковый Redis: blpop отдаёт заранее заданный ответ stt (или ничего)."""
    redis = AsyncMock()
    redis.blpop = AsyncMock(return_value=("k", json.dumps(payload)) if payload else None)
    return redis


@pytest.mark.asyncio
async def test_transcribe_via_stt_returns_text() -> None:
    """Задание уходит в очередь, текст берётся из ответа stt."""
    redis = _redis_with_result({"text": "привет"})
    with patch.object(stt_queue, "get_redis", AsyncMock(return_value=redis)):
        assert await stt_queue.transcribe_via_stt("stt_audio/a.ogg") == "привет"
    queue_key, raw_job = redis.rpush.call_args.args
    job = json.loads(raw_job)
    assert queue_key == stt_queue.STT_QUEUE_KEY
    assert job["path"].endswith("stt_audio/a.ogg")
    assert redis.blpop.call_args.args[0] == [f"{stt_queue.STT_RESULT_KEY_PREFIX}{job['job_id']}"]


@pytest.mark.asyncio
async def test_transcribe_via_stt_raises_on_stt_error() -> None:
    """Ошибка распознавания на стороне stt пробрасывается боту."""
    redis = _redis_with_result({"error": "CUDA OOM"})
    with (
        patch.object(stt_queue, "get_redis", AsyncMock(return_value=redis)),
        pytest.raises(stt_queue.SttUnavailableError, match="CUDA OOM"),
    ):
        await stt_queue.transcribe_via_stt("a.ogg")


@pytest.mark.asyncio
async def test_transcribe_via_stt_times_out() -> None:
    """Без ответа stt до TRANSCRIBE_TIMEOUT бот получает SttUnavailableError."""
    redis = _redis_with_result(None)
    with (
        patch.object(stt_queue, "get_redis", AsyncMock(return_value=redis)),
        patch.object(stt_queue, "TRANSCRIBE_TIMEOUT", 0.0),
        pytest.raises(stt_queue.SttUnavailableError, match="не ответил"),
    ):
        await stt_queue.transcribe_via_stt("a.ogg")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("transcribe", "expected_key"),
    [(AsyncMock(return_value="текст"), "text"), (AsyncMock(side_effect=RuntimeError("boom")), "error")],
)
async def test_process_job_publishes_result_with_ttl(transcribe: AsyncMock, expected_key: str) -> None:
    """stt пишет текст или ошибку в ключ результата и ставит TTL."""
    pipe = MagicMock(execute=AsyncMock())
    ctx = MagicMock(__aenter__=AsyncMock(return_value=pipe), __aexit__=AsyncMock(return_value=False))
    redis = MagicMock(pipeline=MagicMock(return_value=ctx))
    await stt_queue._process_job(redis, json.dumps({"job_id": "j1", "path": "/x.ogg"}), transcribe)

    key, raw = pipe.rpush.call_args.args
    assert key == f"{stt_queue.STT_RESULT_KEY_PREFIX}j1"
    assert expected_key in json.loads(raw)
    pipe.expire.assert_called_once_with(key, stt_queue.STT_RESULT_TTL_SECONDS)
