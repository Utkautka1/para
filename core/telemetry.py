"""
Модуль распределенного трейсинга OpenTelemetry и экспорта в Jaeger (OTLP).

Обеспечивает сквозную трассировку пользовательских запросов:
  1. Telegram Bot (Aiogram CallbackQuery / Message)
  2. Внутренний gRPC клиент и сервер (W3C TraceContext в metadata)
  3. HTTP REST API эндпоинты (FastAPI Instrumentation)
  4. L2 Redis кэш (операции get / set)
  5. SQLite база данных

Поддерживает fail-safe режим: при недоступности Jaeger или OTEL_ENABLED=False
используется no-op провайдер без сетевых задержек и исключений.
"""

from collections.abc import Iterable
from typing import Any

from opentelemetry import context, propagate, trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

from config import OTEL_ENABLED, OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME
from core.logger import get_logger, set_trace_id

log = get_logger("telemetry")

_IS_INITIALIZED: bool = False


def setup_telemetry(service_name: str | None = None) -> None:
    """
    Инициализирует глобальный TracerProvider с экспортером OTLP gRPC.

    Если OTEL_ENABLED=False, оставляет no-op провайдер по умолчанию,
    гарантируя нулевые сетевые издержки и отсутствие блокировок.
    """
    global _IS_INITIALIZED
    if _IS_INITIALIZED or not OTEL_ENABLED:
        log.debug("OpenTelemetry пропущен: init=%s, enabled=%s", _IS_INITIALIZED, OTEL_ENABLED)
        return

    name = service_name or OTEL_SERVICE_NAME
    resource = Resource.create({"service.name": name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _IS_INITIALIZED = True
    log.info("OpenTelemetry инициализирован: service=%s, endpoint=%s", name, OTEL_EXPORTER_OTLP_ENDPOINT)


def get_tracer(name: str = "para") -> trace.Tracer:
    """
    Возвращает именованный экземпляр Tracer для создания spans.

    Безопасен для многократного вызова из любых корутин и потоков.
    """
    return trace.get_tracer(name)


def format_trace_id(span: trace.Span | None = None) -> str:
    """
    Форматирует 32-значный hex идентификатор трейса для передачи в логи.

    Возвращает строку trace_id или пустую строку, если контекст невалиден.
    """
    active_span = span or trace.get_current_span()
    ctx = active_span.get_span_context() if active_span else None
    if ctx and ctx.is_valid:
        return format(ctx.trace_id, "032x")
    return ""


def inject_trace_carrier(carrier: dict[str, str] | None = None) -> dict[str, str]:
    """
    Инжектирует активный W3C TraceContext в переданный или новый словарь.

    Используется для сквозной передачи заголовков traceparent через HTTP/gRPC.
    """
    target = {} if carrier is None else carrier
    propagate.inject(target)
    return target


def extract_trace_context(carrier: dict[str, str] | None) -> context.Context:
    """
    Извлекает контекст трейсинга из словаря заголовков W3C TraceContext.

    Возвращает объект context.Context для создания дочерних спанов.
    """
    if not carrier:
        return context.get_current()
    return propagate.extract(carrier)


def carrier_from_grpc_metadata(metadata: Any) -> dict[str, str]:
    """
    Преобразует метаданные gRPC вызова в словарь строковых заголовков.

    Обрабатывает кортежи кортежей и словари, приводя ключи к нижнему регистру.
    """
    if not metadata:
        return {}
    if isinstance(metadata, dict):
        return {str(k).lower(): str(v) for k, v in metadata.items()}
    if isinstance(metadata, Iterable):
        return {str(k).lower(): str(v) for k, v in metadata}
    return {}


def carrier_to_grpc_metadata(carrier: dict[str, str]) -> tuple[tuple[str, str], ...]:
    """
    Преобразует словарь трейсинга в формат метаданных gRPC (tuple of tuples).

    Подходит для непосредственной передачи в grpc.aio stubs.
    """
    return tuple((str(k), str(v)) for k, v in carrier.items())


class SpanContextManager:
    """Универсальный менеджер контекста спана (поддерживает sync и async with)."""

    def __init__(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
        parent_context: context.Context | None = None,
        tracer_name: str = "para",
    ) -> None:
        self.name = name
        self.attributes = attributes or {}
        self.parent_context = parent_context
        self.tracer = get_tracer(tracer_name)
        self._cm: Any = None
        self.span: trace.Span | None = None

    def __enter__(self) -> trace.Span:
        self._cm = self.tracer.start_as_current_span(
            self.name,
            context=self.parent_context,
            attributes=self.attributes,
        )
        self.span = self._cm.__enter__()
        tid = format_trace_id(self.span)
        if tid:
            set_trace_id(tid)
        return self.span

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool | None:
        if self.span and exc_val is not None:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        if self._cm:
            return self._cm.__exit__(exc_type, exc_val, exc_tb)
        return None

    async def __aenter__(self) -> trace.Span:
        return self.__enter__()

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool | None:
        return self.__exit__(exc_type, exc_val, exc_tb)


def trace_span(
    name: str,
    attributes: dict[str, Any] | None = None,
    parent_context: context.Context | None = None,
    tracer_name: str = "para",
) -> SpanContextManager:
    """
    Создает контекстный менеджер трейс-спана с автоматической фиксацией ошибок.

    Синтаксис: `with trace_span(...) as span:` или `async with trace_span(...):`.
    """
    return SpanContextManager(
        name=name,
        attributes=attributes,
        parent_context=parent_context,
        tracer_name=tracer_name,
    )
