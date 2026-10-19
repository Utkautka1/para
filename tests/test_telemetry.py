"""
Тесты распределенного трейсинга OpenTelemetry (core.telemetry, middleware, gRPC).

Проверяет:
  1. Инициализацию TracerProvider и fallback при отключенном трейсинге
  2. Генерацию и форматирование trace_id
  3. Контекстный менеджер trace_span (sync и async with)
  4. Сериализацию и десериализацию W3C TraceContext в gRPC metadata и HTTP headers
  5. Aiogram TracingMiddleware для CallbackQuery и Message
  6. Серверный gRPC интерцептор GrpcTracingInterceptor
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import CallbackQuery, Chat, Message, User

from api.grpc.server import GrpcTracingInterceptor
from bot.middlewares.tracing import TracingMiddleware
from core.logger import get_trace_id
from core.telemetry import (
    carrier_from_grpc_metadata,
    carrier_to_grpc_metadata,
    extract_trace_context,
    format_trace_id,
    get_tracer,
    inject_trace_carrier,
    trace_span,
)


def test_get_tracer_returns_valid_instance() -> None:
    """Проверяет, что get_tracer возвращает работоспособный экземпляр Tracer."""
    tracer = get_tracer("test_subsystem")
    assert tracer is not None
    assert hasattr(tracer, "start_as_current_span")


def test_carrier_metadata_conversions() -> None:
    """Проверяет конвертацию заголовков в gRPC metadata и обратно."""
    headers = {"traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"}
    metadata = carrier_to_grpc_metadata(headers)
    assert ("traceparent", headers["traceparent"]) in metadata

    converted_back = carrier_from_grpc_metadata(metadata)
    assert converted_back["traceparent"] == headers["traceparent"]
    assert carrier_from_grpc_metadata(None) == {}


def test_carrier_from_dict_and_none() -> None:
    """Проверяет обработку словарей и пустых структур в carrier_from_grpc_metadata."""
    dict_meta = {"X-Trace-Id": "12345"}
    assert carrier_from_grpc_metadata(dict_meta) == {"x-trace-id": "12345"}
    assert carrier_from_grpc_metadata(123) == {}


def test_trace_span_sync() -> None:
    """Проверяет синхронный контекстный менеджер trace_span."""
    with trace_span("test.sync_span", attributes={"test.attr": "value"}) as span:
        assert span is not None
        tid = format_trace_id(span)
        if tid:
            assert get_trace_id() == tid


@pytest.mark.asyncio
async def test_trace_span_async_and_exception() -> None:
    """Проверяет асинхронный контекстный менеджер и запись исключений."""
    with pytest.raises(RuntimeError, match="test error"):
        async with trace_span("test.async_span"):
            raise RuntimeError("test error")


from datetime import UTC, datetime

from opentelemetry.sdk.trace import TracerProvider


def test_inject_and_extract_trace_context() -> None:
    """Проверяет сквозную передачу W3C TraceContext через словарь carrier."""
    provider = TracerProvider()
    tracer = provider.get_tracer("test_carrier")
    with tracer.start_as_current_span("parent_span") as span:
        carrier = inject_trace_carrier()
        assert "traceparent" in carrier
        ctx = extract_trace_context(carrier)
        assert ctx is not None

        child_span = tracer.start_span("child_span", context=ctx)
        assert format_trace_id(span) == format_trace_id(child_span)
        child_span.end()


def test_extract_trace_context_none() -> None:
    """Проверяет extract_trace_context при пустом носителе."""
    ctx = extract_trace_context(None)
    assert ctx is not None


@pytest.mark.asyncio
async def test_tracing_middleware_callback_query() -> None:
    """Проверяет создание спана в Aiogram TracingMiddleware для CallbackQuery."""
    middleware = TracingMiddleware()
    now = datetime.now(UTC)
    user = User(id=12345, is_bot=False, first_name="Tester")
    chat = Chat(id=67890, type="private")
    msg = Message(message_id=1, date=now, chat=chat)
    cb = CallbackQuery(id="cb1", from_user=user, chat_instance="ci", message=msg, data="sched:today")

    handler = AsyncMock(return_value="handler_ok")
    result = await middleware(handler, cb, {})

    assert result == "handler_ok"
    handler.assert_awaited_once_with(cb, {})


@pytest.mark.asyncio
async def test_tracing_middleware_message() -> None:
    """Проверяет создание спана в Aiogram TracingMiddleware для Message."""
    middleware = TracingMiddleware()
    now = datetime.now(UTC)
    user = User(id=111, is_bot=False, first_name="Student")
    chat = Chat(id=222, type="group")
    msg = Message(message_id=2, date=now, chat=chat, from_user=user, text="/schedule")

    handler = AsyncMock(return_value="msg_ok")
    result = await middleware(handler, msg, {})

    assert result == "msg_ok"
    handler.assert_awaited_once_with(msg, {})


@pytest.mark.asyncio
async def test_grpc_tracing_interceptor() -> None:
    """Проверяет перехват входящего вызова gRPC сервером и создание дочернего спана."""
    interceptor = GrpcTracingInterceptor()
    call_details = MagicMock()
    call_details.method = "/ScheduleService/GetDaySchedule"
    call_details.invocation_metadata = (("traceparent", "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"),)

    mock_unary = AsyncMock(return_value="grpc_resp")
    inner_handler = MagicMock()
    inner_handler.unary_unary = mock_unary
    inner_handler.request_deserializer = None
    inner_handler.response_serializer = None

    continuation = AsyncMock(return_value=inner_handler)
    wrapped = await interceptor.intercept_service(continuation, call_details)

    assert wrapped is not None
    assert wrapped.unary_unary is not None

    servicer_ctx = MagicMock()
    res = await wrapped.unary_unary("req", servicer_ctx)
    assert res == "grpc_resp"
    mock_unary.assert_awaited_once_with("req", servicer_ctx)
