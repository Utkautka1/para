"""
Модульные тесты для системы миграций реляционной базы данных Alembic.

Проверяет применимость миграций 'upgrade head' и 'downgrade base'
на изолированной временной базе данных SQLite.
"""

from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import command
from db.sqlite.models import Base


@pytest.fixture
def temp_alembic_cfg(tmp_path: Path) -> Config:
    """Создает изолированную конфигурацию Alembic с временным файлом SQLite."""
    db_file = tmp_path / "test_migration.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


def test_alembic_upgrade_and_downgrade(temp_alembic_cfg: Config) -> None:
    """
    Проверяет сквозное применение всех миграций upgrade head и откат downgrade base.

    Гарантирует отсутствие синтаксических ошибок в DDL и циклических зависимостей.
    """
    command.upgrade(temp_alembic_cfg, "head")
    command.downgrade(temp_alembic_cfg, "base")


@pytest.mark.asyncio
async def test_alembic_tables_match_metadata(temp_alembic_cfg: Config) -> None:
    """
    Проверяет, что после upgrade head созданы все таблицы из Base.metadata.
    """
    command.upgrade(temp_alembic_cfg, "head")
    db_url = temp_alembic_cfg.get_main_option("sqlalchemy.url")
    assert db_url is not None
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        existing_tables = {row[0] for row in res.fetchall()}
    await engine.dispose()

    for table_name in Base.metadata.tables:
        assert table_name in existing_tables, f"Таблица {table_name} не создана миграцией"
