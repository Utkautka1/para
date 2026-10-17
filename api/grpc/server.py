"""
Управление асинхронным gRPC сервером para-api.

Запускает gRPC сервер на базе grpc.aio с пулом потоков и регистрацией
сервисеров расписания, экзаменов и преподавателей.
"""


import secrets
from collections.abc import Awaitable, Callable
from typing import Any

import grpc

from api.grpc.servicers import ExamsServicer, ScheduleServicer, TeachersServicer
from api.proto import exams_pb2_grpc, schedule_pb2_grpc, teachers_pb2_grpc
from config import (
    API_SECRET_KEY,
    GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA,
    GRPC_HTTP2_MIN_PING_INTERVAL_MS,
    GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS,
    GRPC_KEEPALIVE_TIME_MS,
    GRPC_KEEPALIVE_TIMEOUT_MS,
    GRPC_MAX_MESSAGE_LENGTH,
)
from core.logger import get_logger

log = get_logger("grpc_server")


class ApiKeyAuthInterceptor(grpc.aio.ServerInterceptor):
    """Интерцептор проверки X-API-Key заголовка для защиты gRPC эндпоинтов."""

    @staticmethod
    async def _abort_unauthenticated(_req: Any, context: grpc.aio.ServicerContext) -> Any:
        await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing X-API-Key header")

    async def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        metadata = dict(handler_call_details.invocation_metadata or ())
        api_key = metadata.get("x-api-key")
        if not api_key or not secrets.compare_digest(api_key, API_SECRET_KEY):
            return grpc.unary_unary_rpc_method_handler(self._abort_unauthenticated)
        return await continuation(handler_call_details)


def _register_servicers(server: grpc.aio.Server) -> None:
    """Регистрирует все gRPC сервисеры на сервере."""
    schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)
    exams_pb2_grpc.add_ExamsServiceServicer_to_server(ExamsServicer(), server)
    teachers_pb2_grpc.add_TeachersServiceServicer_to_server(TeachersServicer(), server)


def create_grpc_server() -> grpc.aio.Server:
    """Создает и настраивает экземпляр gRPC сервера с HTTP/2 keepalive опциями."""
    options = [
        ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH),
        ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
        ("grpc.keepalive_time_ms", GRPC_KEEPALIVE_TIME_MS),
        ("grpc.keepalive_timeout_ms", GRPC_KEEPALIVE_TIMEOUT_MS),
        ("grpc.keepalive_permit_without_calls", GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS),
        ("grpc.http2.max_pings_without_data", GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA),
        ("grpc.http2.min_ping_interval_without_data_ms", GRPC_HTTP2_MIN_PING_INTERVAL_MS),
    ]
    server = grpc.aio.server(options=options, interceptors=[ApiKeyAuthInterceptor()])
    _register_servicers(server)
    return server


async def start_grpc_server(server: grpc.aio.Server, host: str, port: int) -> None:
    """Привязывает сокет и запускает обработку gRPC соединений."""
    listen_addr = f"{host}:{port}"
    server.add_insecure_port(listen_addr)
    log.info(f"🚀 Запуск gRPC сервера на {listen_addr}")
    await server.start()


async def stop_grpc_server(server: grpc.aio.Server | None, grace: float = 5.0) -> None:
    """Останавливает gRPC сервер с ожиданием завершения активных вызовов."""
    if server is not None:
        log.info(f"🛑 Остановка gRPC сервера (grace={grace}s)...")
        await server.stop(grace=grace)
        log.info("✅ gRPC сервер успешно остановлен")
