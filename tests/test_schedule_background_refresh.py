"""
Тесты фонового обновления расписания: worker качает, api/bot читают снапшот из Redis.

Проверяет:
  1. Читатель отдаёт свежий снапшот worker'а без загрузки из API КТМУ.
  2. force_refresh у читателя ставит запрос worker'у и не качает сам.
  3. Смена версии снапшота перечитывает его и сбрасывает L1-кэш дней.
  4. Устаревший или отсутствующий снапшот включает самостоятельную загрузку.
  5. Цикл worker'а качает по таймеру и по флагу «обновить сейчас».
  6. Метаданные снапшота содержат версию и время загрузки.
"""

import json
import time
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import services.schedule_parser as sp
from services import schedule_refresher

_SNAP_V1 = {"config": {"semesterStart": "2026-09-01"}, "v": 1}
_SNAP_V2 = {"config": {"semesterStart": "2026-09-01"}, "v": 2}


@pytest.fixture(autouse=True)
def _reset_parser_state():
    """Сбрасывает глобальное состояние schedule_parser между тестами."""
    sp._DATA_CACHE = (0.0, None)
    sp._LOCAL_VERSION = None
    sp._LAST_SYNC_CHECK = 0.0
    sp._IS_FETCH_OWNER = False
    sp.clear_resolved_day_cache()
    yield
    sp._IS_FETCH_OWNER = False


def _meta(version: str, age: float = 0.0) -> dict:
    """Метаданные снапшота с заданной версией и возрастом (секунды)."""
    return {"version": version, "fetched_at": time.time() - age}


@pytest.mark.asyncio
async def test_reader_serves_fresh_snapshot_without_fetching() -> None:
    """Читатель берёт снапшот worker'а и не обращается к API КТМУ."""
    fetch = AsyncMock()
    with (
        patch("core.redis_cache.load_schedule_meta", AsyncMock(return_value=_meta("v1"))),
        patch("core.redis_cache.load_schedule_snapshot", AsyncMock(return_value=(_SNAP_V1, _meta("v1")))),
        patch.object(sp, "_fetch_remote_schedule", fetch),
    ):
        assert await sp.fetch_schedule_data() == _SNAP_V1
    fetch.assert_not_called()
    assert sp._LOCAL_VERSION == "v1"


@pytest.mark.asyncio
async def test_reader_force_refresh_requests_worker_instead_of_fetching() -> None:
    """force_refresh у читателя ставит флаг worker'у и сразу отдаёт кэш."""
    request = AsyncMock(return_value=True)
    fetch = AsyncMock()
    with (
        patch("core.redis_cache.request_schedule_refresh", request),
        patch("core.redis_cache.load_schedule_meta", AsyncMock(return_value=_meta("v1"))),
        patch("core.redis_cache.load_schedule_snapshot", AsyncMock(return_value=(_SNAP_V1, _meta("v1")))),
        patch.object(sp, "_fetch_remote_schedule", fetch),
    ):
        assert await sp.fetch_schedule_data(force_refresh=True) == _SNAP_V1
    request.assert_awaited_once()
    fetch.assert_not_called()


@pytest.mark.asyncio
async def test_reader_reloads_snapshot_and_day_cache_on_version_change() -> None:
    """Новая версия в meta перечитывает снапшот и сбрасывает L1-кэш дней."""
    sp._DATA_CACHE = (time.time(), _SNAP_V1)
    sp._LOCAL_VERSION = "v1"
    sp._RESOLVED_DAY_CACHE[date(2026, 10, 30)] = []
    with (
        patch("core.redis_cache.load_schedule_meta", AsyncMock(return_value=_meta("v2"))),
        patch("core.redis_cache.load_schedule_snapshot", AsyncMock(return_value=(_SNAP_V2, _meta("v2")))),
    ):
        assert await sp.fetch_schedule_data() == _SNAP_V2
    assert sp._LOCAL_VERSION == "v2"
    assert date(2026, 10, 30) not in sp._RESOLVED_DAY_CACHE


@pytest.mark.asyncio
async def test_reader_skips_redis_within_sync_window() -> None:
    """В пределах SCHEDULE_SYNC_CHECK_SECONDS читатель не ходит в Redis."""
    sp._DATA_CACHE = (time.time(), _SNAP_V1)
    sp._LAST_SYNC_CHECK = time.time()
    meta = AsyncMock()
    with patch("core.redis_cache.load_schedule_meta", meta):
        assert await sp.fetch_schedule_data() == _SNAP_V1
    meta.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("meta", [None, _meta("v1", age=sp.SCHEDULE_STALE_LIMIT_SECONDS + 60)])
async def test_reader_falls_back_to_own_fetch_when_snapshot_stale(meta: dict | None) -> None:
    """Без свежего снапшота (worker упал) читатель качает сам."""
    refresh = AsyncMock()
    with (
        patch("core.redis_cache.load_schedule_meta", AsyncMock(return_value=meta)),
        patch("core.redis_cache.load_schedule_snapshot", AsyncMock(return_value=(None, None))),
        patch.object(sp, "refresh_schedule_in_background", refresh),
    ):
        await sp.fetch_schedule_data()
    refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_owner_does_not_refresh_by_ttl() -> None:
    """Загрузчик не запускает загрузку по TTL — этим занимается schedule_refresh_loop."""
    sp.enable_schedule_fetch_ownership()
    sp._DATA_CACHE = (time.time() - sp.SCHEDULE_CACHE_TTL_SECONDS - 1, _SNAP_V1)
    with patch.object(sp, "_trigger_stale_refresh", AsyncMock()) as trigger:
        assert await sp.fetch_schedule_data() == _SNAP_V1
    trigger.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("forced", "next_due_offset", "should_fetch"),
    [(False, -1.0, True), (False, 100.0, False), (True, 100.0, True)],
)
async def test_refresher_fetches_by_timer_or_request(forced: bool, next_due_offset: float, should_fetch: bool) -> None:
    """Цикл worker'а качает по таймеру или по флагу; иначе ждёт."""
    refresh = AsyncMock()
    next_due = time.monotonic() + next_due_offset
    with (
        patch.object(schedule_refresher, "pop_schedule_refresh_request", AsyncMock(return_value=forced)),
        patch.object(schedule_refresher, "refresh_schedule_in_background", refresh),
    ):
        new_due = await schedule_refresher._refresh_if_due(next_due)
    assert refresh.await_count == int(should_fetch)
    if should_fetch:
        refresh.assert_awaited_once_with(force=forced)
        assert new_due > time.monotonic()
    else:
        assert new_due == next_due


@pytest.mark.asyncio
async def test_snapshot_meta_contains_version_and_fetch_time() -> None:
    """save_schedule_snapshot добавляет в meta хэш версии и время загрузки."""
    from core import redis_cache

    # У redis pipeline set() синхронный (буферизует команду), await только у execute()
    pipe = MagicMock(execute=AsyncMock())
    client = AsyncMock()
    client.pipeline = lambda transaction: _AsyncCtx(pipe)
    with patch.object(redis_cache, "init_redis", AsyncMock(return_value=client)):
        await redis_cache.save_schedule_snapshot(_SNAP_V1, {"etag": None})
        await redis_cache.save_schedule_snapshot(_SNAP_V2, {"etag": None})

    metas = [c.args[1] for c in pipe.set.call_args_list if c.args[0] == redis_cache.SNAPSHOT_META_KEY]
    first, second = (json.loads(m) for m in metas)
    assert first["version"] != second["version"]
    assert abs(first["fetched_at"] - time.time()) < 5


class _AsyncCtx:
    """Минимальный async context manager для подмены redis pipeline."""

    def __init__(self, obj):
        self.obj = obj

    async def __aenter__(self):
        return self.obj

    async def __aexit__(self, *exc):
        return False
