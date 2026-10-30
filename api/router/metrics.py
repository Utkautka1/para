"""
Роутер телеметрии Prometheus — GET /metrics.

Отдает накопленные метрики производительности API, задержек нейросетей
и состояния очередей для скрейпинга агентом мониторинга Prometheus.
"""

from fastapi import APIRouter, Depends, Response

from api.deps import verify_admin_access
from core.metrics import generate_metrics_payload

router = APIRouter(tags=["Metrics"])


# Только админ: в метриках видны маршруты и нагрузка, а внешнего скрейпера у проекта нет
@router.get("/metrics", include_in_schema=False, dependencies=[Depends(verify_admin_access)])
async def get_prometheus_metrics() -> Response:
    """
    Экспортирует системные метрики в формате текстового протокола Prometheus.

    Доступ — мастер-ключ (X-API-Key) или админ-сессия; скрейпер Prometheus
    должен передавать ключ заголовком.

    Возвращает HTTP Response с бинарным телом метрик и соответствующим Content-Type.
    """
    payload, media_type = generate_metrics_payload()
    return Response(content=payload, media_type=media_type)
