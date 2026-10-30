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
from core.telemetry import (
    carrier_from_grpc_metadata,
    extract_trace_context,
    trace_span,
)

log = get_logger("grpc_server")


def _wrap_unary_handler(fn: Any, method: str, parent_ctx: Any) -> Any:
    """Оборачивает унарный RPC обработчик в спан OpenTelemetry."""

    async def _traced_unary(req: Any, context: grpc.aio.ServicerContext) -> Any:
        attrs = {"rpc.system": "grpc", "rpc.method": method}
        async with trace_span(f"grpc.server{method}", attributes=attrs, parent_context=parent_ctx):
            return await fn(req, context)

    return _traced_unary


class GrpcTracingInterceptor(grpc.aio.ServerInterceptor):
    """Интерцептор распределенного трейсинга OpenTelemetry для входящих gRPC вызовов."""

    async def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """Извлекает W3C TraceContext из метаданных и связывает дочерние спаны сервисеров."""
        handler = await continuation(handler_call_details)
        if handler is None:
            return None

        carrier = carrier_from_grpc_metadata(handler_call_details.invocation_metadata)
        parent_ctx = extract_trace_context(carrier)
        method = handler_call_details.method

        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                _wrap_unary_handler(handler.unary_unary, method, parent_ctx),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler


class ApiKeyAuthInterceptor(grpc.aio.ServerInterceptor):
    """Интерцептор проверки X-API-Key заголовка для защиты gRPC эндпоинтов."""

    @staticmethod
    async def _abort_unauthenticated(_req: Any, context: grpc.aio.ServicerContext) -> Any:
        """
        Прерывает вызов с кодом UNAUTHENTICATED при невалидном ключе.

        Возбуждает исключение gRPC context abort.
        """
        await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing X-API-Key header")

    async def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """
        Перехватывает RPC-вызов и проверяет соответствие ключа авторизации в метаданных.

        Использует secrets.compare_digest для предотвращения атак по времени.

        Возвращает обработчик метода или перенаправляет на abort.
        """
        metadata = dict(handler_call_details.invocation_metadata or ())
        api_key = metadata.get("x-api-key")

        if not api_key or not secrets.compare_digest(api_key.encode("utf-8"), API_SECRET_KEY.encode("utf-8")):
            return grpc.unary_unary_rpc_method_handler(self._abort_unauthenticated)

        return await continuation(handler_call_details)


def _register_servicers(server: grpc.aio.Server) -> None:
    """
    Регистрирует все gRPC сервисеры на экземпляре сервера.

    Подключает ScheduleService, ExamsService и TeachersService.

    Ничего не возвращает.
    """
    schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)
    exams_pb2_grpc.add_ExamsServiceServicer_to_server(ExamsServicer(), server)
    teachers_pb2_grpc.add_TeachersServiceServicer_to_server(TeachersServicer(), server)


def create_grpc_server() -> grpc.aio.Server:
    """
    Создает и настраивает экземпляр gRPC сервера с HTTP/2 keepalive опциями.

    Конфигурирует сетевые буферы сообщений и интерцепторы аутентификации.

    Возвращает инициализированный объект grpc.aio.Server.
    """
    options = [
        ("grpc.max_receive_message_length", GRPC_MAX_MESSAGE_LENGTH),
        ("grpc.max_send_message_length", GRPC_MAX_MESSAGE_LENGTH),
        ("grpc.keepalive_time_ms", GRPC_KEEPALIVE_TIME_MS),
        ("grpc.keepalive_timeout_ms", GRPC_KEEPALIVE_TIMEOUT_MS),
        ("grpc.keepalive_permit_without_calls", GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS),
        ("grpc.http2.max_pings_without_data", GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA),
        ("grpc.http2.min_ping_interval_without_data_ms", GRPC_HTTP2_MIN_PING_INTERVAL_MS),
    ]

    server = grpc.aio.server(
        options=options,
        interceptors=[GrpcTracingInterceptor(), ApiKeyAuthInterceptor()],
    )
    _register_servicers(server)

    return server


async def start_grpc_server(server: grpc.aio.Server, host: str, port: int) -> None:
    """
    Привязывает сокет и запускает обработку входящих gRPC соединений.

    Открывает TCP-порт и переводит сервер в активное состояние прослушивания.

    Ничего не возвращает.
    """
    listen_addr = f"{host}:{port}"
    server.add_insecure_port(listen_addr)

    log.info("🚀 Запуск gRPC сервера на %s", listen_addr)
    await server.start()


async def stop_grpc_server(server: grpc.aio.Server | None, grace: float = 5.0) -> None:
    """
    Останавливает gRPC сервер с ожиданием завершения активных вызовов.

    Предоставляет период grace секунд для корректного закрытия соединений клиентами.

    Ничего не возвращает.
    """
    if server is not None:
        log.info("🛑 Остановка gRPC сервера (grace=%ss)...", grace)
        await server.stop(grace=grace)
        log.info("✅ gRPC сервер успешно остановлен")
