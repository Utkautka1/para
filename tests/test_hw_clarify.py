"""
Тесты окна уточнений солвера ДЗ (отложенная очередь в core/redis_cache.py и хэндлер).

Баг: реплай студента на своё задание уходил в solver отдельной задачей — два решения.
Проверяет:
  1. Новое задание откладывается, созревшее переносится в очередь
  2. Уточнение в окне склеивается с отложенным заданием — решение одно
  3. Уточнение после ухода задания в solver — исправление (revision_of), сразу в очередь
  4. Реплай на чужое задание остаётся самостоятельной задачей
  5. Подпись исправленного решения ссылается на задание и уточнение
"""

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import core.redis_cache as rc
from bot.handlers.user import hw_solver
from services.solver.telegram_reporter import build_solution_caption


class FakeRedis:
    """Минимальный Redis для отложенной очереди: zset, строки, список и Lua-перенос."""

    def __init__(self) -> None:
        self.zset: dict[str, float] = {}
        self.kv: dict[str, str] = {}
        self.queue: list[str] = []

    async def zadd(self, key: str, mapping: dict[str, float]) -> None:
        self.zset.update(mapping)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.kv[key] = value

    async def getdel(self, key: str) -> str | None:
        return self.kv.pop(key, None)

    async def zrem(self, key: str, member: str) -> int:
        return int(self.zset.pop(member, None) is not None)

    async def eval(self, script: str, numkeys: int, *args) -> int:
        # Повторяет LUA_PROMOTE_DUE: созревшие элементы zset уходят в конец очереди
        due = [p for p, score in sorted(self.zset.items(), key=lambda x: x[1]) if score <= float(args[-1])]
        for payload in due:
            del self.zset[payload]
            self.queue.append(payload)
        return len(due)


@pytest.fixture
def redis():
    fake = FakeRedis()
    with patch.object(rc, "init_redis", AsyncMock(return_value=fake)):
        yield fake


@pytest.mark.asyncio
async def test_task_waits_in_window_then_promoted(redis) -> None:
    await rc.schedule_hw_task({"message_id": 1, "prompt": "реши"}, delay_seconds=30)
    assert await rc.promote_due_hw_tasks() == 0
    with patch.object(rc.time, "time", return_value=time.time() + 31):
        assert await rc.promote_due_hw_tasks() == 1
    assert json.loads(redis.queue[0])["message_id"] == 1


@pytest.mark.asyncio
async def test_take_pending_only_before_promotion(redis) -> None:
    await rc.schedule_hw_task({"message_id": 1}, delay_seconds=30)
    assert (await rc.take_pending_hw_task(1))["message_id"] == 1
    assert await rc.promote_due_hw_tasks() == 0
    await rc.schedule_hw_task({"message_id": 2}, delay_seconds=0)
    await rc.promote_due_hw_tasks()
    # Задание уже в solver — окно уточнений закрыто
    assert await rc.take_pending_hw_task(2) is None


def _msg(message_id: int, user_id: int, text: str, reply_to: MagicMock | None = None) -> MagicMock:
    msg = MagicMock(message_id=message_id, text=text, caption=None, photo=None, document=None, message_thread_id=405)
    msg.from_user = MagicMock(id=user_id, full_name="Иванов Иван")
    msg.chat = MagicMock(id=-100123)
    msg.reply_to_message = reply_to
    return msg


@pytest.fixture
def handler_env():
    """Изолирует хэндлер: всё разрешено, Redis-обвязка и ачивки замоканы."""
    with (
        patch.object(hw_solver, "is_hw_allowed", AsyncMock(return_value=True)),
        patch.object(hw_solver, "is_message_processed", AsyncMock(return_value=True)),
        patch.object(hw_solver, "is_hash_processed", AsyncMock(return_value=False)),
        patch.object(hw_solver, "mark_hash_processed", AsyncMock()),
        patch.object(hw_solver, "mark_message_processed", AsyncMock()),
        patch.object(hw_solver, "acknowledge_hw_task", AsyncMock()),
        patch.object(hw_solver, "on_homework_task", MagicMock()),
        patch.object(hw_solver.asyncio, "create_task", MagicMock()),
        patch.object(hw_solver, "push_hw_task", AsyncMock()) as push,
        patch.object(hw_solver, "schedule_hw_task", AsyncMock()) as schedule,
        patch.object(hw_solver, "take_pending_hw_task", AsyncMock(return_value=None)) as take,
    ):
        yield push, schedule, take


@pytest.mark.asyncio
async def test_new_task_is_scheduled_not_pushed(handler_env) -> None:
    push, schedule, _ = handler_env
    await hw_solver.handle_new_homework(_msg(1, 7, "реши задачу 5"), AsyncMock())
    push.assert_not_awaited()
    assert schedule.await_args.args[0]["revision_of"] is None


@pytest.mark.asyncio
async def test_clarification_in_window_merges(handler_env) -> None:
    push, schedule, take = handler_env
    take.return_value = {"message_id": 1, "prompt": "реши задачу 5"}
    original = _msg(1, 7, "реши задачу 5")
    await hw_solver.handle_new_homework(_msg(2, 7, "только пункт б", reply_to=original), AsyncMock())
    push.assert_not_awaited()
    merged = schedule.await_args.args[0]
    assert merged["message_id"] == 1
    assert merged["prompt"] == "реши задачу 5\nУточнение: только пункт б"


@pytest.mark.asyncio
async def test_clarification_after_start_is_revision(handler_env) -> None:
    push, schedule, _ = handler_env
    original = _msg(1, 7, "реши задачу 5")
    await hw_solver.handle_new_homework(_msg(2, 7, "только пункт б", reply_to=original), AsyncMock())
    schedule.assert_not_awaited()
    task = push.await_args.args[0]
    assert (task["message_id"], task["revision_of"]) == (2, 1)


@pytest.mark.asyncio
async def test_reply_to_someone_else_is_separate_task(handler_env) -> None:
    push, schedule, take = handler_env
    foreign = _msg(1, 99, "задача 5 из учебника")
    await hw_solver.handle_new_homework(_msg(2, 7, "реши 2 вариант", reply_to=foreign), AsyncMock())
    take.assert_not_awaited()
    push.assert_not_awaited()
    assert schedule.await_args.args[0]["revision_of"] is None


def test_solution_caption() -> None:
    assert "Готовое решение" in build_solution_caption(-100123, 5, None)
    revised = build_solution_caption(-100123, 6, 5)
    assert "Исправленное решение" in revised
    assert "t.me/c/123/5" in revised and "t.me/c/123/6" in revised
