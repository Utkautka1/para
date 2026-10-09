"""
Тесты утилиты синхронизации HTTPS-туннеля scripts/tunnel_sync.py.
"""

from pathlib import Path

from scripts.tunnel_sync import parse_tunnel_url, update_env_miniapp_url


def test_parse_tunnel_url() -> None:
    line = "Your quick Tunnel has been created! Visit it at: https://sample-tunnel.trycloudflare.com"
    url = parse_tunnel_url(line)
    assert url == "https://sample-tunnel.trycloudflare.com"


def test_parse_tunnel_url_no_match() -> None:
    line = "Starting cloudflared agent connecting to edges..."
    assert parse_tunnel_url(line) is None


def test_update_env_miniapp_url(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("API_BASE_URL=http://api:8000\nMINIAPP_URL=https://old.com\nSWAGGER_URL=https://old.com/docs\n", encoding="utf-8")
    monkeypatch.setattr("scripts.tunnel_sync.ENV_FILE", env_file)

    ok = update_env_miniapp_url("https://sample-tunnel.trycloudflare.com")
    assert ok is True
    content = env_file.read_text(encoding="utf-8")
    assert "MINIAPP_URL=https://sample-tunnel.trycloudflare.com/miniapp" in content
    assert "SWAGGER_URL=https://sample-tunnel.trycloudflare.com/docs" in content
