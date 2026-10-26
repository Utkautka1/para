"""
Роутер Telegram Mini App и аутентификации тестеров Swagger UI.

Обеспечивает защищённый доступ к документации и эндпоинтам API через
валидацию HMAC-SHA256 подписи Telegram initData и управление сессионными куками.
"""

import secrets
from pathlib import Path

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

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
    API_SECRET_KEY,
    DEPUTY_USER_ID,
    MINIAPP_HTML_FILE_PATH,
    SESSION_MAX_AGE_SECONDS,
)
from core.logger import get_logger
from services.classmates_auth import find_classmate_by_tg_id
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

    if _HTML_PATH.exists():
        return HTMLResponse(content=_HTML_PATH.read_text(encoding="utf-8"))

    return HTMLResponse(content="<h1>para-api Mini App</h1>", status_code=200)


@router.get("/dev-login")
async def dev_login(key: str = Query(..., description="API Secret Key")) -> Response:
    """Выполняет вход разработчика по API ключу и перенаправляет в MiniApp."""
    if not secrets.compare_digest(key.strip(), API_SECRET_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    redirect = RedirectResponse(url="/miniapp", status_code=status.HTTP_303_SEE_OTHER)
    _set_tester_cookie(redirect, ALLOWED_USER_ID)
    log.info(f"🔑 Успешный dev-login разработчика (user_id={ALLOWED_USER_ID})")
    return redirect


def _auth_developer_key(api_key: str, response: Response) -> MiniappAuthResponse:
    """Проверяет ключ разработчика и устанавливает сессионную куку тестера."""
    if not secrets.compare_digest(api_key.strip(), API_SECRET_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    _set_tester_cookie(response, ALLOWED_USER_ID)
    log.info(f"✅ Вход тестера с ПК по API-ключу (user_id={ALLOWED_USER_ID})")
    return MiniappAuthResponse(user_id=ALLOWED_USER_ID, first_name="Разработчик", username="dev")


async def _auth_telegram_init(init_data: str, response: Response) -> MiniappAuthResponse:
    """Валидирует подпись Telegram initData и проверяет права студента или тестера."""
    info = validate_telegram_init_data(init_data)
    if not info or "id" not in info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram signature")
    uid = int(info["id"])
    is_classmate = bool(uid == ALLOWED_USER_ID or find_classmate_by_tg_id(uid) is not None)
    is_tester = await is_tester_allowed(uid)
    if not is_classmate and not is_tester:
        log.warning(f"🚫 Пользователь {uid} не в группе 1-КПД-3 и не в списке тестеров")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not allowed")
    _set_tester_cookie(response, uid)
    return MiniappAuthResponse(user_id=uid, first_name=info.get("first_name"), username=info.get("username"))


@router.post("/auth", response_model=MiniappAuthResponse)
async def authenticate_miniapp(payload: MiniappAuthRequest, response: Response) -> MiniappAuthResponse:
    """Аутентифицирует пользователя по Telegram initData или ключу разработчика."""
    if payload.api_key:
        return _auth_developer_key(payload.api_key, response)
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


@router.get("/testers", response_model=TesterListResponse, dependencies=[Depends(verify_api_or_tester)])
async def list_api_testers() -> TesterListResponse:
    """
    Возвращает список всех зарегистрированных тестеров Swagger UI.

    Помечает главных администраторов бота флагом is_admin=True.
    Используется для управления доступом к закрытой документации.

    Возвращает TesterListResponse со списком тестеров и их количеством.
    """

    uids = await get_all_testers()
    items = [TesterItemResponse(user_id=u, is_admin=(u in {ALLOWED_USER_ID, DEPUTY_USER_ID})) for u in uids]

    return TesterListResponse(count=len(items), testers=items)


@router.post("/testers/{user_id}", dependencies=[Depends(verify_admin_access)])
async def api_add_tester(user_id: int) -> dict:
    """
    Добавляет пользователя в постоянный список тестеров API (Admin only).

    Сохраняет Telegram ID в Redis-множество тестеров.
    Выбрасывает HTTP 400 при невозможности добавления.

    Возвращает подтверждающий словарь со статусом 'ok' и ID тестера.
    """

    success = await add_tester(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add tester")

    return {"status": "ok", "user_id": user_id}


@router.delete("/testers/{user_id}", dependencies=[Depends(verify_admin_access)])
async def api_remove_tester(user_id: int) -> dict:
    """
    Удаляет пользователя из списка авторизованных тестеров API (Admin only).

    Запрещает удаление главных администраторов проекта из белого списка.
    Выбрасывает HTTP 400 при попытке удаления админа или сбое хранилища.

    Возвращает словарь со статусом 'ok' и ID удаленного тестера.
    """

    success = await remove_tester(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot remove admin or error")

    return {"status": "ok", "user_id": user_id}
