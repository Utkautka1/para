"""
Синхронизатор Cloudflare Tunnel (trycloudflare.com) для Telegram Mini App Swagger UI.

Зачем существует этот модуль:
Сервер para развёрнут на хосте за NAT без белого IP.
Telegram Mini App и удаленные тестировщики требуют защищенный публичный HTTPS-эндпоинт.
Модуль запускает официальный cloudflared туннель через глобальную сеть Cloudflare,
автоматически обновляет MINIAPP_URL и SWAGGER_URL в .env и перезапускает бота.
"""

import asyncio
import re
import shutil
import subprocess  # nosec B404
from pathlib import Path

TARGET_PORT = 8080
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")


def parse_tunnel_url(line: str) -> str | None:
    """Извлекает HTTPS-ссылку Cloudflare из строки вывода cloudflared."""
    match = URL_REGEX.search(line)
    return match.group(0) if match else None


def update_env_urls(new_url: str) -> bool:
    """Обновляет значения MINIAPP_URL и SWAGGER_URL в файле .env."""
    if not ENV_FILE.exists():
        return False
    content = ENV_FILE.read_text(encoding="utf-8")
    miniapp_ep = f"{new_url.rstrip('/')}/miniapp"
    swagger_ep = f"{new_url.rstrip('/')}/docs"
    content = re.sub(r"MINIAPP_URL=.*", f"MINIAPP_URL={miniapp_ep}", content)
    content = re.sub(r"SWAGGER_URL=.*", f"SWAGGER_URL={swagger_ep}", content)
    ENV_FILE.write_text(content, encoding="utf-8")
    return True


update_env_miniapp_url = update_env_urls


def restart_bot_service() -> None:
    """Перезапускает контейнер para-bot с перечитыванием обновленного .env."""
    cmd = ["docker", "compose", "up", "-d", "bot"]
    subprocess.run(cmd, cwd=ENV_FILE.parent, check=False)  # nosec B603


async def monitor_tunnel_stream(proc: asyncio.subprocess.Process) -> None:
    """Слушает лог cloudflared и применяет новый HTTPS URL при подключении."""
    last_url = None
    while proc.returncode is None:
        line_bytes = await proc.stderr.readline()
        if not line_bytes:
            break
        line = line_bytes.decode(errors="ignore")
        found_url = parse_tunnel_url(line)
        if found_url and found_url != last_url:
            last_url = found_url
            print(f"[CLOUDFLARE] Активен HTTPS туннель: {found_url}", flush=True)
            if update_env_urls(found_url):
                print(f"[CLOUDFLARE] Обновлены MINIAPP_URL и SWAGGER_URL в .env", flush=True)
                restart_bot_service()
                print("[CLOUDFLARE] para-bot успешно перезапущен!", flush=True)


async def run_tunnel_process() -> None:
    """Запускает официальный клиент Cloudflare Quick Tunnel."""
    bin_path = shutil.which("cloudflared") or "/usr/local/bin/cloudflared"
    cmd = [bin_path, "tunnel", "--url", f"http://127.0.0.1:{TARGET_PORT}", "--no-autoupdate"]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    await monitor_tunnel_stream(proc)
    await proc.wait()


async def main() -> None:
    """Бесконечный цикл синхронизации Cloudflare Tunnel с авто-восстановлением."""
    print("🚀 Запуск службы Cloudflare Tunnel для Swagger UI и Mini App", flush=True)
    while True:
        try:
            await run_tunnel_process()
        except (OSError, asyncio.SubprocessError) as exc:
            print(f"[CLOUDFLARE] Ошибка процесса: {exc}", flush=True)
        print("[CLOUDFLARE] Переподключение через 5 секунд...", flush=True)
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
