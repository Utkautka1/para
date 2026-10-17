"""
Модуль конфигурации бота расписания КТМУ.

Считывает все параметры исключительно из файла .env без хардкод-значений.
При отсутствии любой из обязательных переменных выбрасывает исключение ValueError.
"""

import os
from zoneinfo import ZoneInfo

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
SCHEDULE_FALLBACK_API_URL: str = os.getenv("SCHEDULE_FALLBACK_API_URL", "")
YANDEX_DOC_PUBLIC_URL: str = get_required_env("YANDEX_DOC_PUBLIC_URL")

# Параметры целевой группы
GROUP_ID: str = get_required_env("GROUP_ID")
GROUP_NAME: str = get_required_env("GROUP_NAME")

# Часовой пояс проекта
TIMEZONE_NAME: str = get_required_env("TIMEZONE")
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
BIRTHDAY_TOPIC_THREAD_ID: int = int(get_required_env("BIRTHDAY_TOPIC_THREAD_ID"))
IMPORTANT_TOPIC_THREAD_ID: int = int(get_required_env("IMPORTANT_TOPIC_THREAD_ID"))
ATTENDANCE_TOPIC_THREAD_ID: int = int(get_required_env("ATTENDANCE_TOPIC_THREAD_ID"))
EXAM_SCHEDULE_API_URL: str = get_required_env("EXAM_SCHEDULE_API_URL")
EXAM_SCHEDULE_FALLBACK_API_URL: str = os.getenv("EXAM_SCHEDULE_FALLBACK_API_URL", "")

# Настройки прокси (опционально)
PROXY_URL: str | None = os.getenv("PROXY_URL")

# Файл с подписками
SUBSCRIBERS_FILE_PATH: str = "data/subscribers.json"

# Настройки Redis
REDIS_HOST: str = get_required_env("REDIS_HOST")
REDIS_PORT: int = int(get_required_env("REDIS_PORT"))
REDIS_PASSWORD: str = get_required_env("REDIS_PASSWORD")
REDIS_CACHE_TTL_SECONDS: int = int(get_required_env("REDIS_CACHE_TTL_SECONDS"))

# Настройки DeepSeek HW Solver
DEEPSEEK_API_KEY: str = get_required_env("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL_NAME: str = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash-vision-exp")
HW_INPUT_TOPIC_THREAD_ID: int = int(get_required_env("HW_INPUT_TOPIC_THREAD_ID"))
HW_OUTPUT_TOPIC_THREAD_ID: int = int(get_required_env("HW_OUTPUT_TOPIC_THREAD_ID"))

# Настройки внутреннего API (para-api)
API_SECRET_KEY: str = get_required_env("API_SECRET_KEY")
API_BASE_URL: str = get_required_env("API_BASE_URL")
API_HOST: str = get_required_env("API_HOST")
API_PORT: int = int(get_required_env("API_PORT"))
API_EXTERNAL_PORT: int = int(get_required_env("API_EXTERNAL_PORT"))
SWAGGER_URL: str = get_required_env("SWAGGER_URL")
GRPC_HOST: str = get_required_env("GRPC_HOST")
GRPC_PORT: int = int(get_required_env("GRPC_PORT"))
GRPC_SERVER_ADDRESS: str = get_required_env("GRPC_SERVER_ADDRESS")
GRPC_MAX_MESSAGE_LENGTH: int = int(get_required_env("GRPC_MAX_MESSAGE_LENGTH"))
MINIAPP_URL: str = get_required_env("MINIAPP_URL")
REDIS_TESTERS_KEY: str = get_required_env("REDIS_TESTERS_KEY")
SESSION_MAX_AGE_SECONDS: int = int(get_required_env("SESSION_MAX_AGE_SECONDS"))
REDIS_TESTER_KEY_TO_UID_PREFIX: str = get_required_env("REDIS_TESTER_KEY_TO_UID_PREFIX")
REDIS_TESTER_UID_TO_KEY_PREFIX: str = get_required_env("REDIS_TESTER_UID_TO_KEY_PREFIX")
API_TESTER_KEY_PREFIX: str = get_required_env("API_TESTER_KEY_PREFIX")

# Настройки отметки посещаемости (староста и замстаросты)
DEPUTY_USER_ID: int = int(get_required_env("DEPUTY_USER_ID"))
ALLOWED_ATTENDANCE_USER_IDS: set[int] = {ALLOWED_USER_ID, DEPUTY_USER_ID}
ATTENDANCE_DOC_URL: str = get_required_env("ATTENDANCE_DOC_URL")
ATTENDANCE_SYNC_DAY_INTERVAL_SECONDS: int = int(os.getenv("ATTENDANCE_SYNC_DAY_INTERVAL_SECONDS", "180"))
ATTENDANCE_SYNC_NIGHT_INTERVAL_SECONDS: int = int(os.getenv("ATTENDANCE_SYNC_NIGHT_INTERVAL_SECONDS", "900"))
YANDEX_SESSION_ID: str = os.getenv("YANDEX_SESSION_ID", "")
YANDEX_COOKIE: str = os.getenv("YANDEX_COOKIE", "")

# Ключ хранения актуальных Cookie в Redis и их TTL (60 дней)
REDIS_YANDEX_COOKIE_KEY: str = "yandex:session_cookie"
REDIS_COOKIE_TTL_SECONDS: int = 5184000

# Централизованные пути к файлам данных
BIRTHDAYS_FILE_PATH: str = "data/birthdays.json"
WISHES_FILE_PATH: str = "data/birthday_wishes.json"
STAROSTA_WISHES_FILE_PATH: str = "data/starosta_wishes.json"
BIRTHDAY_TOPIC_STATE_FILE: str = "data/birthday_topic_state.json"
HISTORY_FILE_PATH: str = "data/birthday_history.json"
STAROSTA_HISTORY_FILE_PATH: str = "data/starosta_history.json"
CONGRATS_STATE_FILE_PATH: str = "data/birthday_congrats_state.json"
EXAM_TOPIC_STATE_FILE: str = "data/exam_topic_state.json"
ATTENDANCE_TOPIC_STATE_FILE: str = "data/attendance_topic_state.json"
TOPIC_STATE_FILE: str = "data/topic_state.json"
USER_CACHE_FILE_PATH: str = "data/user_cache.json"
CUSTOM_TEACHERS_FILE_PATH: str = "data/custom_teachers.json"

# Лимиты и таймауты фонового решебника ДЗ
HW_MAX_FILE_SIZE: int = 20 * 1024 * 1024
HW_MAX_PROMPT_TEXT_LENGTH: int = 15000
HW_MAX_TASK_RETRIES: int = 3
HW_QUEUE_KEY: str = "hw:tasks:queue"
HW_PROCESSING_KEY: str = "hw:tasks:processing"
HW_DLQ_KEY: str = "hw:tasks:dlq"

# Ключи расписания и отложенной очистки сообщений в Redis
SNAPSHOT_KEY: str = "schedule:snapshot"
SNAPSHOT_META_KEY: str = "schedule:snapshot:meta"
TOPIC_CLEANUP_KEY: str = "cleanup:topic_messages"

# Параметры сессий отметки посещаемости
ATTENDANCE_SESSION_TTL_SECONDS: int = 7200
ATTENDANCE_MAX_COMMIT_RETRIES: int = 3
ATTENDANCE_COMMIT_RETRY_DELAY_SECONDS: int = 5
ATTENDANCE_STATS_CACHE_TTL_SECONDS: int = 300
SCHEDULE_COOLDOWN_SECONDS: int = 300


# Лимиты безопасности для голосовых сообщений в Telegram боте
MAX_AUDIO_DURATION: int = 300  # 5 минут
MAX_AUDIO_SIZE: int = 20 * 1024 * 1024  # 20 МБ
MAX_CONCURRENT_PER_USER: int = 2  # максимум одновременных аудио на пользователя
DOWNLOAD_TIMEOUT: float = 25.0  # секунд
TRANSCRIBE_TIMEOUT: float = 90.0  # секунд

_USER_IN_FLIGHT: dict[int, int] = {}

# Параметры параллелизма и Rate Limiting решателя ДЗ
SOLVER_MAX_CONCURRENT_TASKS: int = int(os.getenv("SOLVER_MAX_CONCURRENT_TASKS", "3"))
SOLVER_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("SOLVER_RATE_LIMIT_PER_MINUTE", "5"))
SOLVER_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("SOLVER_RATE_LIMIT_WINDOW_SECONDS", "60"))

# Кэширование посещаемости и срезов отметок
REDIS_STUDENTS_CACHE_KEY: str = os.getenv("REDIS_STUDENTS_CACHE_KEY", "att:cached_students")
STUDENTS_CACHE_TTL_SECONDS: int = int(os.getenv("STUDENTS_CACHE_TTL_SECONDS", "86400"))
REDIS_MARKS_CACHE_PREFIX: str = os.getenv("REDIS_MARKS_CACHE_PREFIX", "att:marks")
MARKS_CACHE_TTL_SECONDS: int = int(os.getenv("MARKS_CACHE_TTL_SECONDS", "2592000"))

# Безопасные префиксы для очистки кэша
SAFE_CACHE_FLUSH_PREFIXES: tuple[str, ...] = ("sched:", "att:", "teachers:", "exams:", "hw_hash:", "rem:")

# Параметры gRPC Keepalive и HTTP/2 сокетов
GRPC_KEEPALIVE_TIME_MS: int = int(os.getenv("GRPC_KEEPALIVE_TIME_MS", "10000"))
GRPC_KEEPALIVE_TIMEOUT_MS: int = int(os.getenv("GRPC_KEEPALIVE_TIMEOUT_MS", "5000"))
GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS: int = int(os.getenv("GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS", "1"))
GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA: int = int(os.getenv("GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA", "0"))
GRPC_HTTP2_MIN_PING_INTERVAL_MS: int = int(os.getenv("GRPC_HTTP2_MIN_PING_INTERVAL_MS", "5000"))

# Сжатие ответов API
GZIP_MIN_SIZE_BYTES: int = int(os.getenv("GZIP_MIN_SIZE_BYTES", "1000"))

# Физические адреса корпусов учебного заведения
CAMPUS_ADDRESS_VOZNESENSKY: str = os.getenv("CAMPUS_ADDRESS_VOZNESENSKY", "Вознесенский пр., 44")
CAMPUS_ADDRESS_TSVETOCHNAYA: str = os.getenv("CAMPUS_ADDRESS_TSVETOCHNAYA", "ул. Цветочная, д. 8")
CAMPUS_ADDRESS_REMOTE: str = "Дистанционно"

# Пулы соединений HTTP-клиента
HTTP_POOL_MAX_KEEPALIVE_CONNECTIONS: int = int(os.getenv("HTTP_POOL_MAX_KEEPALIVE_CONNECTIONS", "5"))
HTTP_POOL_MAX_CONNECTIONS: int = int(os.getenv("HTTP_POOL_MAX_CONNECTIONS", "10"))
HTTP_CLIENT_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_CLIENT_TIMEOUT_SECONDS", "60.0"))

# Конфигурация Swagger UI и маскирования хоста
SWAGGER_SERVERS_URL: str = get_required_env("SWAGGER_SERVERS_URL")
SWAGGER_SERVERS_DESCRIPTION: str = get_required_env("SWAGGER_SERVERS_DESCRIPTION")
SWAGGER_MASK_HOST_PATTERN: str = get_required_env("SWAGGER_MASK_HOST_PATTERN")

# Настройки распознавания речи Whisper (только из .env)
WHISPER_MODEL_NAME: str = get_required_env("WHISPER_MODEL_NAME")
WHISPER_DEVICE: str = get_required_env("WHISPER_DEVICE")
WHISPER_COMPUTE_TYPE: str = get_required_env("WHISPER_COMPUTE_TYPE")
WHISPER_DOWNLOAD_ROOT: str = get_required_env("WHISPER_DOWNLOAD_ROOT")
WHISPER_LANGUAGE: str = get_required_env("WHISPER_LANGUAGE")
WHISPER_BEAM_SIZE: int = int(get_required_env("WHISPER_BEAM_SIZE"))



