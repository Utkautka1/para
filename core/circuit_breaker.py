"""
Модуль асинхронного Circuit Breaker и повторных попыток с экспоненциальным backoff.

Предотвращает каскадные сбои при деградации внешних сетевых сервисов
(DeepSeek AI API, Yandex WOPI, Telegram Bot API) за счет быстрого отсечения запросов.
"""

import asyncio
from enum import Enum
import random
import time
from typing import Any, Awaitable, Callable, TypeVar

from core.logger import get_logger

log = get_logger("circuit_breaker")

T = TypeVar("T")


class CircuitState(str, Enum):
    """Состояния конечного автомата Circuit Breaker."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    """Исключение, выбрасываемое при блокировке запроса открытым Circuit Breaker."""

    def __init__(self, name: str, retry_after: float):
        super().__init__(f"Circuit '{name}' is OPEN. Retry after {retry_after:.1f}s")
        self.name = name
        self.retry_after = retry_after


class CircuitBreaker:
    """Управляет защитой внешних вызовов от каскадных сбоев."""

    def __init__(self, name: str, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_state_change = time.monotonic()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Возвращает актуальное состояние с учетом истечения recovery timeout."""
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_state_change
            if elapsed >= self.recovery_timeout:
                return CircuitState.HALF_OPEN
        return self._state

    async def check_permission(self) -> None:
        """Проверяет право на выполнение запроса или выбрасывает CircuitOpenError."""
        async with self._lock:
            current_state = self.state
            if current_state == CircuitState.OPEN:
                wait_time = self.recovery_timeout - (time.monotonic() - self._last_state_change)
                raise CircuitOpenError(self.name, max(0.0, wait_time))
            if current_state == CircuitState.HALF_OPEN and self._state != CircuitState.HALF_OPEN:
                self._state = CircuitState.HALF_OPEN
                log.info(f"⚡ CircuitBreaker '{self.name}': OPEN -> HALF_OPEN (пробный запрос)")

    async def record_success(self) -> None:
        """Сбрасывает счетчик ошибок при успешном завершении запроса."""
        async with self._lock:
            if self._state != CircuitState.CLOSED:
                log.info(f"✅ CircuitBreaker '{self.name}': {self._state.value} -> CLOSED (сервис восстановился)")
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_state_change = time.monotonic()

    async def record_failure(self, error: Exception) -> None:
        """Фиксирует сбой и переводит в OPEN при превышении порога."""
        async with self._lock:
            self._failure_count += 1
            self._last_state_change = time.monotonic()
            log.warning(f"⚠️ CircuitBreaker '{self.name}': ошибка #{self._failure_count}: {error}")
            if self._failure_count >= self.failure_threshold or self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                log.error(f"🛑 CircuitBreaker '{self.name}' перешел в состояние OPEN на {self.recovery_timeout}с")


async def async_retry_with_backoff(
    coro_fn: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Выполняет асинхронную операцию с экспоненциальным backoff и jitter."""
    attempt = 0
    while True:
        try:
            return await coro_fn()
        except retryable_exceptions as exc:
            attempt += 1
            if attempt > max_retries:
                log.error(f"❌ Превышено число повторных попыток ({max_retries}): {exc}")
                raise
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0.0, 0.2 * delay)
            total_delay = delay + jitter
            log.warning(f"🔄 Retry #{attempt}/{max_retries} через {total_delay:.2f}с из-за ошибки: {exc}")
            await asyncio.sleep(total_delay)
