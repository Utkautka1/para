"""
Модуль конфигурации бота расписания КТМУ.

Считывает все параметры исключительно из файла .env без хардкод-значений.
При отсутствии любой из обязательных переменных выбрасывает исключение ValueError.
"""

import os
from dotenv import load_dotenv


# Загружаем переменные окружения из файла .env
load_dotenv()


def get_required_env(key: str) -> str:
    """
    Извлекает обязательную переменную из .env или вызывает ValueError.

    :param key: Название ключа переменной
    :return: Значение переменной из окружения
    """
    val = os.getenv(key)
    if not val:
        raise ValueError(f"ОШИБКА: Обязательная переменная '{key}' отсутствует в .env файле!")
    return val


# Токен бота и авторизованный Telegram ID
BOT_TOKEN: str = get_required_env("BOT_TOKEN")
ALLOWED_USER_ID: int = int(get_required_env("ALLOWED_USER_ID"))

# URL-адреса API расписания и Яндекс Диска
SCHEDULE_API_URL: str = get_required_env("SCHEDULE_API_URL")
YANDEX_DOC_PUBLIC_URL: str = get_required_env("YANDEX_DOC_PUBLIC_URL")

# Параметры целевой группы
GROUP_ID: str = get_required_env("GROUP_ID")
GROUP_NAME: str = get_required_env("GROUP_NAME")

# Часовой пояс проекта
TIMEZONE_NAME: str = get_required_env("TIMEZONE")
from zoneinfo import ZoneInfo
TIMEZONE = ZoneInfo(TIMEZONE_NAME)

# Интервалы рассылок и кэширования
DAILY_NOTIFY_HOUR: int = int(get_required_env("DAILY_NOTIFY_HOUR"))
DAILY_NOTIFY_MINUTE: int = int(get_required_env("DAILY_NOTIFY_MINUTE"))
REMINDER_OFFSET_MINUTES: int = int(get_required_env("REMINDER_OFFSET_MINUTES"))
DOCX_CACHE_TTL_SECONDS: int = int(get_required_env("DOCX_CACHE_TTL_SECONDS"))
SCHEDULE_CACHE_TTL_SECONDS: int = int(get_required_env("SCHEDULE_CACHE_TTL_SECONDS"))

# Настройки топика группы Telegram
TOPIC_CHAT_ID: int = int(get_required_env("TOPIC_CHAT_ID"))
TOPIC_THREAD_ID: int = int(get_required_env("TOPIC_THREAD_ID"))
EXAM_TOPIC_THREAD_ID: int = int(get_required_env("EXAM_TOPIC_THREAD_ID"))
FLOOD_TOPIC_THREAD_ID: int = int(os.getenv("FLOOD_TOPIC_THREAD_ID", "4"))
EXAM_SCHEDULE_API_URL: str = get_required_env("EXAM_SCHEDULE_API_URL")

# Настройки прокси (опционально)
PROXY_URL: str | None = os.getenv("PROXY_URL")

# Файл с подписками
SUBSCRIBERS_FILE_PATH: str = "data/subscribers.json"
