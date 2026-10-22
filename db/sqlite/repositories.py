"""
Репозитории доступа к данным SQLite (SQLAlchemy 2.0).

Реализует CRUD-операции для подписчиков, журналов инцидентов и посещаемости.
Каждый метод строго изолирован и придерживается принципа единственной ответственности.
"""

from collections.abc import Sequence
from datetime import date
from typing import Any

from sqlalchemy import func, select

from core.database import get_async_session
from core.logger import get_logger
from db.sqlite.models import AttendanceSnapshot, IncidentSeverity, Subscriber, SystemIncident

log = get_logger("repositories")


class SubscriberRepository:
    """Репозиторий управления списком подписчиков в SQLite."""

    @staticmethod
    async def get_active_chat_ids() -> set[int]:
        """Возвращает множество активных chat_id подписчиков."""
        async with get_async_session() as session:
            stmt = select(Subscriber.chat_id).where(Subscriber.is_active.is_(True))
            result = await session.execute(stmt)
            return set(result.scalars().all())

    @staticmethod
    async def add_subscriber(chat_id: int, username: str | None = None, full_name: str | None = None) -> bool:
        """Добавляет нового подписчика или реактивирует существующего."""
        async with get_async_session() as session:
            stmt = select(Subscriber).where(Subscriber.chat_id == chat_id)
            sub = (await session.execute(stmt)).scalars().first()
            if sub and sub.is_active:
                return False
            if sub:
                sub.is_active = True
                sub.username = username or sub.username
                sub.full_name = full_name or sub.full_name
            else:
                session.add(Subscriber(chat_id=chat_id, username=username, full_name=full_name, is_active=True))
            log.info(f"Подписчик {chat_id} успешно сохранен в SQLite")
            return True

    @staticmethod
    async def remove_subscriber(chat_id: int) -> bool:
        """Деактивирует подписчика в базе данных."""
        async with get_async_session() as session:
            stmt = select(Subscriber).where(Subscriber.chat_id == chat_id, Subscriber.is_active.is_(True))
            sub = (await session.execute(stmt)).scalars().first()
            if not sub:
                return False
            sub.is_active = False
            log.info(f"Подписчик {chat_id} деактивирован в SQLite")
            return True

    @staticmethod
    async def count_active() -> int:
        """Возвращает общее количество активных подписчиков."""
        async with get_async_session() as session:
            stmt = select(func.count(Subscriber.id)).where(Subscriber.is_active.is_(True))
            return (await session.execute(stmt)).scalar() or 0


class IncidentRepository:
    """Репозиторий журнала сбоев, сетевых аномалий и алертов."""

    @staticmethod
    async def record_incident(
        incident_type: str,
        title: str,
        description: str,
        severity: str = IncidentSeverity.WARNING,
        trace_id: str | None = None,
    ) -> SystemIncident:
        """Фиксирует новый системный инцидент в реляционной базе данных."""
        async with get_async_session() as session:
            incident = SystemIncident(
                incident_type=incident_type,
                severity=severity,
                title=title,
                description=description,
                trace_id=trace_id,
            )
            session.add(incident)
            await session.flush()
            log.warning(f"Зафиксирован инцидент [{severity}] {incident_type}: {title}")
            return incident

    @staticmethod
    async def get_recent_incidents(limit: int = 50, unresolved_only: bool = False) -> Sequence[SystemIncident]:
        """Возвращает список недавних системных инцидентов."""
        async with get_async_session() as session:
            stmt = select(SystemIncident).order_by(SystemIncident.created_at.desc()).limit(limit)
            if unresolved_only:
                stmt = stmt.where(SystemIncident.resolved.is_(False))
            return (await session.execute(stmt)).scalars().all()


class AttendanceRepository:
    """Репозиторий исторических снимков посещаемости студентов."""

    @staticmethod
    async def save_daily_snapshots(snapshot_date: date, records: list[dict[str, Any]]) -> int:
        """Сохраняет срез посещаемости студентов за указанную дату."""
        async with get_async_session() as session:
            count = 0
            for item in records:
                name = item.get("name") or item.get("student_name")
                if not name:
                    continue
                session.add(
                    AttendanceSnapshot(
                        snapshot_date=snapshot_date,
                        student_name=str(name),
                        total_hours=int(item.get("total_hours", 0)),
                        attended_hours=int(item.get("attended_hours", 0)),
                        percent=float(item.get("percent", 0.0)),
                    )
                )
                count += 1
            log.info(f"Сохранено {count} записей посещаемости за {snapshot_date}")
            return count

    @staticmethod
    async def get_latest_snapshots() -> Sequence[AttendanceSnapshot]:
        """Возвращает последний доступный срез посещаемости всех студентов."""
        async with get_async_session() as session:
            subq = select(func.max(AttendanceSnapshot.snapshot_date)).scalar_subquery()
            stmt = select(AttendanceSnapshot).where(AttendanceSnapshot.snapshot_date == subq)
            result = await session.execute(stmt)
            return result.scalars().all()
