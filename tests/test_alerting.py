"""
Тесты сервиса алертинга об инцидентах и доставки уведомлений.
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from db.sqlite.models import IncidentSeverity
from services.alerting import (
    IncidentType,
    _format_alert_text,
    _last_alert_timestamps,
    _resolve_alert_destination,
    _should_throttle_alert,
    send_admin_alert,
)


def test_format_alert_text() -> None:
    """Проверяет корректность разметки алерта для Telegram."""
    text = _format_alert_text(
        incident_type=IncidentType.CIRCUIT_BREAKER_OPEN,
        severity=IncidentSeverity.CRITICAL,
        title="Circuit Breaker Open",
        description="Outage detected",
        trace_id="tr-404",
    )
    assert "🚨" in text
    assert "[SYSTEM ALERT] CIRCUIT_BREAKER_OPEN" in text
    assert "tr-404" in text


def test_resolve_alert_destination() -> None:
    """Проверяет маршрутизацию алертов по топикам форума в зависимости от severity."""
    with (
        patch("services.alerting.DEBUG_CHAT_ID", -1004381975171),
        patch("services.alerting.FATAL_THREAD_ID", 7),
        patch("services.alerting.WARNING_THREAD_ID", 5),
        patch("services.alerting.DEBUG_THREAD_ID", 3),
    ):
        assert _resolve_alert_destination(IncidentSeverity.CRITICAL) == (-1004381975171, 7)
        assert _resolve_alert_destination(IncidentSeverity.WARNING) == (-1004381975171, 5)
        assert _resolve_alert_destination(IncidentSeverity.INFO) == (-1004381975171, 3)

    with patch("services.alerting.DEBUG_CHAT_ID", None):
        chat_id, thread_id = _resolve_alert_destination(IncidentSeverity.CRITICAL)
        assert thread_id is None
        assert chat_id is not None


def test_alert_throttling_window() -> None:
    """Проверяет окно троттлинга для предотвращения спама алертов."""
    _last_alert_timestamps.clear()
    inc = "TEST_INCIDENT"

    assert _should_throttle_alert(inc, cooldown_seconds=60.0) is False
    assert _should_throttle_alert(inc, cooldown_seconds=60.0) is True


@pytest.mark.asyncio
async def test_send_admin_alert_success(tmp_path: Path) -> None:
    """Проверяет запись в БД и вызов bot.send_message при алерте."""
    _last_alert_timestamps.clear()
    db_file = tmp_path / "test_alert.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    with patch("core.database.SQLITE_DB_PATH", str(db_file)), patch("core.database.DATABASE_URL", db_url):
        import core.database as db_mod

        db_mod._engine = None
        db_mod._session_factory = None
        await db_mod.init_db()

        mock_send = AsyncMock()
        with patch("services.alerting.bot.send_message", mock_send):
            ok = await send_admin_alert(
                incident_type=IncidentType.YANDEX_COOKIE_EXPIRED,
                title="Yandex Cookie Dead",
                description="Needs renewal",
            )
            assert ok is True
            mock_send.assert_awaited_once()


@pytest.mark.asyncio
async def test_redis_alert_throttling() -> None:
    """Проверяет распределенный троттлинг алертов через Redis set nx."""
    from services.alerting import _check_redis_throttle, _is_alert_throttled

    mock_redis = AsyncMock()
    mock_redis.set.return_value = True  # first call: key set successfully (new alert)
    with patch("core.redis.get_redis", AsyncMock(return_value=mock_redis)):
        assert await _check_redis_throttle("INCIDENT_X", 3600.0) is False
        assert await _is_alert_throttled("INCIDENT_X", 3600.0) is False

    mock_redis.set.return_value = False  # second call: key already exists (throttled)
    with patch("core.redis.get_redis", AsyncMock(return_value=mock_redis)):
        assert await _check_redis_throttle("INCIDENT_X", 3600.0) is True
        assert await _is_alert_throttled("INCIDENT_X", 3600.0) is True
