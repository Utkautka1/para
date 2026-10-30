"""
Сервис мониторинга инцидентов и доставки критических алертов администратору.

Записывает сбои в таблицу system_incidents базы данных SQLite и отправляет
уведомления администратору в Telegram с защитой от лавинообразного спама (cooldown).
"""

import time
from enum import StrEnum

from config import (
    ALLOWED_USER_ID,
    DEBUG_CHAT_ID,
    DEBUG_THREAD_ID,
    FATAL_THREAD_ID,
    WARNING_THREAD_ID,
)
from core.bot import bot
from core.logger import get_logger
from db.sqlite.models import IncidentSeverity
from db.sqlite.repositories import IncidentRepository

log = get_logger("alerting")

_last_alert_timestamps: dict[str, float] = {}


class IncidentType(StrEnum):
    """Типы системных инцидентов и сетевых отказов."""

    CIRCUIT_BREAKER_OPEN = "CIRCUIT_BREAKER_OPEN"
    YANDEX_COOKIE_EXPIRED = "YANDEX_COOKIE_EXPIRED"
    TIMETABLE_API_DOWN = "TIMETABLE_API_DOWN"
    BACKUP_FAILED = "BACKUP_FAILED"
    BACKUP_SUCCESS = "BACKUP_SUCCESS"


DEFAULT_ALERT_COOLDOWNS: dict[str, float] = {
    IncidentType.TIMETABLE_API_DOWN: 3600.0,
    IncidentType.YANDEX_COOKIE_EXPIRED: 7200.0,
    IncidentType.CIRCUIT_BREAKER_OPEN: 1800.0,
    IncidentType.BACKUP_FAILED: 1800.0,
}


async def _check_redis_throttle(incident_type: str, cooldown_seconds: float) -> bool | None:
    """Проверяет и выставляет распределенный ключ кулдауна в Redis."""
    try:
        from core.redis import get_redis

        client = await get_redis()
        if not client:
            return None
        key = f"alert:cooldown:{incident_type}"
        is_new = await client.set(key, "1", ex=int(cooldown_seconds), nx=True)
        return not bool(is_new)
    except Exception as exc:
        log.debug("Сбой проверки распределенного троттлинга Redis: %s", exc)
        return None


def _should_throttle_alert(incident_type: str, cooldown_seconds: float = 300.0) -> bool:
    """Проверяет необходимость локального троттлинга уведомления в памяти процесса."""
    now = time.monotonic()
    if incident_type not in _last_alert_timestamps:
        _last_alert_timestamps[incident_type] = now
        return False
    last_sent = _last_alert_timestamps[incident_type]
    if (now - last_sent) < cooldown_seconds:
        return True
    _last_alert_timestamps[incident_type] = now
    return False


async def _is_alert_throttled(incident_type: str, cooldown_seconds: float) -> bool:
    """Координирует распределенный (Redis) и локальный (память) троттлинг алертов."""
    redis_throttle = await _check_redis_throttle(incident_type, cooldown_seconds)
    if redis_throttle is not None:
        return redis_throttle
    return _should_throttle_alert(incident_type, cooldown_seconds)


def _format_alert_text(
    incident_type: str, severity: str, title: str, description: str, trace_id: str | None = None
) -> str:
    """Форматирует HTML-текст алерта для Telegram."""
    emoji = "🚨" if severity == IncidentSeverity.CRITICAL else "⚠️"
    trace_info = f"\n🔍 <b>Trace ID:</b> <code>{trace_id}</code>" if trace_id else ""
    return (
        f"{emoji} <b>[SYSTEM ALERT] {incident_type}</b>\n"
        f"<b>Статус:</b> {severity}\n"
        f"<b>Событие:</b> {title}\n\n"
        f"📝 <b>Детали:</b>\n{description}"
        f"{trace_info}"
    )


def _resolve_alert_destination(severity: str) -> tuple[int, int | None]:
    """Определяет целевой chat_id и message_thread_id по уровню серьезности алерта."""
    if DEBUG_CHAT_ID:
        if severity == IncidentSeverity.CRITICAL:
            return DEBUG_CHAT_ID, FATAL_THREAD_ID
        if severity == IncidentSeverity.WARNING:
            return DEBUG_CHAT_ID, WARNING_THREAD_ID
        return DEBUG_CHAT_ID, DEBUG_THREAD_ID
    return ALLOWED_USER_ID, None


async def _record_incident_safe(
    incident_type: str,
    severity: str,
    title: str,
    description: str,
    trace_id: str | None,
) -> None:
    """Безопасно сохраняет событие инцидента в базу данных SQLite."""
    try:
        await IncidentRepository.record_incident(
            incident_type=incident_type,
            severity=severity,
            title=title,
            description=description,
            trace_id=trace_id,
        )
    except Exception as exc:
        log.error("Не удалось зафиксировать инцидент в SQLite: %s", exc)


async def _deliver_alert_message(
    incident_type: str,
    severity: str,
    title: str,
    description: str,
    trace_id: str | None,
) -> bool:
    """Форматирует и отправляет сообщение алерта в Telegram."""
    try:
        text = _format_alert_text(incident_type, severity, title, description, trace_id)
        chat_id, thread_id = _resolve_alert_destination(severity)
        await bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=text,
            parse_mode="HTML",
        )
        log.info("✅ Алерт %s доставлен в %s (topic=%s)", incident_type, chat_id, thread_id)
        return True
    except Exception as exc:
        log.error("❌ Ошибка отправки алерта: %s", exc)
        return False


async def send_admin_alert(
    incident_type: str,
    title: str,
    description: str,
    severity: str = IncidentSeverity.WARNING,
    trace_id: str | None = None,
    cooldown_seconds: float | None = None,
) -> bool:
    """Записывает инцидент в SQLite и отправляет Telegram-алерт администратору."""
    await _record_incident_safe(incident_type, severity, title, description, trace_id)
    cooldown = cooldown_seconds or DEFAULT_ALERT_COOLDOWNS.get(incident_type, 1800.0)
    if await _is_alert_throttled(incident_type, cooldown):
        log.debug("Алерт %s пропущен из-за кулдауна троттлинга", incident_type)
        return False
    return await _deliver_alert_message(incident_type, severity, title, description, trace_id)
