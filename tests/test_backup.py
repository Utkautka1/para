"""
Тесты сервиса автоматического бэкапа и ротации архивов.
"""

import os
import sqlite3
import time
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from services.backup_manager import (
    _backup_sqlite_online,
    _create_tar_archive,
    _rotate_old_backups,
    run_backup_pipeline,
)


def test_sqlite_online_backup(tmp_path: Path) -> None:
    """Проверяет консистентный снимок SQLite базы через Online Backup API."""
    src_db = tmp_path / "source.db"
    dst_db = tmp_path / "dest.db"

    with sqlite3.connect(src_db) as conn:
        conn.execute("CREATE TABLE test_data (id INT, val TEXT);")
        conn.execute("INSERT INTO test_data VALUES (1, 'hello');")
        conn.commit()

    with patch("services.backup_manager.SQLITE_DB_PATH", str(src_db)):
        ok = _backup_sqlite_online(str(dst_db))
        assert ok is True
        assert os.path.exists(dst_db)

        with sqlite3.connect(dst_db) as conn2:
            row = conn2.execute("SELECT val FROM test_data WHERE id=1;").fetchone()
            assert row[0] == "hello"


def test_create_tar_archive_and_rotation(tmp_path: Path) -> None:
    """Проверяет создание архива и ротацию по времени."""
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "dummy.txt").write_text("backup contents")

    archive = tmp_path / "para_backup_old.tar.gz"
    ok = _create_tar_archive(str(staging), str(archive))
    assert ok is True
    assert os.path.exists(archive)

    # Имитируем возраст файла 10 дней
    ten_days_ago = time.time() - (10 * 86400)
    os.utime(archive, (ten_days_ago, ten_days_ago))

    deleted = _rotate_old_backups(str(tmp_path), retention_days=7)
    assert deleted == 1
    assert not os.path.exists(archive)


@pytest.mark.asyncio
async def test_run_backup_pipeline_mocked(tmp_path: Path) -> None:
    """Проверяет полный цикл пайплайна создания бэкапа с отправкой."""
    src_db = tmp_path / "source.db"
    with sqlite3.connect(src_db) as conn:
        conn.execute("CREATE TABLE t (id INT);")

    backup_dir = tmp_path / "backups"

    with (
        patch("services.backup_manager.SQLITE_DB_PATH", str(src_db)),
        patch("services.backup_manager.BACKUP_DIR_PATH", str(backup_dir)),
        patch("services.backup_manager._send_backup_to_telegram", AsyncMock(return_value=True)),
        patch("services.backup_manager.redis_client", None),
    ):
        success = await run_backup_pipeline()
        assert success is True
        archives = [f for f in os.listdir(backup_dir) if f.endswith(".tar.gz")]
        assert len(archives) == 1
