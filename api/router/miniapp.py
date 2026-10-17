"""
Роутер Telegram Mini App и аутентификации тестеров Swagger UI.

Обеспечивает защищённый доступ к документации и эндпоинтам API через
валидацию HMAC-SHA256 подписи Telegram initData и управление сессионными куками.
"""

from pathlib import Path

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.miniapp import (
    MiniappAuthRequest,
    MiniappAuthResponse,
    MiniappCheckResponse,
    TesterItemResponse,
    TesterListResponse,
)
from config import (
    ALLOWED_USER_ID,
    DEPUTY_USER_ID,
    MINIAPP_HTML_FILE_PATH,
    SESSION_MAX_AGE_SECONDS,
)
from core.logger import get_logger
from services.testers_manager import (
    add_tester,
    get_all_testers,
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
    """Устанавливает подписанную защищенную сессионную куку тестера."""
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
    """Отдаёт интерфейс Telegram Mini App портала со встроенным Swagger UI."""
    if _HTML_PATH.exists():
        return HTMLResponse(content=_HTML_PATH.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>para-api Mini App</h1>", status_code=200)


@router.post("/auth", response_model=MiniappAuthResponse)
async def authenticate_miniapp(payload: MiniappAuthRequest, response: Response) -> MiniappAuthResponse:
    """Аутентифицирует пользователя по Telegram initData и выдает сессию."""
    info = validate_telegram_init_data(payload.init_data)
    if not info or "id" not in info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram signature")
    user_id = int(info["id"])
    if not await is_tester_allowed(user_id):
        log.warning(f"🚫 Пользователь {user_id} не в списке тестеров API")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")
    _set_tester_cookie(response, user_id)
    return MiniappAuthResponse(user_id=user_id, first_name=info.get("first_name"), username=info.get("username"))


@router.get("/status", response_model=MiniappCheckResponse)
async def check_tester_status(para_session: str = Cookie(default=None)) -> MiniappCheckResponse:
    """Возвращает статус авторизации текущего пользователя."""
    if not para_session:
        return MiniappCheckResponse(authenticated=False, is_tester=False)
    uid = verify_tester_session(para_session)
    if uid is None:
        return MiniappCheckResponse(authenticated=False, is_tester=False)
    allowed = await is_tester_allowed(uid)
    return MiniappCheckResponse(authenticated=True, user_id=uid, is_tester=allowed)


@router.get("/testers", response_model=TesterListResponse, dependencies=[Depends(verify_api_or_tester)])
async def list_api_testers() -> TesterListResponse:
    """Возвращает список всех зарегистрированных тестеров API."""
    uids = await get_all_testers()
    items = [TesterItemResponse(user_id=u, is_admin=(u in {ALLOWED_USER_ID, DEPUTY_USER_ID})) for u in uids]
    return TesterListResponse(count=len(items), testers=items)


@router.post("/testers/{user_id}", dependencies=[Depends(verify_admin_access)])
async def api_add_tester(user_id: int) -> dict:
    """Добавляет пользователя в белый список тестеров API (Admin only)."""
    success = await add_tester(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add tester")
    return {"status": "ok", "user_id": user_id}


@router.delete("/testers/{user_id}", dependencies=[Depends(verify_admin_access)])
async def api_remove_tester(user_id: int) -> dict:
    """Удаляет пользователя из белого списка тестеров API (Admin only)."""
    success = await remove_tester(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot remove admin or error")
    return {"status": "ok", "user_id": user_id}
