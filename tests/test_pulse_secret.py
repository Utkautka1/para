"""
Тесты секретной игры за «пульсом группы» (api/router/pulse.py) и скрытия секретных ачивок.

Проверяет:
  1. Роутер не виден в OpenAPI, а секретной ачивки нет в публичном каталоге
  2. Код игры отдаётся только по живому токену
  3. Счёт проверяется по времени: мгновенный POST с большим счётом не проходит
  4. Честный забег открывает ачивку и гасит токен
  5. В чужом профиле секретная ачивка вырезана, в своём — видна
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api import create_app
from api.router import pulse
from config import ALLOWED_USER_ID
from services.gamification import hide_secret_achievements
from services.gamification_models import StudentProfile
from utils.miniapp_auth import generate_tester_session


class FakeRedis:
    """Хранилище вместо core.redis_cache: cache_get / cache_set / cache_delete."""

    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.data.get(key)

    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self.data[key] = value

    async def delete(self, key: str) -> bool:
        return self.data.pop(key, None) is not None


@pytest.fixture
def redis():
    store = FakeRedis()
    with (
        patch.object(pulse, "cache_get", store.get),
        patch.object(pulse, "cache_set", store.set),
        patch.object(pulse, "cache_delete", store.delete),
    ):
        yield store


def _client() -> AsyncClient:
    client = AsyncClient(transport=ASGITransport(app=create_app()), base_url="https://test")
    client.cookies.set("para_session", generate_tester_session(ALLOWED_USER_ID))
    return client


async def _start(client: AsyncClient) -> str:
    resp = await client.post("/miniapp/pulse/ecg", json={})
    assert resp.status_code == 200
    return resp.json()["trace"]


def _age_trace(redis: FakeRedis, trace: str, seconds: float) -> None:
    """Сдвигает время выдачи токена в прошлое — как будто игра шла seconds секунд."""
    uid, issued = redis.data[pulse._trace_key(trace)].split(":")
    redis.data[pulse._trace_key(trace)] = f"{uid}:{float(issued) - seconds}"


@pytest.mark.asyncio
async def test_pulse_is_hidden_everywhere() -> None:
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url="https://test") as client:
        catalog = (await client.get("/gamification/achievements")).json()
        spec = create_app().openapi()
    assert all(a["id"] != pulse.SECRET_ACHIEVEMENT_ID for a in catalog["achievements"])
    assert not [path for path in spec["paths"] if "pulse" in path]


@pytest.mark.asyncio
async def test_script_requires_live_trace(redis) -> None:
    async with _client() as client:
        assert (await client.get("/miniapp/pulse/ecg.js", params={"t": "nope"})).status_code == 404
        trace = await _start(client)
        resp = await client.get("/miniapp/pulse/ecg.js", params={"t": trace})
    assert resp.status_code == 200
    assert "javascript" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_instant_high_score_is_rejected(redis) -> None:
    award = AsyncMock(return_value=True)
    with patch("services.achievement_service.award_achievement", award):
        async with _client() as client:
            trace = await _start(client)
            resp = await client.post(f"/miniapp/pulse/ecg/{trace}", json={"score": 5000})
    assert resp.json()["accepted"] is False
    award.assert_not_awaited()
    assert pulse._trace_key(trace) in redis.data


@pytest.mark.asyncio
async def test_honest_run_unlocks_secret_once(redis) -> None:
    award = AsyncMock(return_value=True)
    with patch("services.achievement_service.award_achievement", award):
        async with _client() as client:
            trace = await _start(client)
            _age_trace(redis, trace, 20)
            resp = await client.post(f"/miniapp/pulse/ecg/{trace}", json={"score": 250})
            again = await client.post(f"/miniapp/pulse/ecg/{trace}", json={"score": 250})
    body = resp.json()
    assert body["accepted"] and body["unlocked"] and body["xp"] == 404
    award.assert_awaited_once_with(ALLOWED_USER_ID, pulse.SECRET_ACHIEVEMENT_ID)
    assert again.status_code == 404


@pytest.mark.parametrize(("score", "elapsed", "ok"), [(99, 60, False), (100, 10, True), (300, 10, False)])
def test_plausible_score(score: int, elapsed: float, ok: bool) -> None:
    assert pulse.is_plausible_score(score, elapsed) is ok


def test_hide_secret_from_other_viewers() -> None:
    profile = StudentProfile(
        fio="Иванов Иван",
        short_fio="Иванов И.",
        attendance_pct=90.0,
        total_classes=10,
        present_count=9,
        late_count=0,
        excused_count=0,
        unexcused_count=1,
        rank_name="",
        rank_icon="",
        rank_description="",
        xp=504,
        unlocked_achievements=["bot_welcome", "egg_dino"],
    )
    assert hide_secret_achievements(profile, "Петров Пётр").unlocked_achievements == ["bot_welcome"]
    assert hide_secret_achievements(profile, None).unlocked_achievements == ["bot_welcome"]
    assert "egg_dino" in hide_secret_achievements(profile, "Иванов Иван").unlocked_achievements
    assert profile.unlocked_achievements == ["bot_welcome", "egg_dino"]


@pytest.mark.parametrize(
    ("identity", "expected"),
    [("classmate:1", "Иванов Иван"), ("tester:1", "Иванов Иван"), ("master_admin", None), ("classmate:x", None)],
)
def test_viewer_fio_for_classmate_session(identity: str, expected: str | None) -> None:
    from api.router import gamification as router

    with patch.object(router, "find_classmate_by_tg_id", return_value={"full_name": "Иванов Иван"}):
        assert router._viewer_fio(identity) == expected
