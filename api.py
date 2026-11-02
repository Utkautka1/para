"""
Точка входа сервиса para-api (FastAPI + gRPC Server + Swagger UI).

Единая точка доступа к данным расписания, экзаменов, преподавателей и посещаемости.
Поддерживает gRPC (порт GRPC_PORT) и HTTP REST со Swagger UI (порт 8000).
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import create_app
from api.grpc.server import create_grpc_server, start_grpc_server, stop_grpc_server
from api.router.jaeger import close_jaeger_client
from config import API_HOST, API_PORT, GRPC_HOST, GRPC_PORT
from core.api_client import close_api_client
from core.background import drain_background
from core.logger import get_logger
from core.redis import close_redis, init_redis

log = get_logger("api_main")


class _InvalidHttpFilter(logging.Filter):
    """Фильтр сообщений логов для подавления шума сетевых сканеров."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Фильтрует мусорные записи логов о некорректных HTTP-запросах.

        Подавляет спам от автоматических сетевых сканеров и попыток SSL-хэндшейка.
        Предотвращает засорение производственных логов бессмысленными варнингами.

        Возвращает False, если сообщение содержит мусорный паттерн, иначе True.
        """

        return "Invalid HTTP request received" not in record.getMessage()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управляет жизненным циклом gRPC-сервера и соединений FastAPI.

    Инициализирует gRPC-сервер и Redis перед приемом трафика.
    При завершении приложения корректно закрывает gRPC, Redis и API-клиенты.

    Ничего не возвращает (асинхронный генератор контекста).
    """

    grpc_server = create_grpc_server()
    await start_grpc_server(grpc_server, GRPC_HOST, GRPC_PORT)
    log.info("⚡ gRPC сервер активен на %s:%s", GRPC_HOST, GRPC_PORT)
    await init_redis()
    from core.database import init_db

    await init_db()

    try:
        yield
    finally:
        await stop_grpc_server(grpc_server)
        await drain_background()
        await close_redis()
        await close_api_client()
        await close_jaeger_client()


app = create_app()
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    logging.getLogger("uvicorn.error").addFilter(_InvalidHttpFilter())
    log.info("=" * 60)
    log.info("ЗАПУСК Dual-Protocol API: HTTP :%s | gRPC :%s", API_PORT, GRPC_PORT)
    log.info("  Swagger UI: /docs | Telegram Mini App: /miniapp")
    log.info("=" * 60)
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        loop="uvloop",
        http="httptools",
        log_level="warning",
    )
