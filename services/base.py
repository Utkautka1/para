"""
Базовый класс внутренних сервисов и менеджеров.

Определяет общий жизненный цикл фоновых воркеров и управляющих сервисов:
инициализацию зависимостей, циклический запуск и корректную остановку.
"""
from abc import ABC, abstractmethod

from core.logger import get_logger

log = get_logger("services_base")


class BaseServiceManager(ABC):
    """Абстрактный базовый класс для менеджеров бизнес-логики."""

    def __init__(self, name: str) -> None:
        # name — системный идентификатор менеджера для логирования
        self.name = name
        self._is_running = False

    @abstractmethod
    async def start(self) -> None:
        """Запускает рабочий цикл менеджера."""
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        """Корректно останавливает менеджер с сохранением состояния."""
        raise NotImplementedError
