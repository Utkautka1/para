"""
Unit-тесты для проверки устранения уязвимостей и узких горлышек (Аудит 2026).

Проверяет:
  1. Защиту POST /teachers/custom (требование прав администратора).
  2. Корректность работы GET /attendance/student/{fio} без падений.
  3. Блокировку опасных паттернов сброса кэша POST /system/cache/flush.
  4. Защиту от флуда и rate limiting на эндпоинте POST /solver/solve.
  5. Кэширование списка студентов в services/attendance_manager.py.
"""

from unittest.mock import AsyncMock, patch

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
