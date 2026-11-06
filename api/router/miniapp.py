"""
Роутер Telegram Mini App и аутентификации тестеров Swagger UI.

Обеспечивает защищённый доступ к документации и эндпоинтам API через
валидацию HMAC-SHA256 подписи Telegram initData и управление сессионными куками.
"""

import asyncio
import secrets
from pathlib import Path

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.miniapp import (
    MiniappActionRequest,
    MiniappActionResult,
    MiniappAuthRequest,
    MiniappAuthResponse,
    MiniappCheckResponse,
    TesterActionResponse,
    TesterItemResponse,
    TesterListResponse,
)
from config import (
    ADMIN_USER_IDS,
    ALLOWED_USER_ID,
    API_SECRET_KEY,
    DEPUTY_USER_ID,
    MINIAPP_HTML_FILE_PATH,
    SESSION_MAX_AGE_SECONDS,
)
from core.background import spawn
from core.logger import get_logger
from services.achievement_events import on_profile_view
from services.achievement_service import award_achievement
from services.classmates_auth import find_classmate_by_tg_id
from services.gamification_registry import ACHIEVEMENTS_MAP
from services.login_tokens import LOGIN_REDIRECT_TARGETS, consume_login_token
from services.testers_manager import (
    add_tester,
    get_all_testers,
    get_tester_by_key,
    is_tester_allowed,
    remove_tester,
)
from utils.miniapp_auth import (
    generate_tester_session,
    validate_telegram_init_data,
    verify_tester_session,
)

log = get_logger("miniapp_router")

router = APIRouter(tags=["Telegram Mini App"], prefix="/miniapp")

_HTML_PATH = Path(MINIAPP_HTML_FILE_PATH)


def _set_tester_cookie(response: Response, user_id: int) -> None:
    """
    Устанавливает подписанную защищенную сессионную куку тестера.

    Использует флаги HttpOnly, Secure и SameSite=None для работы внутри iframe Telegram.
    Защищает от XSS атак и обеспечивает сохранение сессии в Swagger UI.

    Ничего не возвращает (модифицирует заголовок Set-Cookie ответа).
    """

    token = generate_tester_session(user_id)
    response.set_cookie(
        key="para_session",
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="none",
        secure=True,
    )


@router.get("", response_class=HTMLResponse)
async def serve_miniapp_page() -> HTMLResponse:
    """
    Отдаёт одностраничный интерфейс Telegram Mini App портала со встроенным Swagger UI.

    Считывает скомпилированный HTML-шаблон с диска сервера.
    В случае отсутствия файла отдает базовую разметку со статусом 200.

    Возвращает HTMLResponse с содержимым страницы портала.
    """

    # Дисковый I/O уводим в поток, чтобы не блокировать event loop на каждом открытии Mini App
    try:
        content = await asyncio.to_thread(_HTML_PATH.read_text, encoding="utf-8")
    except FileNotFoundError:
        log.warning("⚠️  Шаблон Mini App не найден: %s", _HTML_PATH)
        return HTMLResponse(content="<h1>para-api Mini App</h1>", status_code=200)
    return HTMLResponse(content=content)


async def _resolve_api_key_user(key: str) -> tuple[int, str, str] | None:
    """Определяет Telegram ID и профиль пользователя по мастер-ключу или ключу тестера."""
    clean = key.strip()
    if secrets.compare_digest(clean.encode("utf-8"), API_SECRET_KEY.encode("utf-8")):
        return ALLOWED_USER_ID, "Староста (Admin)", "admin"
    uid = await get_tester_by_key(clean)
    if uid and await is_tester_allowed(uid):
        cm = find_classmate_by_tg_id(uid)
        name = (cm.get("full_name") if isinstance(cm, dict) else getattr(cm, "full_name", None)) or f"Тестер {uid}"
        return uid, name, f"tester_{uid}"
    return None


@router.get("/login", include_in_schema=False)
async def login_by_token(
    t: str = Query(..., description="Одноразовый токен входа из бота"),
    next_target: str = Query(default="miniapp", alias="next"),
) -> Response:
    """
    Обменивает одноразовый токен из ссылки бота на сессионную куку.

    Токен гасится при первом использовании, поэтому в URL никогда не живёт
    постоянный ключ. next принимается только из whitelist — защита от open redirect.

    Возвращает redirect 303 на Mini App или Swagger UI, либо HTTP 401.
    """
    uid = await consume_login_token(t)
    if uid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login link expired or already used")
    target = LOGIN_REDIRECT_TARGETS.get(next_target, LOGIN_REDIRECT_TARGETS["miniapp"])
    redirect = RedirectResponse(url=target, status_code=status.HTTP_303_SEE_OTHER)
    # Не отдаём URL с токеном в Referer при переходах со страницы назначения
    redirect.headers["Referrer-Policy"] = "no-referrer"
    _set_tester_cookie(redirect, uid)
    log.info("🔑 Вход по одноразовой ссылке (user_id=%s) -> %s", uid, target)
    return redirect


async def _auth_by_key(api_key: str, response: Response) -> MiniappAuthResponse:
    """Проверяет ключ доступа и устанавливает сессионную куку тестера."""
    resolved = await _resolve_api_key_user(api_key)
    if not resolved:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    uid, name, uname = resolved
    _set_tester_cookie(response, uid)
    log.info("🔑 Успешный вход по API-ключу в MiniApp (user_id=%s, name=%s)", uid, name)
    return MiniappAuthResponse(user_id=uid, first_name=name, username=uname)


async def _auth_telegram_init(init_data: str, response: Response) -> MiniappAuthResponse:
    """Валидирует подпись Telegram initData и проверяет права студента или тестера."""
    info = validate_telegram_init_data(init_data)
    if not info or "id" not in info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram signature")
    uid = int(info["id"])
    is_classmate = bool(uid in ADMIN_USER_IDS or find_classmate_by_tg_id(uid) is not None)
    is_tester = await is_tester_allowed(uid)
    if not is_classmate and not is_tester:
        log.warning("🚫 Пользователь %s не в группе 1-КПД-3 и не в списке тестеров", uid)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")
    _set_tester_cookie(response, uid)

    spawn(award_achievement(uid, "bot_miniapp", None, info.get("first_name")))
    return MiniappAuthResponse(user_id=uid, first_name=info.get("first_name"), username=info.get("username"))


@router.post("/auth", response_model=MiniappAuthResponse)
async def authenticate_miniapp(payload: MiniappAuthRequest, response: Response) -> MiniappAuthResponse:
    """Аутентифицирует пользователя по Telegram initData или ключу доступа."""
    if payload.api_key:
        return await _auth_by_key(payload.api_key, response)
    if payload.init_data:
        return await _auth_telegram_init(payload.init_data, response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing auth credentials")


@router.get("/status", response_model=MiniappCheckResponse)
async def check_tester_status(para_session: str = Cookie(default=None)) -> MiniappCheckResponse:
    """
    Проверяет статус авторизации и наличие прав тестера по сессионной куке.

    Декодирует криптографическую подпись куки и сверяет пользователя со списком в Redis.
    Не выбрасывает ошибок при отсутствии сессии, а возвращает authenticated=False.

    Возвращает MiniappCheckResponse с флагами аутентификации и правами.
    """

    if not para_session:
        return MiniappCheckResponse(authenticated=False, is_tester=False)

    uid = verify_tester_session(para_session)
    if uid is None:
        return MiniappCheckResponse(authenticated=False, is_tester=False)

    allowed = await is_tester_allowed(uid)
    return MiniappCheckResponse(authenticated=True, user_id=uid, is_tester=allowed)


def resolve_action_uid(init_data: str | None, session: str | None) -> int | None:
    """Определяет Telegram ID инициатора действия из сессии или init_data."""
    if session:
        uid = verify_tester_session(session)
        if uid is not None:
            return uid
    if init_data:
        info = validate_telegram_init_data(init_data)
        if info and "id" in info and info["id"] is not None:
            return int(info["id"])
    return None


# Клиентские действия Mini App → ачивки. Сервер не может проверить, что тема
# правда включена, но эти ачивки — пасхалки интерфейса, а не журнальные заслуги.
MINIAPP_ACTION_ACHIEVEMENTS: dict[str, str] = {
    "matrix_theme": "egg_matrix",
    "konami_code": "egg_konami",
    "open_miniapp": "bot_miniapp",
    "all_tabs": "egg_api_hacker",
}


def _action_result(ach_id: str | None, unlocked: bool) -> MiniappActionResult:
    """Собирает ответ action-эндпоинта с паспортом открытой ачивки."""

    ach = ACHIEVEMENTS_MAP.get(ach_id or "")
    if not unlocked or not ach:
        return MiniappActionResult(status="ok", unlocked=False)
    return MiniappActionResult(
        status="ok", unlocked=True, achievement=ach.title, achievement_id=ach.id, xp=ach.xp_reward
    )


def require_group_member(uid: int | None) -> int:
    """
    Пропускает только одногруппников: валидный initData есть у любого, кто открыл бота.

    Возвращает uid или выбрасывает HTTP 401/403.
    """
    if uid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if uid not in ADMIN_USER_IDS and find_classmate_by_tg_id(uid) is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a group member")
    return uid


@router.post("/action", response_model=MiniappActionResult)
async def trigger_miniapp_action(
    payload: MiniappActionRequest, para_session: str | None = Cookie(default=None)
) -> MiniappActionResult:
    """Разблокирует клиентские достижения Mini App (пасхалки, темы, вкладки, профили)."""
    uid = require_group_member(resolve_action_uid(payload.init_data, para_session))

    if payload.action == "view_profile":
        unlocked = await on_profile_view(uid, payload.target or "")
        return _action_result("soc_solidarity", unlocked)
    ach_id = MINIAPP_ACTION_ACHIEVEMENTS.get(payload.action)
    if not ach_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown action")
    return _action_result(ach_id, await award_achievement(uid, ach_id))


@router.get("/testers", response_model=TesterListResponse, dependencies=[Depends(verify_api_or_tester)])
async def list_api_testers() -> TesterListResponse:
    """
    Возвращает список всех зарегистрированных тестеров Swagger UI.

    Помечает главных администраторов бота флагом is_admin=True.
    Используется для управления доступом к закрытой документации.

    Возвращает TesterListResponse со списком тестеров и их количеством.
    """

    uids = await get_all_testers()
    items = [TesterItemResponse(user_id=u, is_admin=(u in (ADMIN_USER_IDS | {DEPUTY_USER_ID}))) for u in uids]

    return TesterListResponse(count=len(items), testers=items)


@router.post("/testers/{user_id}", response_model=TesterActionResponse, dependencies=[Depends(verify_admin_access)])
async def api_add_tester(user_id: int) -> TesterActionResponse:
    """
    Добавляет пользователя в постоянный список тестеров API (Admin only).

    Сохраняет Telegram ID в Redis-множество тестеров.
    Выбрасывает HTTP 400 при невозможности добавления.

    Возвращает TesterActionResponse со статусом 'ok' и ID тестера.
    """

    success = await add_tester(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add tester")

    return TesterActionResponse(status="ok", user_id=user_id)


@router.delete("/testers/{user_id}", response_model=TesterActionResponse, dependencies=[Depends(verify_admin_access)])
async def api_remove_tester(user_id: int) -> TesterActionResponse:
    """
    Удаляет пользователя из списка авторизованных тестеров API (Admin only).

    Запрещает удаление главных администраторов проекта из белого списка.
    Выбрасывает HTTP 400 при попытке удаления админа или сбое хранилища.

    Возвращает TesterActionResponse со статусом 'ok' и ID удаленного тестера.
    """

    success = await remove_tester(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot remove admin or error")

    return TesterActionResponse(status="ok", user_id=user_id)
