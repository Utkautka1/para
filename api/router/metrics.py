"""
Роутер телеметрии Prometheus — GET /metrics.

Отдает накопленные метрики производительности API, задержек нейросетей
и состояния очередей для скрейпинга агентом мониторинга Prometheus.
"""

from fastapi import APIRouter, Response

from core.metrics import generate_metrics_payload

router = APIRouter(tags=["Metrics"])


@router.get("/metrics", include_in_schema=False)
async def get_prometheus_metrics() -> Response:
    """
    Экспортирует системные метрики в формате текстового протокола Prometheus.

    Используется системами мониторинга (Prometheus, Grafana, VictoriaMetrics)
    без требования предварительной авторизации.

    Возвращает HTTP Response с бинарным телом метрик и соответствующим Content-Type.
    """
    payload, media_type = generate_metrics_payload()
    return Response(content=payload, media_type=media_type)
