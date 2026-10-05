"""
Базовый абстрактный класс для всех внешних интеграций.

Задаёт единый интерфейс жизненного цикла внешних сервисов
(DeepSeek, Yandex Documents, Яндекс Диск, КТМУ):
проверку доступности (healthcheck) и безопасное закрытие ресурсов.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from core.logger import get_logger

log = get_logger("integrations_base")


class BaseIntegration(ABC):
    """Абстрактный класс интеграции с внешними API."""

    def __init__(self, service_name: str) -> None:
        # service_name — смысловое наименование внешнего сервиса
        self.service_name = service_name

    @abstractmethod
    async def ping(self) -> bool:
        """
        Проверяет доступность внешнего сервиса.

        Возвращает True если сервис отвечает, иначе False.
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Освобождает сетевые ресурсы и клиенты сессий."""
        raise NotImplementedError
