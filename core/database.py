"""
Модуль управления асинхронным подключением к реляционной БД SQLite (SQLAlchemy 2.0).

Настраивает пул соединений с принудительным включением WAL-режима (Write-Ahead Logging),
проверки внешних ключей и быстрого таймаута ожидания блокировок (busy_timeout).
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import event, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from config import DATABASE_URL, SQLITE_DB_PATH, SUBSCRIBERS_FILE_PATH
from core.logger import get_logger
from core.telemetry import trace_span
from utils.storage import sync_load_json

log = get_logger("database")

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
    """Устанавливает оптимальные PRAGMA параметры для SQLite при каждом новом подключении."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA busy_timeout=5000;")
    cursor.close()


def get_database_engine() -> AsyncEngine:
    """Возвращает синглтон асинхронного движка SQLAlchemy для SQLite."""
    global _engine
    if _engine is None:
        os.makedirs(os.path.dirname(SQLITE_DB_PATH) or ".", exist_ok=True)
        _engine = create_async_engine(
            DATABASE_URL,
            poolclass=NullPool,
            echo=False,
            future=True,
        )
        event.listen(_engine.sync_engine, "connect", _set_sqlite_pragmas)
        log.info(f"Инициализирован движок SQLite: {SQLITE_DB_PATH} (WAL-mode)")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Возвращает фабрику асинхронных сессий SQLAlchemy."""
    global _session_factory
    if _session_factory is None:
        engine = get_database_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Контекстный менеджер для безопасной работы с асинхронной сессией БД."""
    factory = get_session_factory()
    async with trace_span("sqlite.session", attributes={"db.system": "sqlite"}), factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def _migrate_subscribers_from_json(session: AsyncSession) -> None:
    """Выполняет плавную однократную миграцию подписчиков из subscribers.json в SQLite."""
    from db.sqlite.models import Subscriber

    sub_count = (await session.execute(select(Subscriber))).scalars().first()
    if sub_count is not None or not os.path.exists(SUBSCRIBERS_FILE_PATH):
        return

    data = sync_load_json(SUBSCRIBERS_FILE_PATH, default=[])
    if isinstance(data, list) and data:
        for chat_id in set(data):
            session.add(Subscriber(chat_id=int(chat_id), is_active=True))
        await session.flush()
        log.info(f"✅ Успешно мигрировано {len(data)} подписчиков из JSON в SQLite")


def _migrate_attendance_snapshot_columns(conn: Any) -> None:
    """Добавляет недостающие столбцы посещаемости (late_hours, excused_hours, unexcused_hours)."""
    try:
        cursor = conn.execute(text("PRAGMA table_info(attendance_snapshots)"))
        existing = {row[1] for row in cursor.fetchall()}
        for col in ("late_hours", "excused_hours", "unexcused_hours"):
            if col not in existing:
                conn.execute(text(f"ALTER TABLE attendance_snapshots ADD COLUMN {col} INTEGER DEFAULT 0"))
    except Exception as exc:
        log.debug(f"Миграция колонок attendance_snapshots пропущена: {exc}")


async def init_db() -> None:
    """Создает все необходимые таблицы в SQLite и проводит стартовую миграцию."""
    from db.sqlite.models import Base

    engine = get_database_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_attendance_snapshot_columns)
    log.info("Реляционные схемы SQLite успешно инициализированы")

    async with get_async_session() as session:
        await _migrate_subscribers_from_json(session)
