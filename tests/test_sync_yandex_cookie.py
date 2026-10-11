"""
Тесты утилиты синхронизации Cookie Яндекс Документов scripts/sync_yandex_cookie.py.
"""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from scripts.sync_yandex_cookie import (
    build_cookie_header,
    extract_raw_yandex_cookies,
    update_env_file,
    verify_yandex_cookie,
)


def test_build_cookie_header_success():
    """Проверяет корректность сборки Cookie строки при наличии всех ключей."""
    cookies = {
        "Session_id": "3:test_session",
        "sessionid2": "3:test_id2",
        "_yasc": "test_yasc",
        "yandexuid": "123456",
        "other": "ignore_me"
    }
    res = build_cookie_header(cookies)
    assert "Session_id=3:test_session" in res
    assert "sessionid2=3:test_id2" in res
    assert "yandexuid=123456" in res
    assert "other=" not in res


def test_build_cookie_header_missing_session():
    """Проверяет генерацию ошибки при отсутствии Session_id."""
    cookies = {"yandexuid": "123456"}
    with pytest.raises(ValueError, match="отсутствует активная Session_id"):
        build_cookie_header(cookies)


def test_update_env_file_replaces_existing(tmp_path: Path):
    """Проверяет замену существующей переменной YANDEX_COOKIE в .env."""
    env = tmp_path / ".env"
    env.write_text('FOO=bar\nYANDEX_COOKIE="old_val"\nBAZ=qux\n', encoding="utf-8")
    update_env_file(env, "new_cookie=123")
    content = env.read_text(encoding="utf-8")
    assert 'YANDEX_COOKIE="new_cookie=123"' in content
    assert "old_val" not in content


def test_update_env_file_appends_new(tmp_path: Path):
    """Проверяет добавление YANDEX_COOKIE в конец файла, если переменная не найдена."""
    env = tmp_path / ".env"
    env.write_text("FOO=bar\n", encoding="utf-8")
    update_env_file(env, "new_cookie=123")
    content = env.read_text(encoding="utf-8")
    assert 'YANDEX_COOKIE="new_cookie=123"' in content
    assert content.startswith("FOO=bar\n")


def test_verify_yandex_cookie_success():
    """Проверяет успешную валидацию Cookie при наличии client-config в DOM."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'<html><script id="client-config">{}</script></html>'
    mock_resp.__enter__.return_value = mock_resp
    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert verify_yandex_cookie("Session_id=123") is True


def test_verify_yandex_cookie_failure():
    """Проверяет неуспешную валидацию Cookie при редиректе на авторизацию."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = "<html><title>Авторизация</title></html>".encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert verify_yandex_cookie("Session_id=123") is False



def test_extract_raw_yandex_cookies(tmp_path: Path):
    """Проверяет корректное извлечение cookie из временной базы moz_cookies."""
    db_file = tmp_path / "cookies.sqlite"
    with sqlite3.connect(db_file) as conn:
        conn.execute(
            "CREATE TABLE moz_cookies (name TEXT, value TEXT, host TEXT, originAttributes TEXT, lastAccessed INTEGER)"
        )
        conn.execute(
            "INSERT INTO moz_cookies VALUES ('Session_id', 'sess_val', '.yandex.ru', '', 100)"
        )
        conn.execute(
            "INSERT INTO moz_cookies VALUES ('other', 'other_val', '.google.com', '', 100)"
        )
    extracted = extract_raw_yandex_cookies(db_file)
    assert extracted.get("Session_id") == "sess_val"
    assert "other" not in extracted
