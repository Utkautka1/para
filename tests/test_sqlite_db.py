"""
Тесты реляционной базы данных SQLite (SQLAlchemy 2.0 + aiosqlite).
"""

from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import text

from core.database import get_async_session, init_db
from db.sqlite.models import IncidentSeverity
from db.sqlite.repositories import AttendanceRepository, IncidentRepository, SubscriberRepository


@pytest.mark.asyncio
async def test_init_db_creates_tables_and_pragmas(tmp_path: Path) -> None:
    """Проверяет создание реляционных таблиц и установку WAL-режима."""
    db_file = tmp_path / "test_para.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    with patch("core.database.SQLITE_DB_PATH", str(db_file)), patch("core.database.DATABASE_URL", db_url):
        import core.database as db_mod

        db_mod._engine = None
        db_mod._session_factory = None
        await init_db()

        async with get_async_session() as session:
            res = await session.execute(text("PRAGMA journal_mode;"))
            journal_mode = res.scalar()
            assert str(journal_mode).lower() == "wal"


@pytest.mark.asyncio
async def test_subscriber_repository_crud(tmp_path: Path) -> None:
    """Проверяет добавление, деактивацию и подсчет подписчиков в SQLite."""
    db_file = tmp_path / "test_subs.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    with (
        patch("core.database.SQLITE_DB_PATH", str(db_file)),
        patch("core.database.DATABASE_URL", db_url),
        patch("core.database.SUBSCRIBERS_FILE_PATH", str(tmp_path / "nonexistent.json")),
    ):
        import core.database as db_mod

        db_mod._engine = None
        db_mod._session_factory = None
        await init_db()

        added = await SubscriberRepository.add_subscriber(123456, "alice", "Alice Smith")
        assert added is True

        added_again = await SubscriberRepository.add_subscriber(123456)
        assert added_again is False

        subs = await SubscriberRepository.get_active_chat_ids()
        assert 123456 in subs
        assert await SubscriberRepository.count_active() == 1

        removed = await SubscriberRepository.remove_subscriber(123456)
        assert removed is True
        assert await SubscriberRepository.count_active() == 0


@pytest.mark.asyncio
async def test_incident_repository(tmp_path: Path) -> None:
    """Проверяет фиксацию и чтение системных инцидентов."""
    db_file = tmp_path / "test_incidents.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    with patch("core.database.SQLITE_DB_PATH", str(db_file)), patch("core.database.DATABASE_URL", db_url):
        import core.database as db_mod

        db_mod._engine = None
        db_mod._session_factory = None
        await init_db()

        incident = await IncidentRepository.record_incident(
            incident_type="CIRCUIT_BREAKER_OPEN",
            title="DeepSeek API Degraded",
            description="500 Internal Server Error",
            severity=IncidentSeverity.CRITICAL,
            trace_id="tr-test-123",
        )
        assert incident.id is not None

        recent = await IncidentRepository.get_recent_incidents(limit=10)
        assert len(recent) == 1
        assert recent[0].title == "DeepSeek API Degraded"


@pytest.mark.asyncio
async def test_attendance_repository_snapshots(tmp_path: Path) -> None:
    """Проверяет сохранение среза посещаемости студентов."""
    db_file = tmp_path / "test_att.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"

    with patch("core.database.SQLITE_DB_PATH", str(db_file)), patch("core.database.DATABASE_URL", db_url):
        import core.database as db_mod

        db_mod._engine = None
        db_mod._session_factory = None
        await init_db()

        records = [
            {"name": "Иванов Иван", "total_hours": 40, "attended_hours": 36, "percent": 90.0},
            {"name": "Петров Петр", "total_hours": 40, "attended_hours": 20, "percent": 50.0},
        ]
        saved = await AttendanceRepository.save_daily_snapshots(date(2026, 10, 19), records)
        assert saved == 2
