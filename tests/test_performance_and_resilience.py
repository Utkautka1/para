"""
Unit-тесты для подсистем оптимизации производительности и надежности.

Проверяет:
  1. Синглтон пула соединений Redis (core/redis.py)
  2. Кэширование и мгновенное восстановление снимка расписания (services/redis_cache.py)
  3. Надежную обработку очереди задач ДЗ (BLMOVE, ACK, Recovery)
  4. Сохранение идемпотентных состояний напоминаний и топика
  5. Отслеживание и очистку временных сообщений по расписанию в Redis ZSET
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.api_client import _get_client
from core.redis import get_redis_pool
from core.redis_cache import (
    ack_hw_task,
    get_expired_messages_for_cleanup,
    get_topic_state_redis,
    is_reminder_sent,
    load_schedule_snapshot,
    mark_reminder_sent,
    pop_hw_task,
    recover_stale_hw_tasks,
    register_message_for_cleanup,
    save_schedule_snapshot,
    set_topic_state_redis,
)
from services.schedule_parser import init_schedule_cache_from_redis


def test_redis_connection_pool_configuration() -> None:
    """Проверяет корректность параметров пула соединений Redis."""
    pool = get_redis_pool()
    assert pool.max_connections == 20
    assert pool.connection_kwargs.get("socket_keepalive") is True
    assert pool.connection_kwargs.get("health_check_interval") == 30


def test_api_client_limits() -> None:
    """Проверяет настройку пула соединений в API клиенте."""
    client = _get_client()
    assert client._transport._pool._max_keepalive_connections == 10
    assert client._transport._pool._max_connections == 20


@pytest.mark.asyncio
async def test_save_and_load_schedule_snapshot() -> None:
    """Проверяет сохранение и чтение снимка расписания из Redis."""
    mock_redis = MagicMock()
    pipe = MagicMock()
    pipe.set = MagicMock()
    pipe.execute = AsyncMock()
    mock_redis.pipeline.return_value.__aenter__.return_value = pipe
    snap_data = {"subjects": ["Математика"]}
    meta_data = {"etag": "123", "last_modified": "Sat"}

    with patch("core.redis_cache.init_redis", AsyncMock(return_value=mock_redis)):
        await save_schedule_snapshot(snap_data, meta_data)
        assert pipe.set.call_count == 2

    mock_redis.get = AsyncMock(side_effect=[json.dumps(snap_data), json.dumps(meta_data)])
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=mock_redis)):
        snap, meta = await load_schedule_snapshot()
        assert snap == snap_data
        assert meta["etag"] == "123"


@pytest.mark.asyncio
async def test_reminder_sent_state() -> None:
    """Проверяет проверку и отметку отправленного напоминания."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "1"
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=mock_redis)):
        sent = await is_reminder_sent("2026-10-04_1_0_Math")
        assert sent is True
        await mark_reminder_sent("2026-10-04_1_0_Math")
        mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_topic_state_redis() -> None:
    """Проверяет чтение и запись ID главного сообщения в Redis."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = "54321"
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=mock_redis)):
        msg_id = await get_topic_state_redis()
        assert msg_id == 54321
        await set_topic_state_redis(99999)
        mock_redis.set.assert_called_with("topic:main_msg_id", "99999")


@pytest.mark.asyncio
async def test_reliable_queue_pop_and_ack() -> None:
    """Проверяет перемещение задачи в processing и подтверждение ack."""
    task = {"message_id": 101, "prompt": "реши 2+2"}
    mock_redis = AsyncMock()
    mock_redis.blmove.return_value = json.dumps(task)
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=mock_redis)):
        popped = await pop_hw_task(timeout=1)
        assert popped == task
        await ack_hw_task(task)
        mock_redis.lrem.assert_called_once()


@pytest.mark.asyncio
async def test_recover_stale_hw_tasks() -> None:
    """Проверяет восстановление зависших задач из processing очереди."""
    mock_redis = AsyncMock()
    mock_redis.rpoplpush.side_effect = ["task1", "task2", None]
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=mock_redis)):
        recovered = await recover_stale_hw_tasks()
        assert recovered == 2
        assert mock_redis.rpoplpush.call_count == 3


@pytest.mark.asyncio
async def test_message_cleanup_registration() -> None:
    """Проверяет регистрацию и извлечение сообщений для очистки."""
    mock_redis = AsyncMock()
    mock_redis.zrangebyscore.return_value = ["-100123:555", "-100123:556"]
    with patch("core.redis_cache.init_redis", AsyncMock(return_value=mock_redis)):
        await register_message_for_cleanup(-100123, 555, delay_sec=60)
        mock_redis.zadd.assert_called_once()
        expired = await get_expired_messages_for_cleanup()
        assert len(expired) == 2
        assert expired[0] == (-100123, 555)


@pytest.mark.asyncio
async def test_schedule_parser_cold_start_from_redis() -> None:
    """Проверяет инициализацию кэша парсера из снимка Redis."""
    snap = {"subjects": ["Информатика"]}
    meta = {"etag": "etag-xyz", "last_modified": "Sun", "published_at": "2026-10-04"}
    with patch("core.redis_cache.load_schedule_snapshot", AsyncMock(return_value=(snap, meta))):
        success = await init_schedule_cache_from_redis(1000.0)
        assert success is True


@pytest.mark.asyncio
async def test_get_day_schedule_cached_miss() -> None:
    """Проверяет промах L1 Redis-кэша и заполнение из API."""
    from datetime import date
    from bot.handlers.user.schedule import get_day_schedule_cached
    from services.models import Lesson
    test_d = date(2026, 10, 5)
    sample_lessons = [
        Lesson(
            subject="Физика", teacher="Сидоров С.С.", room="202",
            time_str="08:30-10:00", period=0, is_remote=False,
            lesson_type="Лек", address="Корпус 2"
        )
    ]
    with patch("bot.handlers.user.schedule.cache_get", AsyncMock(return_value=None)), \
         patch("bot.handlers.user.schedule.cache_set", AsyncMock()) as mock_set, \
         patch("bot.handlers.user.schedule.get_api_schedule_for_date", AsyncMock(return_value=sample_lessons)):
        text, lessons = await get_day_schedule_cached(test_d)
        assert len(lessons) == 1
        assert "Физика" in text
        mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_get_day_schedule_cached_hit() -> None:
    """Проверяет попадание в L1 Redis-кэш без обращения к API."""
    from datetime import date
    from bot.handlers.user.schedule import get_day_schedule_cached
    test_d = date(2026, 10, 5)
    cached_payload = json.dumps({"text": "Кэшированный текст", "lessons": []})
    with patch("bot.handlers.user.schedule.cache_get", AsyncMock(return_value=cached_payload)), \
         patch("bot.handlers.user.schedule.get_api_schedule_for_date", AsyncMock()) as mock_api:
        text, lessons = await get_day_schedule_cached(test_d)
        assert text == "Кэшированный текст"
        assert len(lessons) == 0
        mock_api.assert_not_called()


def test_classmates_registry_in_memory_mtime_cache() -> None:
    """Проверяет in-memory кэширование реестра студентов по mtime файла."""
    from services.classmates_auth import clear_registry_cache, load_classmates_registry
    clear_registry_cache()
    mock_data = [{"full_name": "Тест Студент", "tg_id": 111222}]
    with patch("os.path.getmtime", return_value=12345.0), \
         patch("services.classmates_auth.sync_load_json", return_value=mock_data) as mock_load:
        reg1 = load_classmates_registry()
        reg2 = load_classmates_registry()
        assert reg1 == mock_data
        assert reg2 == mock_data
        assert mock_load.call_count == 1
    clear_registry_cache()


@pytest.mark.asyncio
async def test_concurrent_send_reminders() -> None:
    """Проверяет параллельную доставку напоминаний нескольким подписчикам."""
    from services.models import Lesson
    from services.notifier import send_single_reminder
    lesson = Lesson(
        subject="Химия", teacher="Петров П.П.", room="303",
        time_str="10:05-11:30", period=1, is_remote=False,
        lesson_type="Лаб", address="Корпус 1"
    )
    targets = {111, 222, 333}
    with patch("db.subscribers.load_subscribers", return_value=targets), \
         patch("services.notifier.bot.send_message", AsyncMock()) as mock_send:
        await send_single_reminder(lesson)
        assert mock_send.call_count == 3


@pytest.mark.asyncio
async def test_retry_after_middleware_success() -> None:
    """Проверяет прозрачный retry при получении TelegramRetryAfter."""
    from aiogram.exceptions import TelegramRetryAfter

    from bot.middlewares.retry import RetryAfterMiddleware
    mw = RetryAfterMiddleware()
    handler = AsyncMock(side_effect=[TelegramRetryAfter(method=MagicMock(), message="Too Fast", retry_after=0.01), "success"])
    event = MagicMock()
    with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
        res = await mw(handler, event, {})
        assert res == "success"
        assert handler.call_count == 2
        mock_sleep.assert_called_once_with(0.01)


@pytest.mark.asyncio
async def test_collect_health_summary() -> None:
    """Проверяет формирование диагностического текста в админке."""
    from bot.handlers.admin.panel import _collect_health_summary
    with patch("db.subscribers.load_subscribers", return_value={1, 2}), \
         patch("services.classmates_auth.load_classmates_registry", return_value=[{"tg_id": 1}]), \
         patch("bot.handlers.admin.panel.fetch_teachers", AsyncMock(return_value={"count": 15})), \
         patch("integrations.yandex_docs.get_effective_yandex_cookie", AsyncMock(return_value="cookie=123")), \
         patch("core.redis_cache.init_redis", AsyncMock(return_value=None)):
        summary = await _collect_health_summary()
        assert "ДИАГНОСТИКА СИСТЕМЫ" in summary
        assert "15" in summary
        assert "Подписчики ЛС:</b> <code>2</code>" in summary
        assert "Сессия Яндекс:</b> ✅ Активна" in summary


@pytest.mark.asyncio
async def test_callback_throttle_middleware() -> None:
    """Проверяет подавление повторных кликов через CallbackThrottleMiddleware."""
    from aiogram.types import CallbackQuery

    from bot.middlewares.throttling import CallbackThrottleMiddleware
    mw = CallbackThrottleMiddleware()
    event = MagicMock(spec=CallbackQuery)
    event.from_user = MagicMock(id=123)
    event.data = "sched:refresh"
    event.answer = AsyncMock()
    handler = AsyncMock(return_value="handled")

    res1 = await mw(handler, event, {})
    assert res1 == "handled"
    assert handler.call_count == 1

    res2 = await mw(handler, event, {})
    assert res2 is None
    assert handler.call_count == 1
    event.answer.assert_called_with("⏳ Подождите секунду...", show_alert=False)


@pytest.mark.asyncio
async def test_docx_singleflight_cache_freshness() -> None:
    """Проверяет защиту от повторного скачивания docx при кулдауне."""
    import time

    import integrations.docx_parser as dp_mod
    cached = {"teacher": {"full_name": "T", "link_info": "L"}}
    with (
        patch.object(dp_mod, "_CACHE", (time.time(), cached)),
        patch.object(dp_mod, "fetch_docx_bytes", AsyncMock()) as mock_fetch,
    ):
        res = await dp_mod.get_teacher_links(force_refresh=True)
        assert "teacher" in res
        mock_fetch.assert_not_called()


@pytest.mark.asyncio
async def test_week_schedule_single_fetch() -> None:
    """Проверяет однократный fetch_schedule_data при get_week_schedule с force."""
    from datetime import date

    from services.schedule_parser import get_week_schedule
    with patch("services.schedule_parser.fetch_schedule_data", AsyncMock()) as mock_fetch, \
         patch("services.schedule_parser.get_schedule_for_date", AsyncMock(return_value=[])) as mock_day:
        res = await get_week_schedule(date(2026, 10, 5), force_refresh=True)
        assert len(res) == 6
        mock_fetch.assert_called_once_with(force_refresh=True)
        assert mock_day.call_count == 6

