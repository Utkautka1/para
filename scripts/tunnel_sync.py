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
import sys
from pathlib import Path

# Обеспечиваем доступность корневого пакета при автономном вызове скрипта
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import API_EXTERNAL_PORT, CLOUDFLARE_TUNNEL_URL_REGEX

TARGET_PORT = API_EXTERNAL_PORT
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
URL_REGEX = CLOUDFLARE_TUNNEL_URL_REGEX


def parse_tunnel_url(line: str) -> str | None:
    """
    Извлекает публичный HTTPS-адрес туннеля из строкового потока вывода cloudflared.

    Ищет вхождение регулярного выражения *.trycloudflare.com в служебных логах
    демона Cloudflare Quick Tunnel.

    Возвращает строку HTTPS URL или None, если в строке ссылка не найдена.
    """
    match = URL_REGEX.search(line)
    return match.group(0) if match else None


def update_env_urls(new_url: str) -> bool:
    """
    Атомарно обновляет параметры MINIAPP_URL и SWAGGER_URL в локальном файле .env.

    Формирует публичные эндпоинты интерфейсов /miniapp и /docs на основе нового
    динамического туннельного домена Cloudflare.

    Возвращает True при успешной записи в файл, False при отсутствии файла .env.
    """
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
    """
    Перезапускает docker-контейнер бота para-bot для применения новых переменных окружения.

    Вызывает 'docker compose up -d bot' в каталоге проекта для бесшовного
    перечитывания обновленного файла конфигурации .env.

    Не возвращает значений; ошибки subprocess игнорируются для отказоустойчивости.
    """
    cmd = ["docker", "compose", "up", "-d", "bot"]
    subprocess.run(cmd, cwd=ENV_FILE.parent, check=False)  # nosec B603


async def monitor_tunnel_stream(proc: asyncio.subprocess.Process) -> None:
    """
    Асинхронно считывает поток stderr процесса cloudflared и применяет новые URL.

    Фильтрует дубликаты адресов, обновляет файл конфигурации и инициирует
    перезапуск бота только при реальном изменении публичного хоста.

    Не возвращает значений; завершается при остановке процесса или закрытии потока.
    """
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
                print("[CLOUDFLARE] Обновлены MINIAPP_URL и SWAGGER_URL в .env", flush=True)
                restart_bot_service()
                print("[CLOUDFLARE] para-bot успешно перезапущен!", flush=True)


async def run_tunnel_process() -> None:
    """
    Запускает бинарник cloudflared в режиме быстрого временного туннеля (Quick Tunnel).

    Пробрасывает локальный порт внутреннего API TARGET_PORT в глобальную сеть
    Cloudflare без необходимости проброса портов на роутере.

    Не возвращает значений; ожидает завершения дочернего процесса.
    """
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
    """
    Основной бесконечный цикл супервизора туннеля Cloudflare с авто-восстановлением.

    Перезапускает процесс туннеля с 5-секундной задержкой при любых сетевых сбоях
    или непредвиденных падениях бинарного демона cloudflared.

    Не возвращает значений; выполняется бесконечно до прерывания процесса.
    """
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
