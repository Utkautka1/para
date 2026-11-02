"""
Тесты секретной игры за «пульсом группы» (api/router/pulse.py) и скрытия секретных ачивок.

Проверяет:
  1. Роутер не виден в OpenAPI, а секретной ачивки нет в публичном каталоге
  2. Код игры отдаётся только по живому токену
  3. Итог без цепочки ударов в честном ритме не проходит
  4. Честный забег открывает ачивку и гасит токен
  5. Ритм ударов: рывки, паузы и стартовый счёт проверяются сервером
  6. В чужом профиле секретная ачивка вырезана, в своём — видна
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


class Clock:
    """Управляемое время для pulse.time.time — удары без реального ожидания."""

    def __init__(self) -> None:
        self.now = 1_000_000.0

    def time(self) -> float:
        return self.now


@pytest.fixture
def clock():
    fake = Clock()
    with patch.object(pulse.time, "time", fake.time):
        yield fake


async def _run(client: AsyncClient, clock: Clock, trace: str, beats: int, rate: float = 10.0) -> int:
    """Имитирует честный забег: удар каждые 2 секунды с темпом rate очков/с."""
    score = 0
    for _ in range(beats):
        await client.post(f"/miniapp/pulse/ecg/{trace}/beat", json={"score": score})
        clock.now += 2
        score += int(2 * rate)
    return score


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
    with patch.object(pulse, "award_achievement", award):
        async with _client() as client:
            trace = await _start(client)
            resp = await client.post(f"/miniapp/pulse/ecg/{trace}", json={"score": 5000})
    assert resp.json()["accepted"] is False
    award.assert_not_awaited()
    assert pulse._trace_key(trace) in redis.data


@pytest.mark.asyncio
async def test_waiting_without_beats_is_rejected(redis, clock) -> None:
    """Старый обход — подождать и отправить счёт — больше не работает."""
    award = AsyncMock(return_value=True)
    with patch.object(pulse, "award_achievement", award):
        async with _client() as client:
            trace = await _start(client)
            clock.now += 60
            resp = await client.post(f"/miniapp/pulse/ecg/{trace}", json={"score": 150})
    assert resp.json()["accepted"] is False
    award.assert_not_awaited()


@pytest.mark.asyncio
async def test_honest_run_unlocks_secret_once(redis, clock) -> None:
    award = AsyncMock(return_value=True)
    with patch.object(pulse, "award_achievement", award):
        async with _client() as client:
            trace = await _start(client)
            score = await _run(client, clock, trace, beats=8)
            resp = await client.post(f"/miniapp/pulse/ecg/{trace}", json={"score": score})
            again = await client.post(f"/miniapp/pulse/ecg/{trace}", json={"score": score})
    body = resp.json()
    assert body["accepted"] and body["unlocked"] and body["xp"] == 404
    award.assert_awaited_once_with(ALLOWED_USER_ID, pulse.SECRET_ACHIEVEMENT_ID)
    assert again.status_code == 404


@pytest.mark.asyncio
async def test_too_fast_rhythm_breaks_run(redis, clock) -> None:
    """Счёт, растущий быстрее честной игры, обрывает забег."""
    async with _client() as client:
        trace = await _start(client)
        await _run(client, clock, trace, beats=3)
        resp = await client.post(f"/miniapp/pulse/ecg/{trace}/beat", json={"score": 5000})
    assert resp.json()["steady"] is False


@pytest.mark.parametrize(
    ("beats", "score", "now", "ok"),
    [
        ([], 0, 0.0, True),
        ([], 500, 0.0, False),
        ([[0.0, 0]], 20, 2.0, True),
        ([[0.0, 0]], 100, 2.0, False),
        ([[0.0, 0]], 0, 2.0, False),
        ([[0.0, 0]], 70, 7.0, False),
        ([[0.0, 100]], 10, 2.0, True),
    ],
)
def test_next_beats_rhythm(beats: list, score: int, now: float, ok: bool) -> None:
    """Темп, паузы и перезапуск забега после гибели."""
    assert bool(pulse.next_beats(beats, score, now)) is ok


def test_early_beat_is_skipped() -> None:
    """Удар, склеенный джиттером с прошлым, не рвёт забег и не записывается."""
    beats = [[0.0, 0], [2.0, 20]]
    assert pulse.next_beats(beats, 25, 2.5) == beats


@pytest.mark.parametrize(
    ("beats", "score", "now", "ok"),
    [
        ([[t * 2.0, t * 20] for t in range(8)], 150, 15.0, True),
        ([[t * 2.0, t * 20] for t in range(3)], 150, 5.0, False),
        ([[t * 2.0, t * 20] for t in range(8)], 99, 15.0, False),
        ([[t * 2.0, t * 20] for t in range(8)], 500, 15.0, False),
    ],
)
def test_plausible_run(beats: list, score: int, now: float, ok: bool) -> None:
    assert pulse.is_plausible_run(beats, score, now) is ok


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
