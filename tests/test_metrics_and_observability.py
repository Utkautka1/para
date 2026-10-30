"""
Тесты подсистемы наблюдаемости (Observability) и метрик Prometheus.

Проверяет эндпоинт GET /metrics, middleware генерации X-Request-ID,
контекстное логирование trace_id и запись метрик нейросетей и очередей.
"""

import pytest
from fastapi.testclient import TestClient

from api import create_app
from core.logger import get_logger, get_trace_id, set_trace_id
from core.metrics import (
    generate_metrics_payload,
    record_ai_inference,
    record_http_request,
    set_redis_queue_length,
)


@pytest.fixture
def client():
    """Тестовый клиент для приложения FastAPI."""
    app = create_app()
    return TestClient(app)


def test_get_metrics_endpoint_returns_prometheus_format(client):
    """Проверяет отдачу метрик Prometheus через эндпоинт GET /metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    content = response.text
    assert "http_requests_total" in content
    assert "http_request_duration_seconds" in content


def test_observability_middleware_generates_x_request_id(client):
    """Проверяет генерацию X-Request-ID при отсутствии заголовка."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) >= 8


def test_observability_middleware_preserves_incoming_x_request_id(client):
    """Проверяет сохранение входящего заголовка X-Request-ID."""
    custom_trace_id = "test-custom-trace-uuid-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_trace_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_trace_id


def test_core_metrics_recording_helpers():
    """Проверяет запись кастомных метрик задержек AI и длины очередей."""
    record_http_request("GET", "/test_endpoint", 200, 0.042)
    record_ai_inference("deepseek", "deepseek-v4", 1.85)
    set_redis_queue_length("hw:tasks:queue", 5)

    payload, media_type = generate_metrics_payload()
    text = payload.decode("utf-8")
    assert "ai_inference_duration_seconds" in text
    assert "redis_queue_length" in text
    assert media_type is not None


def test_logger_trace_id_context_lifecycle():
    """Проверяет установку и очистку trace_id в контексте логирования."""
    set_trace_id("trace_abc_789")
    assert get_trace_id() == "trace_abc_789"

    log = get_logger("test_observability_logger")
    log.info("Тестовое сообщение с trace_id")

    set_trace_id("")
    assert get_trace_id() == ""


@pytest.mark.parametrize(
    ("argv0", "env", "expected"),
    [
        ("/app/api.py", None, "logs/api.log"),
        ("worker.py", None, "logs/worker.log"),
        ("/usr/bin/pytest", None, "logs/app.log"),
        ("/usr/bin/pytest", "solver", "logs/solver.log"),
    ],
)
def test_log_file_resolved_per_service(monkeypatch, argv0, env, expected):
    """Каждый сервис пишет в свой файл: по LOG_SERVICE или по имени entrypoint."""
    from core import logger as core_logger

    monkeypatch.setattr("sys.argv", [argv0])
    if env:
        monkeypatch.setenv("LOG_SERVICE", env)
    else:
        monkeypatch.delenv("LOG_SERVICE", raising=False)
    assert core_logger._resolve_log_file() == expected


def test_loggers_share_single_file_handler():
    """Все логгеры процесса используют один файловый хэндлер — иначе ротация ломается."""
    import logging

    first = get_logger("test_shared_handlers_a")
    second = get_logger("test_shared_handlers_b")
    file_handlers = {id(h) for lg in (first, second) for h in lg.handlers if isinstance(h, logging.FileHandler)}
    assert len(file_handlers) == 1
