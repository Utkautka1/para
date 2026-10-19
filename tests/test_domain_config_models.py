"""
Тесты валидации доменных моделей конфигурации и обратной совместимости config.py.

Проверяют целостность объектов TelegramConfig, ScheduleConfig, CampusConfig,
RedisConfig, YandexConfig, ApiConfig, AiSolverConfig, WhisperConfig и NotificationConfig,
а также гарантируют корректную привязку глобальных констант к полям моделей.
"""

from dataclasses import FrozenInstanceError
from zoneinfo import ZoneInfo

import pytest

import config
from core.config_models import (
    AiSolverConfig,
    ApiConfig,
    CampusConfig,
    NotificationConfig,
    RedisConfig,
    ScheduleConfig,
    TelegramConfig,
    WhisperConfig,
    YandexConfig,
)


def test_telegram_config_instance() -> None:
    """Проверяет корректность типов и вычисляемых свойств объекта TelegramConfig."""
    cfg = config.telegram_config
    assert isinstance(cfg, TelegramConfig)
    assert cfg.bot_token == config.BOT_TOKEN
    assert cfg.allowed_user_id == config.ALLOWED_USER_ID
    assert cfg.deputy_user_id == config.DEPUTY_USER_ID
    assert cfg.allowed_attendance_user_ids == {config.ALLOWED_USER_ID, config.DEPUTY_USER_ID}
    assert cfg.group_id == config.GROUP_ID
    assert cfg.topic_chat_id == config.TOPIC_CHAT_ID


def test_schedule_config_instance() -> None:
    """Проверяет эндпоинты расписания, таймзону и параметры кэширования ScheduleConfig."""
    cfg = config.schedule_config
    assert isinstance(cfg, ScheduleConfig)
    assert cfg.api_url == config.SCHEDULE_API_URL
    assert cfg.fallback_api_url == config.SCHEDULE_FALLBACK_API_URL
    assert isinstance(cfg.timezone, ZoneInfo)
    assert cfg.timezone.key == config.TIMEZONE_NAME
    assert cfg.cache_ttl_seconds == config.SCHEDULE_CACHE_TTL_SECONDS


def test_campus_and_redis_configs() -> None:
    """Проверяет адреса корпусов колледжа и сетевые параметры брокера Redis."""
    assert isinstance(config.campus_config, CampusConfig)
    assert config.campus_config.voznesensky == config.CAMPUS_ADDRESS_VOZNESENSKY
    assert isinstance(config.redis_config, RedisConfig)
    assert config.redis_config.host == config.REDIS_HOST
    assert config.redis_config.port == config.REDIS_PORT
    assert config.redis_config.password == config.REDIS_PASSWORD


def test_yandex_and_api_configs() -> None:
    """Проверяет конфигурацию WOPI-интеграции Яндекс Документов и шлюза API."""
    assert isinstance(config.yandex_config, YandexConfig)
    assert config.yandex_config.doc_public_url == config.YANDEX_DOC_PUBLIC_URL
    assert isinstance(config.api_config, ApiConfig)
    assert config.api_config.secret_key == config.API_SECRET_KEY
    assert config.api_config.grpc_port == config.GRPC_PORT
    assert config.api_config.swagger_url == config.SWAGGER_URL


def test_solver_whisper_and_notify_configs() -> None:
    """Проверяет конфигурацию DeepSeek AI, faster-whisper STT и таймеров нотификаций."""
    assert isinstance(config.solver_config, AiSolverConfig)
    assert config.solver_config.api_key == config.DEEPSEEK_API_KEY
    assert isinstance(config.whisper_config, WhisperConfig)
    assert config.whisper_config.model_name == config.WHISPER_MODEL_NAME
    assert isinstance(config.notify_config, NotificationConfig)
    assert config.notify_config.daily_notify_hour == config.DAILY_NOTIFY_HOUR


def test_domain_configs_immutability() -> None:
    """Проверяет неизменяемость (frozen dataclass) доменных конфигураций."""
    with pytest.raises(FrozenInstanceError):
        config.telegram_config.allowed_user_id = 999999  # type: ignore[misc]
