"""
Единый реестр метрик Prometheus для сервисов платформы para.

Инициализирует счетчики, гистограммы задержек и датчики очередей Redis.
Предоставляет чистые вспомогательные функции (<= 25 строк) для сбора телеметрии.
"""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# 1. Метрики HTTP REST API
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Общее количество входящих HTTP-запросов",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Гистограмма времени ответа HTTP API в секундах",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# 2. Метрики нейросетевых пайплайнов (DeepSeek & Whisper)
AI_INFERENCE_DURATION_SECONDS = Histogram(
    "ai_inference_duration_seconds",
    "Гистограмма задержки инференса нейросетей в секундах",
    ["subsystem", "model"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0),
)

# 3. Метрики состояния очередей и фоновых задач
REDIS_QUEUE_LENGTH = Gauge(
    "redis_queue_length",
    "Текущее количество задач в очереди Redis",
    ["queue_name"],
)


# Методы, которые попадают в лейбл как есть; остальное (мусор от сканеров) — в "OTHER"
_KNOWN_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})


def normalize_http_method(method: str) -> str:
    """
    Сводит HTTP-метод к ограниченному набору значений лейбла.

    Возвращает метод в верхнем регистре или 'OTHER'.
    """
    upper = method.upper()
    return upper if upper in _KNOWN_HTTP_METHODS else "OTHER"


def record_http_request(method: str, endpoint: str, status: int, duration: float) -> None:
    """
    Фиксирует завершенный HTTP-запрос в счетчиках и гистограмме Prometheus.

    Нормализует код ответа и инкрементирует телеметрические датчики.

    Ничего не возвращает.
    """
    HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint).observe(duration)


def record_ai_inference(subsystem: str, model: str, duration: float) -> None:
    """
    Регистрирует длительность инференса нейросетевой модели.

    Позволяет отслеживать задержки ответов DeepSeek API и инференса Whisper.

    Ничего не возвращает.
    """
    AI_INFERENCE_DURATION_SECONDS.labels(subsystem=subsystem, model=model).observe(duration)


def set_redis_queue_length(queue_name: str, length: int) -> None:
    """
    Обновляет текущий размер очереди в Redis для мониторинга лага обработки.

    Используется воркерами для публикации глубины очереди задач.

    Ничего не возвращает.
    """
    REDIS_QUEUE_LENGTH.labels(queue_name=queue_name).set(length)


def generate_metrics_payload() -> tuple[bytes, str]:
    """
    Экспортирует все накопленные метрики в стандартном текстовом формате Prometheus.

    Используется роутером GET /metrics для отдачи агентам сбора метрик (Prometheus/VictoriaMetrics).

    Возвращает кортеж (бинарное тело метрик, Content-Type заголовок).
    """
    return generate_latest(), CONTENT_TYPE_LATEST
