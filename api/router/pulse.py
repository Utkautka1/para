"""
Роутер секретной игры Mini App, спрятанной за «пульсом группы».

Не попадает в OpenAPI (include_in_schema=False) и в каталог ачивок: о нём не
должно быть ни строчки в Swagger, документации и витрине квестов.

Защита от выдачи ачивки одним POST-запросом:
  1. /ecg выдаёт одноразовый trace-токен (Redis, TTL 1 час) и фиксирует время выдачи
  2. Код игры (/ecg.js) отдаётся только по живому токену — в miniapp.html его нет
  3. /ecg/{trace} принимает счёт, только если он правдоподобен для прошедшего
     времени (не быстрее MAX_POINTS_PER_SECOND) и не ниже MIN_SCORE.
     Токен гасится только при выдаче — после неудачного забега можно играть снова
"""

import asyncio
import secrets
import time
from pathlib import Path

from fastapi import APIRouter, Cookie, HTTPException, Query, status
from fastapi.responses import Response

from api.router.miniapp import require_group_member, resolve_action_uid
from api.schemas.pulse import PulseReadingRequest, PulseReadingResponse, PulseTraceRequest, PulseTraceResponse
from config import MINIAPP_HTML_FILE_PATH
from core.logger import get_logger
from core.redis_cache import cache_delete, cache_get, cache_set

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

# Игра начисляет ~10 очков/с и разгоняется до ~20; 25 с запасом на лаги таймера
MAX_POINTS_PER_SECOND = 25


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
    await cache_set(_trace_key(trace), f"{uid}:{time.time():.3f}", ttl=TRACE_TTL_SECONDS)
    log.debug("Запись пульса начата: user_id=%s", uid)
    return PulseTraceResponse(trace=trace)


async def _load_trace(trace: str) -> tuple[int, float]:
    """
    Достаёт владельца и время выдачи токена.

    Возвращает (uid, unix-время выдачи) или выбрасывает HTTP 404.
    """
    raw = await cache_get(_trace_key(trace))
    if not raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    uid, issued = raw.split(":", 1)
    return int(uid), float(issued)


@router.get("/ecg.js")
async def serve_trace_script(t: str = Query(..., max_length=64)) -> Response:
    """Отдаёт код игры только владельцу живого токена."""
    await _load_trace(t)
    script = await asyncio.to_thread(_GAME_PATH.read_text, encoding="utf-8")
    return Response(content=script, media_type="text/javascript", headers={"Cache-Control": "no-store"})


def is_plausible_score(score: int, elapsed_seconds: float) -> bool:
    """Проверяет, что счёт достижим за прошедшее с выдачи токена время."""
    return MIN_SCORE <= score <= elapsed_seconds * MAX_POINTS_PER_SECOND


@router.post("/ecg/{trace}", response_model=PulseReadingResponse)
async def finish_trace(
    trace: str, payload: PulseReadingRequest, para_session: str | None = Cookie(default=None)
) -> PulseReadingResponse:
    """Принимает счёт забега и открывает секретную ачивку за честную игру."""
    uid, issued = await _load_trace(trace)
    if resolve_action_uid(None, para_session) not in (None, uid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    if not is_plausible_score(payload.score, time.time() - issued):
        log.debug("Забег не засчитан: user_id=%s, score=%s", uid, payload.score)
        return PulseReadingResponse(accepted=False)
    await cache_delete(_trace_key(trace))
    from services.achievement_service import award_achievement
    from services.gamification_registry import ACHIEVEMENTS_MAP

    ach = ACHIEVEMENTS_MAP[SECRET_ACHIEVEMENT_ID]
    unlocked = await award_achievement(uid, SECRET_ACHIEVEMENT_ID)
    log.info("🦖 Забег засчитан: user_id=%s, score=%s, новая ачивка=%s", uid, payload.score, unlocked)
    return PulseReadingResponse(accepted=True, unlocked=unlocked, title=ach.title, icon=ach.icon, xp=ach.xp_reward)
