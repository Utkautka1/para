"""
Сервис мониторинга инцидентов и доставки критических алертов администратору.

Записывает сбои в таблицу system_incidents базы данных SQLite и отправляет
уведомления администратору в Telegram с защитой от лавинообразного спама (cooldown).
"""

import time
from enum import StrEnum

from config import ALLOWED_USER_ID
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


def _should_throttle_alert(incident_type: str, cooldown_seconds: float = 300.0) -> bool:
    """Проверяет необходимость троттлинга уведомления для предотвращения спама."""
    now = time.monotonic()
    last_sent = _last_alert_timestamps.get(incident_type, 0.0)
    if (now - last_sent) < cooldown_seconds:
        return True
    _last_alert_timestamps[incident_type] = now
    return False


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


async def send_admin_alert(
    incident_type: str,
    title: str,
    description: str,
    severity: str = IncidentSeverity.WARNING,
    trace_id: str | None = None,
) -> bool:
    """Записывает инцидент в SQLite и отправляет Telegram-алерт администратору."""
    try:
        await IncidentRepository.record_incident(
            incident_type=incident_type,
            severity=severity,
            title=title,
            description=description,
            trace_id=trace_id,
        )
    except Exception as exc:
        log.error(f"Не удалось зафиксировать инцидент в SQLite: {exc}")

    if _should_throttle_alert(incident_type):
        log.debug(f"Алерт {incident_type} пропущен из-за кулдауна троттлинга")
        return False

    try:
        text = _format_alert_text(incident_type, severity, title, description, trace_id)
        await bot.send_message(chat_id=ALLOWED_USER_ID, text=text, parse_mode="HTML")
        log.info(f"✅ Алерт {incident_type} успешно доставлен администратору {ALLOWED_USER_ID}")
        return True
    except Exception as exc:
        log.error(f"❌ Ошибка отправки алерта администратору: {exc}")
        return False
