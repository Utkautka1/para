"""
Репозитории доступа к данным SQLite (SQLAlchemy 2.0).

Реализует CRUD-операции для подписчиков, журналов инцидентов и посещаемости.
Каждый метод строго изолирован и придерживается принципа единственной ответственности.
"""

import json
from collections.abc import Sequence
from datetime import date
from typing import Any

from sqlalchemy import case, delete, func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from core.database import get_async_session
from core.logger import get_logger
from db.sqlite.models import (
    AchievementBaseline,
    AttendanceSnapshot,
    IncidentSeverity,
    StudentAchievement,
    StudentCounter,
    Subscriber,
    SystemIncident,
)

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
            log.info("Подписчик %s успешно сохранен в SQLite", chat_id)
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
            log.info("Подписчик %s деактивирован в SQLite", chat_id)
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
            log.warning("Зафиксирован инцидент [%s] %s: %s", severity, incident_type, title)
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
                        late_hours=int(item.get("late_hours", 0)),
                        excused_hours=int(item.get("excused_hours", 0)),
                        unexcused_hours=int(item.get("unexcused_hours", 0)),
                        percent=float(item.get("percent", 0.0)),
                    )
                )
                count += 1
            log.info("Сохранено %s записей посещаемости за %s", count, snapshot_date)
            return count

    @staticmethod
    async def get_latest_snapshots() -> Sequence[AttendanceSnapshot]:
        """Возвращает последний доступный срез посещаемости всех студентов."""
        async with get_async_session() as session:
            subq = select(func.max(AttendanceSnapshot.snapshot_date)).scalar_subquery()
            stmt = select(AttendanceSnapshot).where(AttendanceSnapshot.snapshot_date == subq)
            result = await session.execute(stmt)
            return result.scalars().all()


class GamificationRepository:
    """Репозиторий прогресса геймификации и открытых достижений студентов."""

    @staticmethod
    async def get_all_unlocked_map() -> dict[str, set[str]]:
        """Возвращает карту открытых достижений по студентам {ФИО: {id_ачивки}}."""
        try:
            async with get_async_session() as session:
                stmt = select(StudentAchievement.student_fio, StudentAchievement.achievement_id)
                rows = (await session.execute(stmt)).all()
                mapping: dict[str, set[str]] = {}
                for fio, aid in rows:
                    mapping.setdefault(fio.lower(), set()).add(aid)
                return mapping
        except Exception as exc:
            log.debug("Таблица достижений еще не создана: %s", exc)
            return {}

    @staticmethod
    async def unlock_achievement(student_fio: str, achievement_id: str) -> bool:
        """Атомарно сохраняет открытое достижение студента в SQLite."""
        try:
            async with get_async_session() as session:
                stmt = select(StudentAchievement).where(
                    StudentAchievement.student_fio == student_fio,
                    StudentAchievement.achievement_id == achievement_id,
                )
                if (await session.execute(stmt)).scalars().first():
                    return False
                session.add(StudentAchievement(student_fio=student_fio, achievement_id=achievement_id))
                return True
        except Exception as exc:
            log.warning("Ошибка разблокировки достижения: %s", exc)
            return False


class CounterRepository:
    """Репозиторий накопительных счётчиков действий студентов."""

    @staticmethod
    async def increment(student_fio: str, key: str, today: date | None = None) -> int:
        """
        Атомарно увеличивает счётчик студента и возвращает новое значение.

        Upsert (INSERT … ON CONFLICT DO UPDATE … RETURNING) вместо select + update:
        два одновременных апдейта от одного студента не потеряют инкремент.
        Если передан today — счётчик растёт не чаще раза в день («активные дни»).

        Возвращает текущее значение счётчика или 0 при ошибке БД.
        """
        bump = StudentCounter.value + 1
        if today is not None:
            bump = case((StudentCounter.last_day == today, StudentCounter.value), else_=bump)
        stmt = sqlite_insert(StudentCounter).values(student_fio=student_fio, key=key, value=1, last_day=today)
        stmt = stmt.on_conflict_do_update(
            index_elements=["student_fio", "key"], set_={"value": bump, "last_day": today}
        ).returning(StudentCounter.value)
        try:
            async with get_async_session() as session:
                return int((await session.execute(stmt)).scalar_one())
        except Exception as exc:
            log.warning("Ошибка инкремента счётчика %s для %s: %s", key, student_fio, exc)
            return 0

    @staticmethod
    async def set_value(student_fio: str, key: str, value: int) -> None:
        """Записывает счётчику точное значение (например, бонус XP, выданный админом)."""
        stmt = sqlite_insert(StudentCounter).values(student_fio=student_fio, key=key, value=value)
        stmt = stmt.on_conflict_do_update(index_elements=["student_fio", "key"], set_={"value": value})
        async with get_async_session() as session:
            await session.execute(stmt)

    @staticmethod
    async def get_key_values(key: str) -> dict[str, int]:
        """
        Возвращает значения одного счётчика у всех студентов {ФИО в нижнем регистре: значение}.

        Пустой словарь при ошибке БД — рейтинг строится и без бонусов.
        """
        try:
            async with get_async_session() as session:
                rows = (await session.execute(select(StudentCounter).where(StudentCounter.key == key))).scalars()
                return {row.student_fio.lower(): row.value for row in rows}
        except Exception as exc:
            log.warning("Ошибка чтения счётчиков %s: %s", key, exc)
            return {}

    @staticmethod
    async def count_keys(student_fio: str, prefix: str) -> int:
        """
        Считает разные счётчики студента с общим префиксом.

        Так хранятся множества: 'hw_kind:photo', 'hw_kind:text' → 2 разных формата.

        Возвращает количество ключей или 0 при ошибке БД.
        """
        stmt = select(func.count()).where(
            StudentCounter.student_fio == student_fio, StudentCounter.key.startswith(prefix)
        )
        try:
            async with get_async_session() as session:
                return int((await session.execute(stmt)).scalar_one())
        except Exception as exc:
            log.warning("Ошибка подсчёта счётчиков %s* для %s: %s", prefix, student_fio, exc)
            return 0


class AchievementResetRepository:
    """Сброс ачивок группы и хранение точки отсчёта журнала."""

    @staticmethod
    async def reset_with_baseline(stats: dict[str, dict[str, Any]]) -> tuple[int, int]:
        """
        В одной транзакции удаляет все ачивки и счётчики и записывает новый снимок журнала.

        Одна транзакция важна: если упадёт запись снимка, ачивки не пропадут,
        иначе worker тут же выдал бы их заново от нулевой точки отсчёта.

        Возвращает (удалено ачивок, удалено счётчиков).
        """
        async with get_async_session() as session:
            achievements = (await session.execute(delete(StudentAchievement))).rowcount or 0
            counters = (await session.execute(delete(StudentCounter))).rowcount or 0
            await session.execute(delete(AchievementBaseline))
            session.add_all(
                AchievementBaseline(student_fio=fio, snapshot=json.dumps(raw, ensure_ascii=False))
                for fio, raw in stats.items()
            )
        return achievements, counters

    @staticmethod
    async def get_baselines() -> dict[str, dict[str, Any]]:
        """
        Возвращает снимки журнала {ФИО: запись журнала} на момент сброса.

        Пустой словарь — сброса не было (или таблицы ещё нет): ачивки считаются от нуля.
        """
        try:
            async with get_async_session() as session:
                rows = (await session.execute(select(AchievementBaseline))).scalars().all()
                return {row.student_fio: json.loads(row.snapshot) for row in rows}
        except Exception as exc:
            log.warning("Не удалось загрузить точку отсчёта ачивок: %s", exc)
            return {}
