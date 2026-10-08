"""
Синхронизатор HTTPS-туннеля localhost.run для Telegram Mini App Swagger UI.

Зачем существует этот модуль:
Сервер para развёрнут на хосте с динамическим IP за NAT.
Telegram Mini App строго требует публичный HTTPS-эндпоинт.
Модуль запускает SSH-туннель к localhost.run, извлекает выделенный HTTPS URL,
автоматически обновляет MINIAPP_URL в .env и перезапускает para-bot.
"""

import asyncio
import re
import subprocess
from pathlib import Path

TUNNEL_HOST = "nokey@localhost.run"
TARGET_PORT = 8080
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.lhr\.life")


def parse_tunnel_url(line: str) -> str | None:
    """Извлекает HTTPS-ссылку туннеля из строки лога."""
    match = URL_REGEX.search(line)
    return match.group(0) if match else None


def update_env_miniapp_url(new_url: str) -> bool:
    """Обновляет значение MINIAPP_URL в файле .env."""
    if not ENV_FILE.exists():
        return False
    content = ENV_FILE.read_text(encoding="utf-8")
    miniapp_endpoint = f"{new_url.rstrip('/')}/miniapp"
    if "MINIAPP_URL=" in content:
        updated = re.sub(r"MINIAPP_URL=.*", f"MINIAPP_URL={miniapp_endpoint}", content)
    else:
        updated = f"{content.rstrip()}\nMINIAPP_URL={miniapp_endpoint}\n"
    ENV_FILE.write_text(updated, encoding="utf-8")
    return True


def restart_bot_service() -> None:
    """Перезапускает контейнер para-bot для применения нового MINIAPP_URL."""
    cmd = ["docker", "compose", "restart", "bot"]
    subprocess.run(cmd, cwd=ENV_FILE.parent, check=False)  # nosec B603


async def monitor_tunnel_stream(proc: asyncio.subprocess.Process) -> None:
    """Слушает вывод SSH-процесса и реагирует на появление нового HTTPS URL."""
    last_url = None
    while proc.returncode is None:
        line_bytes = await proc.stdout.readline()
        if not line_bytes:
            break
        line = line_bytes.decode(errors="ignore")
        found_url = parse_tunnel_url(line)
        if found_url and found_url != last_url:
            last_url = found_url
            print(f"[TUNNEL] Обнаружен активный URL: {found_url}", flush=True)
            if update_env_miniapp_url(found_url):
                print(f"[TUNNEL] Обновлен .env: MINIAPP_URL={found_url}/miniapp", flush=True)
                restart_bot_service()
                print("[TUNNEL] para-bot успешно перезапущен с новым URL!", flush=True)


async def run_tunnel_process() -> None:
    """Запускает и удерживает SSH-процесс туннеля localhost.run."""
    cmd = [
        "ssh",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=3",
        "-o", "StrictHostKeyChecking=no",
        "-R", f"80:127.0.0.1:{TARGET_PORT}",
        TUNNEL_HOST,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    await monitor_tunnel_stream(proc)
    await proc.wait()


async def main() -> None:
    """Основной бесконечный цикл с авто-восстановлением соединения."""
    print("🚀 Запуск службы синхронизации HTTPS-туннеля для Swagger Mini App", flush=True)
    while True:
        try:
            await run_tunnel_process()
        except (OSError, asyncio.SubprocessError) as exc:
            print(f"[TUNNEL] Ошибка процесса туннеля: {exc}", flush=True)
        print("[TUNNEL] Переподключение через 5 секунд...", flush=True)
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
