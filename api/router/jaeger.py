"""
Роутер реверс-проксирования интерфейса Jaeger UI в защищенный портал Mini App.

Зачем существует этот модуль:
Предоставляет авторизованным тестировщикам и администраторам доступ к веб-интерфейсу
распределенных трейсов OpenTelemetry/Jaeger через единый домен и протокол HTTPS,
закрывая доступ от посторонних через зависимость verify_api_or_tester.
"""

import posixpath
import urllib.parse
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from api.deps import verify_api_or_tester
from config import JAEGER_UI_URL
from core.logger import get_logger

log = get_logger("jaeger_proxy")

router = APIRouter(
    prefix="/jaeger",
    tags=["Jaeger Tracing UI"],
    dependencies=[Depends(verify_api_or_tester)],
)

_HOP_BY_HOP_HEADERS = {
    "host",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length",
    "content-encoding",
}


def _filter_headers(headers: Any) -> dict[str, str]:
    """
    Фильтрует транзитные сетевые заголовки HTTP/1.1 (hop-by-hop).

    Предотвращает конфликты кодировок и повторный расчет длины контента.

    Возвращает очищенный словарь заголовков для пересылки.
    """
    return {k: v for k, v in headers.items() if k.lower() not in _HOP_BY_HOP_HEADERS}


def _sanitize_proxy_path(raw_path: str) -> str:
    """
    Очищает и нормализует путь проксирования, блокируя попытки Path Traversal.

    Декодирует URL-символы и отсекает переходы вверх по каталогу ('..').
    Предотвращает побег за пределы префикса /jaeger на внутреннем хосте.

    Возвращает безопасный строковый путь или выбрасывает HTTPException 400.
    """
    decoded = urllib.parse.unquote(raw_path)
    normalized = posixpath.normpath("/" + decoded.lstrip("/")).lstrip("/")
    if ".." in normalized.split("/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid traversal path")
    return "" if normalized == "." else normalized


def _build_target_url(path: str, query: str) -> str:
    """
    Формирует проверенный целевой адрес Jaeger с учетом безопасного пути.

    Изолирует запросы внутри префикса /jaeger/ и сохраняет исходные GET-параметры.

    Возвращает полный строковый URL назначения.
    """
    base = JAEGER_UI_URL.rstrip("/")
    clean_path = _sanitize_proxy_path(path)
    url = f"{base}/jaeger/{clean_path}" if clean_path else f"{base}/jaeger/"
    return f"{url}?{query}" if query else url


async def _forward_request(method: str, url: str, headers: dict[str, str], body: bytes | None) -> Response:
    """
    Выполняет асинхронный HTTP-запрос к бэкенду Jaeger UI и проксирует ответ.

    Использует httpx.AsyncClient с таймаутом 15 секунд и защитой от падения соединения.

    Возвращает HTTP Response с полученным телом, статусом и заголовками.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.request(method=method, url=url, headers=headers, content=body)
        clean_resp_headers = _filter_headers(resp.headers)
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=clean_resp_headers,
            media_type=resp.headers.get("content-type"),
        )
    except httpx.RequestError as exc:
        log.warning("⚠️ Ошибка соединения с Jaeger UI (%s): %s", url, exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "Jaeger UI service is temporarily unavailable", "detail": str(exc)},
        )


@router.get("", include_in_schema=False)
async def redirect_jaeger_root() -> RedirectResponse:
    """
    Перенаправляет запрос с /jaeger на /jaeger/ со слэшем.

    Необходимо браузеру для корректного разрешения относительных путей статики.

    Возвращает постоянный редирект HTTP 307.
    """
    return RedirectResponse(url="/jaeger/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.api_route("/{path:path}", methods=["GET", "POST", "OPTIONS", "HEAD"], include_in_schema=False)
async def proxy_jaeger(request: Request, path: str = "") -> Response:
    """
    Проксирует все статические ресурсы, HTML и REST API Jaeger UI.

    Передает тело и заголовки запроса в целевой контейнер jaeger:16686.

    Возвращает ответ от Jaeger с валидацией авторизации тестера.
    """
    target_url = _build_target_url(path, request.url.query)
    req_headers = _filter_headers(request.headers)
    body = await request.body() if request.method in {"POST", "PUT", "PATCH"} else None
    return await _forward_request(request.method, target_url, req_headers, body)
