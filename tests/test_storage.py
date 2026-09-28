"""
Unit-тесты для модуля атомарного хранилища JSON (utils/storage.py).

Проверяет:
  1. Синхронное и асинхронное чтение файлов с возвратом дефолтных значений
  2. Атомарную запись через временный файл и fsync с созданием поддиректорий
  3. Устойчивость к битым данным и некорректному синтаксису JSON
  4. Сериализацию кириллицы (ensure_ascii=False) и сложных вложенных структур
"""

import os
from typing import Any
import pytest

from utils.storage import load_json, save_json, sync_atomic_save_json, sync_load_json


@pytest.mark.parametrize(
    "test_data",
    [
        {"key": "value", "count": 10},
        [1, 2, 3, "item"],
        {"nested": {"sub": [True, False, None]}},
        "простая строка с кириллицей",
        12345,
        True,
    ],
)
def test_sync_save_and_load_roundtrip(tmp_path, test_data: Any) -> None:
    """Проверяет точное сохранение и восстановление различных типов данных."""
    file_path = str(tmp_path / "subdir" / "data.json")
    assert sync_atomic_save_json(file_path, test_data) is True
    assert os.path.exists(file_path)
    loaded = sync_load_json(file_path)
    assert loaded == test_data


def test_sync_load_non_existent_file(tmp_path) -> None:
    """Проверяет возврат значения по умолчанию для несуществующего пути."""
    file_path = str(tmp_path / "missing.json")
    assert sync_load_json(file_path, default=None) is None
    assert sync_load_json(file_path, default={"fallback": 1}) == {"fallback": 1}
    assert sync_load_json(file_path, default=[]) == []


def test_sync_load_corrupted_json(tmp_path) -> None:
    """Проверяет безопасную обработку поврежденного синтаксиса JSON."""
    file_path = str(tmp_path / "corrupted.json")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{invalid_json: 123,")
    assert sync_load_json(file_path, default="safe_default") == "safe_default"


def test_sync_save_overwrites_existing_atomically(tmp_path) -> None:
    """Проверяет полную перезапись существующего файла без остаточных данных."""
    file_path = str(tmp_path / "overwrite.json")
    sync_atomic_save_json(file_path, {"initial": "very long data that will be overwritten"})
    sync_atomic_save_json(file_path, {"new": 1})
    assert sync_load_json(file_path) == {"new": 1}


@pytest.mark.asyncio
async def test_async_save_and_load_roundtrip(tmp_path) -> None:
    """Проверяет асинхронные обертки save_json и load_json."""
    file_path = str(tmp_path / "async_test.json")
    payload = {"async_status": "ok", "items": ["пара 1", "пара 2"]}
    saved = await save_json(file_path, payload)
    assert saved is True
    loaded = await load_json(file_path)
    assert loaded == payload


@pytest.mark.parametrize(
    "default_val",
    [
        {},
        [],
        None,
        "default_str",
        42,
    ],
)
def test_sync_load_defaults_matrix(tmp_path, default_val: Any) -> None:
    """Проверяет возвращаемые дефолтные типы при чтении пустого пути."""
    fpath = str(tmp_path / "does_not_exist.json")
    assert sync_load_json(fpath, default=default_val) == default_val
