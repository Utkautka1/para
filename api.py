"""
Точка входа сервиса para-api (FastAPI + gRPC Server + Swagger UI).

Единая точка доступа к данным расписания, экзаменов, преподавателей и посещаемости.
Поддерживает gRPC (порт GRPC_PORT) и HTTP REST со Swagger UI (порт 8000).
"""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator
import uvicorn
from fastapi import FastAPI

from api import create_app
from api.grpc.server import create_grpc_server, start_grpc_server, stop_grpc_server
from config import GRPC_HOST, GRPC_PORT
from core.logger import get_logger

log = get_logger("api_main")


class _InvalidHttpFilter(logging.Filter):
    """Подавляет спам от сетевых сканеров и SSL-хэндшейков на чистом HTTP-порту."""
    def filter(self, record: logging.LogRecord) -> bool:
        return "Invalid HTTP request received" not in record.getMessage()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Управляет жизненным циклом gRPC-сервера параллельно с FastAPI."""
    grpc_server = create_grpc_server()
    await start_grpc_server(grpc_server, GRPC_HOST, GRPC_PORT)
    log.info(f"⚡ gRPC сервер активен на {GRPC_HOST}:{GRPC_PORT}")
    try:
        yield
    finally:
        await stop_grpc_server(grpc_server)


app = create_app()
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    logging.getLogger("uvicorn.error").addFilter(_InvalidHttpFilter())
    log.info("=" * 60)
    log.info(f"ЗАПУСК Dual-Protocol API: HTTP :8000 | gRPC :{GRPC_PORT}")
    log.info("  Swagger UI: /docs | Telegram Mini App: /miniapp")
    log.info("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")  # nosec B104
