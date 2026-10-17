"""
Unit-тесты для проверки устранения уязвимостей и узких горлышек (Аудит 2026).

Проверяет:
  1. Защиту POST /teachers/custom (требование прав администратора).
  2. Корректность работы GET /attendance/student/{fio} без падений.
  3. Блокировку опасных паттернов сброса кэша POST /system/cache/flush.
  4. Защиту от флуда и rate limiting на эндпоинте POST /solver/solve.
  5. Кэширование списка студентов в services/attendance_manager.py.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api import create_app
from config import API_SECRET_KEY


@pytest.mark.asyncio
async def test_teachers_custom_requires_admin() -> None:
    """Проверяет отклонение запроса POST /teachers/custom для не-админа."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Тестер без админских прав (uid 999999)
        with patch("api.deps._resolve_key_identity", new=AsyncMock(return_value="tester:999999")):
            payload = {"last_name": "Тестов", "full_name": "Тестов Т.Т.", "link_info": "https://zoom.us"}
            res = await client.post("/teachers/custom", json=payload, headers={"X-API-Key": "test_key"})
            assert res.status_code == 403


@pytest.mark.asyncio
async def test_attendance_student_arg_order_fix() -> None:
    """Проверяет, что эндпоинт GET /attendance/student/{fio} не падает с AttributeError."""
    app = create_app()
    transport = ASGITransport(app=app)
    fake_stats = {
        "Иванов Иван": {
            "fio": "Иванов Иван",
            "total": {"П": 10, "О": 1, "У": 0, "Н": 2},
            "months": {"СЕНТ": {"П": 10, "О": 1, "У": 0, "Н": 2}},
        }
    }
    with patch("api.router.attendance.fetch_all_time_attendance", new=AsyncMock(return_value=fake_stats)):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {"X-API-Key": API_SECRET_KEY}
            res = await client.get("/attendance/student/Иванов", headers=headers)
            assert res.status_code == 200
            data = res.json()
            assert data["fio"] == "Иванов Иван"
            assert data["total"]["П"] == 10


@pytest.mark.asyncio
async def test_cache_flush_dangerous_pattern_blocked() -> None:
    """Проверяет блокировку опасных масок сброса кэша Redis (например, * или api:*)."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-Key": API_SECRET_KEY}
        for bad_pattern in ["*", "", "*:*", "api:*", "hw:tasks:*"]:
            res = await client.post("/system/cache/flush", json={"pattern": bad_pattern}, headers=headers)
            assert res.status_code == 400


@pytest.mark.asyncio
async def test_solver_solve_rate_limit_exceeded() -> None:
    """Проверяет срабатывание 429 Too Many Requests при превышении лимита solve."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("api.deps._resolve_key_identity", new=AsyncMock(return_value="tester:888888")), \
             patch("api.router.solver.init_redis") as mock_redis, \
             patch("api.router.solver.solve_homework", new=AsyncMock(return_value="Решение")):
            client_mock = AsyncMock()
            client_mock.incr = AsyncMock(return_value=6)  # 6-й запрос превышает лимит 5
            client_mock.expire = AsyncMock()
            mock_redis.return_value = client_mock
            res = await client.post("/solver/solve", json={"prompt": "Решите задачу номер 1"}, headers={"X-API-Key": "key"})
            assert res.status_code == 429

            assert "Too many solver requests" in res.json()["detail"]


@pytest.mark.asyncio
async def test_fetch_target_students_redis_caching() -> None:
    """Проверяет быстрое чтение списка студентов из Redis кэша без скачивания WOPI."""
    from datetime import date

    from services.attendance_manager import fetch_target_students
    fake_list = [(5, "Иванов И.И."), (6, "Петров П.П.")]
    with patch("services.attendance_manager.get_redis") as mock_r, \
         patch("services.attendance_manager._fetch_students_from_wopi") as mock_wopi:
        client_mock = AsyncMock()
        import json
        client_mock.get = AsyncMock(return_value=json.dumps(fake_list))
        mock_r.return_value = client_mock
        res = await fetch_target_students(date(2026, 10, 5))
        assert len(res) == 2
        assert res[0] == (5, "Иванов И.И.")
        mock_wopi.assert_not_called()


def _make_fake_lesson():
    """Создает тестовый объект занятия для проверки L1 кэша."""
    from services.models import Lesson
    return Lesson(
        period=1, time_str="10:10-11:40", subject="Философия",
        lesson_type="Лек", teacher="Смирнов", is_remote=False,
        room="202", address="Цветочная", subgroup=0, is_stream=False
    )


@pytest.mark.asyncio
async def test_schedule_l1_in_memory_caching() -> None:
    """Проверяет мгновенную отдачу из L1 _RESOLVED_DAY_CACHE без повторного парсинга."""
    from datetime import date

    from services.schedule_parser import (
        _RESOLVED_DAY_CACHE,
        clear_resolved_day_cache,
        get_schedule_for_date,
    )
    target = date(2026, 10, 19)
    clear_resolved_day_cache()
    fake_lesson = _make_fake_lesson()
    with patch("services.schedule_parser.fetch_schedule_data", new=AsyncMock(return_value={"schedule": {}})), \
         patch("services.schedule_parser._extract_lessons_for_day", return_value=[fake_lesson]) as mock_ext:
        res1 = await get_schedule_for_date(target)
        assert len(res1) == 1 and res1[0].subject == "Философия"
        res2 = await get_schedule_for_date(target)
        assert res2 == res1 and mock_ext.call_count == 1
        clear_resolved_day_cache()
        assert target not in _RESOLVED_DAY_CACHE


@pytest.mark.asyncio
async def test_system_flush_clears_l1_schedule_cache() -> None:
    """Проверяет, что сброс кэша sched:* очищает локальный L1 кэш уроков."""
    from datetime import date

    from services.models import Lesson
    from services.schedule_parser import _RESOLVED_DAY_CACHE

    app = create_app()
    target = date(2026, 10, 20)
    fake_lesson = Lesson(
        period=1, time_str="10:10-11:40", subject="Информатика",
        lesson_type="Пр", teacher="Петров", is_remote=False,
        room="101", address="Вознесенский", subgroup=0, is_stream=False
    )
    _RESOLVED_DAY_CACHE[target] = [fake_lesson]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("api.deps.verify_admin_access", return_value=True), \
             patch("api.router.system.cache_flush", new=AsyncMock(return_value=5)):
            headers = {"X-API-Key": API_SECRET_KEY}
            res = await client.post("/system/cache/flush", json={"pattern": "sched:*"}, headers=headers)
            assert res.status_code == 200
            assert target not in _RESOLVED_DAY_CACHE


@pytest.mark.asyncio
async def test_toggle_notify_uses_cached_schedule() -> None:
    """Проверяет, что тумблер уведомлений берет пары из кэша без сетевого запроса к API."""
    from bot.handlers.user.schedule import cb_toggle_notify
    cb = MagicMock()
    cb.from_user.id = 111
    cb.message = AsyncMock()
    cb.answer = AsyncMock()

    with patch("bot.handlers.user.schedule.toggle_subscriber", return_value=True), \
         patch("bot.handlers.user.schedule.get_day_schedule_cached", new=AsyncMock(return_value=("текст", []))) as mock_cache, \
         patch("bot.handlers.user.schedule.get_api_schedule_for_date", new=AsyncMock()) as mock_api:
        await cb_toggle_notify(cb)
        mock_cache.assert_awaited_once()
        mock_api.assert_not_awaited()


@pytest.mark.asyncio
async def test_public_copy_shows_alert() -> None:
    """Проверяет, что копирование реквизитов открывает всплывающее окно (show_alert=True)."""
    from bot.handlers.user.public_copy import cb_public_copy_value
    cb = MagicMock()
    cb.data = "copy:123456"
    cb.from_user.id = 111
    cb.answer = AsyncMock()

    await cb_public_copy_value(cb)
    cb.answer.assert_awaited_once_with("Скопировано: 123456", show_alert=True)


def test_redis_auth_pool_configuration() -> None:
    """Проверяет передачу REDIS_PASSWORD в пул соединений Redis."""
    from core import redis as redis_module
    try:
        with patch("core.redis.ConnectionPool") as mock_pool_cls:
            redis_module._pool = None
            redis_module.get_redis_pool()
            mock_pool_cls.assert_called_once()
            assert "password" in mock_pool_cls.call_args.kwargs
            assert mock_pool_cls.call_args.kwargs["password"] is not None
    finally:
        redis_module._pool = None


def test_config_requires_redis_password() -> None:
    """Проверяет выброс ValueError при отсутствии обязательного REDIS_PASSWORD."""
    from config import get_required_env
    with patch.dict("os.environ", {}, clear=True), pytest.raises(ValueError, match="REDIS_PASSWORD"):
        get_required_env("REDIS_PASSWORD")


@pytest.mark.asyncio
async def test_solver_payload_length_limits() -> None:
    """Проверяет валидацию 422 при превышении лимита размера промпта."""
    from fastapi import FastAPI
    from httpx import ASGITransport, AsyncClient

    from api.deps import verify_api_or_tester
    from api.router.solver import router
    from config import HW_MAX_PROMPT_TEXT_LENGTH

    test_app = FastAPI()
    test_app.dependency_overrides[verify_api_or_tester] = lambda: "test_user"
    test_app.include_router(router)
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        too_long_prompt = "a" * (HW_MAX_PROMPT_TEXT_LENGTH + 10)
        res = await client.post("/solver/solve", json={"prompt": too_long_prompt})
        assert res.status_code == 422



