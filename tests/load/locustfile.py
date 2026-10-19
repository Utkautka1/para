"""
Сценарии нагрузочного тестирования HTTP и gRPC API платформы Para на базе Locust.

Симулирует пиковую утреннюю нагрузку (8:00 утра) перед началом учебных пар:
  - Одновременные HTTP REST запросы (расписание дня, недели, health, metrics)
  - Высокоскоростные бинарные gRPC вызовы (ScheduleService GetDaySchedule / GetWeekSchedule)
  - Снятие точных кривых латентности (p50, p95, p99, p99.9) при целевом потоке 500+ RPS.
"""

import os
import time

import grpc
from locust import HttpUser, User, between, events, task

from api.proto import schedule_pb2, schedule_pb2_grpc
from config import (
    API_SECRET_KEY,
    GRPC_AUTH_HEADER_NAME,
    GRPC_SERVER_ADDRESS,
)

AUTH_HEADERS = {"X-API-Key": API_SECRET_KEY}
GRPC_METADATA = ((GRPC_AUTH_HEADER_NAME, API_SECRET_KEY),)


def _fire_grpc_event(name: str, start: float, exc: Exception | None, resp_len: int = 0) -> None:
    """Фиксирует метрику выполненного gRPC вызова во внутреннем сборщике статистики Locust."""
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    events.request.fire(
        request_type="gRPC",
        name=name,
        response_time=elapsed_ms,
        response_length=resp_len,
        exception=exc,
    )


class HttpScheduleUser(HttpUser):
    """Пользователь симуляции HTTP REST API запросов мобильного и веб-клиентов."""

    wait_time = between(0.001, 0.004)

    @task(5)
    def get_day_schedule(self) -> None:
        """Запрашивает расписание на текущий день через HTTP REST эндпоинт."""
        self.client.get("/schedule/day", headers=AUTH_HEADERS, name="HTTP /schedule/day")

    @task(2)
    def get_week_schedule(self) -> None:
        """Запрашивает расписание на неделю через HTTP REST эндпоинт."""
        self.client.get("/schedule/week", headers=AUTH_HEADERS, name="HTTP /schedule/week")

    @task(1)
    def get_health(self) -> None:
        """Проверяет состояние здоровья сервиса по легковесному эндпоинту."""
        self.client.get("/health", name="HTTP /health")

    @task(1)
    def get_metrics(self) -> None:
        """Запрашивает метрики Prometheus для оценки накладных расходов скрапинга."""
        self.client.get("/metrics", headers=AUTH_HEADERS, name="HTTP /metrics")


class GrpcScheduleUser(User):
    """Пользователь симуляции бинарного gRPC протокола между микросервисами."""

    wait_time = between(0.001, 0.004)

    def on_start(self) -> None:
        """Инициализирует постоянный gRPC канал к серверу расписания."""
        host = os.getenv("LOCUST_GRPC_TARGET") or GRPC_SERVER_ADDRESS or "127.0.0.1:50051"
        self.channel = grpc.insecure_channel(host)
        self.stub = schedule_pb2_grpc.ScheduleServiceStub(self.channel)

    def on_stop(self) -> None:
        """Закрывает дескриптор сокета gRPC соединения."""
        if hasattr(self, "channel") and self.channel:
            self.channel.close()

    @task(4)
    def get_day_schedule(self) -> None:
        """Выполняет gRPC запрос GetDaySchedule с фиксацией времени ответа."""
        start = time.perf_counter()
        req = schedule_pb2.DayScheduleRequest(target_date="", force_refresh=False)
        try:
            resp = self.stub.GetDaySchedule(req, timeout=5.0, metadata=GRPC_METADATA)
            _fire_grpc_event("/ScheduleService/GetDaySchedule", start, None, resp.ByteSize())
        except Exception as e:
            _fire_grpc_event("/ScheduleService/GetDaySchedule", start, e)

    @task(2)
    def get_week_schedule(self) -> None:
        """Выполняет gRPC запрос GetWeekSchedule с фиксацией времени ответа."""
        start = time.perf_counter()
        req = schedule_pb2.WeekScheduleRequest(monday="", force_refresh=False)
        try:
            resp = self.stub.GetWeekSchedule(req, timeout=5.0, metadata=GRPC_METADATA)
            _fire_grpc_event("/ScheduleService/GetWeekSchedule", start, None, resp.ByteSize())
        except Exception as e:
            _fire_grpc_event("/ScheduleService/GetWeekSchedule", start, e)
