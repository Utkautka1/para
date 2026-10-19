"""
Модели реляционной базы данных SQLite (SQLAlchemy 2.0).

Определяет Mapped-модели постоянного хранения:
  1. Subscriber — персистентный реестр Telegram-подписчиков бота
  2. AttendanceSnapshot — история посещаемости студентов для аналитики
  3. SystemIncident — журнал критических сбоев, алертов и состояний Circuit Breaker
"""

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех реляционных моделей проекта."""



class IncidentSeverity(StrEnum):
    """Уровни критичности инцидентов системы."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Subscriber(Base):
    """Таблица активных подписчиков утренней рассылки и уведомлений."""

    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class AttendanceSnapshot(Base):
    """Таблица исторических снимков посещаемости студентов из Яндекс Документов."""

    __tablename__ = "attendance_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    student_name: Mapped[str] = mapped_column(String(128), index=True)
    total_hours: Mapped[int] = mapped_column(Integer)
    attended_hours: Mapped[int] = mapped_column(Integer)
    percent: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SystemIncident(Base):
    """Таблица журнала системных сбоев, сетевых аномалий и срабатываний защиты."""

    __tablename__ = "system_incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(32), default=IncidentSeverity.WARNING)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

