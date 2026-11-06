"""
Доменные модели конфигурации распределенной системы Para.

Определяют строго типизированные контейнеры настроек по подсистемам:
Telegram, расписание, кампусы, Redis, Яндекс Документы, API Gateway,
AI Solver (DeepSeek), распознавание речи (Whisper) и уведомления.
"""

from dataclasses import dataclass
from zoneinfo import ZoneInfo


@dataclass(frozen=True, slots=True)
class TelegramConfig:
    """Конфигурация Telegram-бота, ролевого доступа и идентификаторов топиков форума."""

    bot_token: str
    allowed_user_id: int
    deputy_user_id: int
    group_id: str
    group_name: str
    topic_chat_id: int
    topic_thread_id: int
    exam_topic_thread_id: int
    flood_topic_thread_id: int
    birthday_topic_thread_id: int
    important_topic_thread_id: int
    attendance_topic_thread_id: int
    hw_input_topic_thread_id: int
    hw_output_topic_thread_id: int
    admin_user_ids: tuple[int, ...] = ()
    debug_chat_id: int | None = None
    debug_thread_id: int | None = None
    warning_thread_id: int | None = None
    fatal_thread_id: int | None = None

    @property
    def allowed_admin_user_ids(self) -> set[int]:
        """Все главные администраторы (включая указанных через запятую в ALLOWED_USER_ID)."""
        base = {self.allowed_user_id}
        if self.admin_user_ids:
            base.update(self.admin_user_ids)
        return base

    @property
    def allowed_attendance_user_ids(self) -> set[int]:
        """Множество доверенных администраторов для фиксации посещаемости."""
        return self.allowed_admin_user_ids | {self.deputy_user_id}


@dataclass(frozen=True, slots=True)
class ScheduleConfig:
    """Конфигурация внешних эндпоинтов расписания КТМУ, таймзоны и параметров кэширования."""

    default_fallback_api_url: str
    api_url: str
    fallback_api_url: str
    exam_api_url: str
    exam_fallback_api_url: str
    timezone_name: str
    cache_ttl_seconds: int
    cooldown_seconds: int = 300
    docx_cache_ttl_seconds: int = 300
    docx_min_refresh_interval_seconds: float = 30.0

    @property
    def timezone(self) -> ZoneInfo:
        """Объект таймзоны для синхронизации расписания занятий."""
        return ZoneInfo(self.timezone_name)


@dataclass(frozen=True, slots=True)
class CampusConfig:
    """Конфигурация физических корпусов и удаленных локаций колледжа."""

    voznesensky: str
    tsvetochnaya: str
    remote: str


@dataclass(frozen=True, slots=True)
class RedisConfig:
    """Конфигурация подключения к серверу Redis и глобального L2 кэширования."""

    host: str
    port: int
    password: str
    cache_ttl_seconds: int
    snapshot_key: str = "schedule:snapshot"
    snapshot_meta_key: str = "schedule:snapshot:meta"
    topic_cleanup_key: str = "cleanup:topic_messages"


@dataclass(frozen=True, slots=True)
class YandexConfig:
    """Конфигурация интеграции с Яндекс Документами и журналами посещаемости WOPI."""

    doc_public_url: str
    attendance_doc_url: str
    sync_day_interval_seconds: int
    sync_night_interval_seconds: int
    session_id: str
    cookie: str
    keepalive_interval_seconds: int
    cookie_test_doc_url: str
    required_cookie_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ApiConfig:
    """Конфигурация двухпротокольного API-шлюза (HTTP/REST и gRPC HTTP/2)."""

    secret_key: str
    # Ключ подписи сессий Mini App/Swagger; пустой — подписываем secret_key (обратная совместимость)
    session_secret: str
    base_url: str
    host: str
    port: int
    external_port: int
    swagger_url: str
    swagger_servers_url: str
    swagger_servers_description: str
    swagger_mask_host_pattern: str
    grpc_host: str
    grpc_port: int
    grpc_server_address: str
    grpc_max_message_length: int
    miniapp_url: str
    redis_testers_key: str
    session_max_age_seconds: int
    redis_tester_key_to_uid_prefix: str
    redis_tester_uid_to_key_prefix: str
    api_tester_key_prefix: str
    grpc_keepalive_time_ms: int = 10000
    grpc_keepalive_timeout_ms: int = 5000
    grpc_keepalive_permit_without_calls: int = 1
    grpc_http2_max_pings_without_data: int = 0
    grpc_http2_min_ping_interval_ms: int = 5000
    gzip_min_size_bytes: int = 1000
    http_pool_max_keepalive_connections: int = 5
    http_pool_max_connections: int = 10
    http_client_timeout_seconds: float = 60.0


@dataclass(frozen=True, slots=True)
class AiSolverConfig:
    """Конфигурация очередей и клиента модели DeepSeek для решения домашних заданий."""

    api_key: str
    api_base: str
    model_name: str
    timeout_seconds: float
    system_prompt: str
    max_file_size: int = 20 * 1024 * 1024
    max_prompt_text_length: int = 15000
    max_task_retries: int = 3
    max_image_base64_bytes: int = 28 * 1024 * 1024
    max_concurrent_tasks: int = 3
    rate_limit_per_minute: int = 5
    rate_limit_window_seconds: int = 60


@dataclass(frozen=True, slots=True)
class WhisperConfig:
    """Конфигурация модели распознавания речи faster-whisper и лимитов аудио."""

    model_name: str
    device: str
    compute_type: str
    download_root: str
    language: str
    beam_size: int
    max_audio_duration: int = 300
    max_audio_size: int = 20 * 1024 * 1024
    max_concurrent_per_user: int = 2
    download_timeout: float = 25.0
    transcribe_timeout: float = 90.0


@dataclass(frozen=True, slots=True)
class NotificationConfig:
    """Конфигурация расписания уведомлений и параметров троттлинга инлайн-кнопок."""

    daily_notify_hour: int
    daily_notify_minute: int
    reminder_offset_minutes: int
    throttling_heavy_cooldown: float = 4.0
    throttling_nav_cooldown: float = 1.0
    throttling_default_cooldown: float = 0.5


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    """Конфигурация реляционной базы данных SQLite и параметров резервного копирования."""

    db_path: str = "data/para.db"
    database_url: str = "sqlite+aiosqlite:///data/para.db"
    backup_dir: str = "data/backups"
    backup_retention_days: int = 7


@dataclass(frozen=True, slots=True)
class TracingConfig:
    """Конфигурация распределенного трейсинга OpenTelemetry и Jaeger OTLP."""

    enabled: bool = True
    otlp_endpoint: str = "http://jaeger:4317"
    service_name: str = "para"
    jaeger_ui_url: str = "http://jaeger:16686"
    sampling_ratio: float = 1.0
