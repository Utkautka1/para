"""
Роутер секретной игры Mini App, спрятанной за «пульсом группы».

Не попадает в OpenAPI (include_in_schema=False) и в каталог ачивок: о нём не
должно быть ни строчки в Swagger, документации и витрине квестов.

Защита от выдачи ачивки скриптом:
  1. /ecg выдаёт одноразовый trace-токен (Redis, TTL 1 час)
  2. Код игры (/ecg.js) отдаётся только по живому токену — в miniapp.html его нет
  3. Во время забега клиент каждые ~2 с шлёт «удар» /ecg/{trace}/beat с текущим счётом.
     Сервер сам замеряет время между ударами и проверяет ритм: счёт растёт
     со скоростью честной игры, без пауз и рывков. Сбой ритма обнуляет забег
  4. /ecg/{trace} принимает итог, только если за ним стоит цепочка из BEATS_REQUIRED
     ударов и финальный счёт продолжает тот же ритм. Токен гасится только при выдаче

Скрипт по-прежнему может имитировать удары, но для этого ему придётся
«бежать» в реальном времени с правдоподобным темпом — одним POST уже не обойтись.
"""

import asyncio
import json
import secrets
import time
from pathlib import Path

from fastapi import APIRouter, Cookie, HTTPException, Query, status
from fastapi.responses import Response

from api.router.miniapp import require_group_member, resolve_action_uid
from api.schemas.pulse import (
    PulseBeatResponse,
    PulseReadingRequest,
    PulseReadingResponse,
    PulseTraceRequest,
    PulseTraceResponse,
)
from config import MINIAPP_HTML_FILE_PATH
from core.logger import get_logger
from core.redis_cache import cache_delete, cache_get, cache_set
from services.achievement_service import award_achievement
from services.gamification_registry import ACHIEVEMENTS_MAP

log = get_logger("pulse_router")

router = APIRouter(prefix="/miniapp/pulse", include_in_schema=False)

# Код игры лежит рядом с шаблоном Mini App, но отдаётся только по токену
_GAME_PATH = Path(MINIAPP_HTML_FILE_PATH).with_name("pulse.js")

# Секретная ачивка, которую открывает игра
SECRET_ACHIEVEMENT_ID = "egg_dino"

# Время жизни токена записи (секунды)
TRACE_TTL_SECONDS = 3600

# Минимальный счёт для ачивки — примерно 10 секунд честного бега
MIN_SCORE = 100

# Темп честной игры: ~10 очков/с на старте, до ~20 на максимальной скорости.
# Границы шире из-за сетевого джиттера между ударами и просадок FPS на слабых телефонах
MIN_POINTS_PER_SECOND = 3
MAX_POINTS_PER_SECOND = 30

# Удар раньше MIN_BEAT_GAP_SECONDS после прошлого пропускается (джиттер сети склеил два),
# разрыв дольше MAX_BEAT_GAP_SECONDS (свернули вкладку, пауза) обрывает забег
MIN_BEAT_GAP_SECONDS = 1.0
MAX_BEAT_GAP_SECONDS = 6.0

# Сколько ударов должно стоять за итогом — при шаге ~2 с это ~8 секунд игры
BEATS_REQUIRED = 4


def _trace_key(trace: str) -> str:
    """Ключ Redis для токена записи."""
    return f"pulse:trace:{trace}"


@router.post("/ecg", response_model=PulseTraceResponse)
async def start_trace(
    payload: PulseTraceRequest, para_session: str | None = Cookie(default=None)
) -> PulseTraceResponse:
    """Начинает запись кардиограммы: выдаёт одноразовый токен игры."""
    uid = require_group_member(resolve_action_uid(payload.init_data, para_session))
    trace = secrets.token_urlsafe(16)
    await _save_trace(trace, {"uid": uid, "beats": []})
    log.debug("Запись пульса начата: user_id=%s", uid)
    return PulseTraceResponse(trace=trace)


async def _load_trace(trace: str) -> dict:
    """
    Достаёт состояние записи: владелец и удары текущего забега.

    Возвращает {"uid": int, "beats": [[unix-время, счёт], ...]} или выбрасывает HTTP 404.
    """
    raw = await cache_get(_trace_key(trace))
    if not raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return json.loads(raw)


async def _save_trace(trace: str, state: dict) -> None:
    """Сохраняет состояние записи; TTL продлевается, пока игра идёт."""
    await cache_set(_trace_key(trace), json.dumps(state), ttl=TRACE_TTL_SECONDS)


async def _load_owned_trace(trace: str, para_session: str | None) -> dict:
    """
    Достаёт запись и проверяет, что её продолжает тот же пользователь.

    Возвращает состояние записи или выбрасывает HTTP 404 (чужая или неживая запись).
    """
    state = await _load_trace(trace)
    if resolve_action_uid(None, para_session) not in (None, state["uid"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    return state


@router.get("/ecg.js")
async def serve_trace_script(t: str = Query(..., max_length=64)) -> Response:
    """Отдаёт код игры только владельцу живого токена."""
    await _load_trace(t)
    script = await asyncio.to_thread(_GAME_PATH.read_text, encoding="utf-8")
    return Response(content=script, media_type="text/javascript", headers={"Cache-Control": "no-store"})


def is_steady_rhythm(prev: list[float], score: int, now: float) -> bool:
    """
    Проверяет, что счёт вырос от прошлого удара с темпом честной игры.

    Возвращает True, если пауза между ударами и скорость набора очков в допустимых границах.
    """
    gap = now - prev[0]
    return gap <= MAX_BEAT_GAP_SECONDS and MIN_POINTS_PER_SECOND <= (score - prev[1]) / gap <= MAX_POINTS_PER_SECOND


def next_beats(beats: list[list[float]], score: int, now: float) -> list[list[float]]:
    """
    Добавляет удар к забегу или начинает новый.

    Счёт ниже прошлого — игрок погиб и начал заново: забег стартует с этого удара,
    если счёт ещё стартовый. Слишком ранний удар пропускается, сбой ритма обнуляет забег.

    Возвращает новый список ударов (пустой — забег сорван).
    """
    if not beats or score < beats[-1][1]:
        is_fresh_start = score <= MAX_POINTS_PER_SECOND * MAX_BEAT_GAP_SECONDS
        return [[now, score]] if is_fresh_start else []
    if now - beats[-1][0] < MIN_BEAT_GAP_SECONDS:
        return beats
    return [*beats, [now, score]] if is_steady_rhythm(beats[-1], score, now) else []


@router.post("/ecg/{trace}/beat", response_model=PulseBeatResponse)
async def record_beat(
    trace: str, payload: PulseReadingRequest, para_session: str | None = Cookie(default=None)
) -> PulseBeatResponse:
    """Записывает удар кардиограммы — промежуточный счёт идущего забега."""
    state = await _load_owned_trace(trace, para_session)
    beats = next_beats(state.get("beats", []), payload.score, time.time())
    if not beats:
        log.debug("Ритм забега сорван: user_id=%s, score=%s", state["uid"], payload.score)
    await _save_trace(trace, {**state, "beats": beats})
    return PulseBeatResponse(steady=bool(beats))


def is_plausible_run(beats: list[list[float]], score: int, now: float) -> bool:
    """
    Проверяет итог забега: достаточно ударов, счёт не ниже порога и продолжает ритм.

    Возвращает True, если итог можно засчитать.
    """
    if len(beats) < BEATS_REQUIRED or score < MIN_SCORE or score < beats[-1][1]:
        return False
    gap = now - beats[-1][0]
    return gap <= MAX_BEAT_GAP_SECONDS and score - beats[-1][1] <= gap * MAX_POINTS_PER_SECOND


@router.post("/ecg/{trace}", response_model=PulseReadingResponse)
async def finish_trace(
    trace: str, payload: PulseReadingRequest, para_session: str | None = Cookie(default=None)
) -> PulseReadingResponse:
    """Принимает счёт забега и открывает секретную ачивку за честную игру."""
    state = await _load_owned_trace(trace, para_session)
    uid = state["uid"]
    if not is_plausible_run(state.get("beats", []), payload.score, time.time()):
        log.debug("Забег не засчитан: user_id=%s, score=%s", uid, payload.score)
        await _save_trace(trace, {**state, "beats": []})
        return PulseReadingResponse(accepted=False)
    await cache_delete(_trace_key(trace))

    ach = ACHIEVEMENTS_MAP[SECRET_ACHIEVEMENT_ID]
    unlocked = await award_achievement(uid, SECRET_ACHIEVEMENT_ID)
    log.info("🦖 Забег засчитан: user_id=%s, score=%s, новая ачивка=%s", uid, payload.score, unlocked)
    return PulseReadingResponse(accepted=True, unlocked=unlocked, title=ach.title, icon=ach.icon, xp=ach.xp_reward)
