"""
Утилита автоматической синхронизации Cookie Яндекс Документов из Zen Browser.

Скрипт решает проблему истекающих сессий в Yandex Docs:
  1. Извлекает свежие Cookie авторизации (.yandex.ru) из профиля Zen Browser.
  2. Проверяет их валидность прямым HTTP-запросом к документу посещаемости.
  3. Обновляет YANDEX_COOKIE в локальном файле .env.
  4. Передает обновленный заголовок на удаленный сервер через SSH.
  5. Сбрасывает устаревший кэш в Redis и перезапускает сервис воркера.
"""

import base64
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
from pathlib import Path

# Список обязательных Cookie для авторизованного доступа к Яндекс Документам
REQUIRED_COOKIE_NAMES = (
    "Session_id", "sessionid2", "sessar", "_yasc",
    "yandexuid", "i", "yandex_login", "yp", "L"
)
TEST_DOC_URL = "https://disk.yandex.ru/i/uDcaWTFcGbuwZg"


def find_zen_cookies_db() -> Path:
    """
    Находит путь к базе данных cookies.sqlite в профиле Zen Browser.

    Проверяет ~/.config/zen на наличие профилей и выбирает самый свежий.
    Возвращает путь к активному файлу cookies.sqlite.
    """
    zen_dir = Path.home() / ".config" / "zen"
    if not zen_dir.exists():
        raise FileNotFoundError(f"Каталог Zen Browser не найден: {zen_dir}")
    candidates = list(zen_dir.glob("*/cookies.sqlite"))
    if not candidates:
        raise FileNotFoundError("Файл cookies.sqlite не найден в профилях Zen Browser")
    # Выбираем профиль с самым свежим временем модификации базы
    return max(candidates, key=lambda p: p.stat().st_mtime)


def extract_raw_yandex_cookies(db_path: Path) -> dict[str, str]:
    """
    Копирует cookies.sqlite во временный файл и извлекает куки Яндекса.

    Копирование необходимо для обхода файловой блокировки работающего браузера.
    Возвращает словарь имя -> значение для домена yandex.ru.
    """
    tmp_path = Path("/tmp") / f"zen_cookies_{os.getpid()}.sqlite"
    shutil.copy2(db_path, tmp_path)
    try:
        with sqlite3.connect(tmp_path) as conn:
            query = (
                "SELECT name, value FROM moz_cookies "
                "WHERE host LIKE '%yandex.ru%' AND originAttributes = '' "
                "ORDER BY lastAccessed DESC"
            )
            rows = conn.cursor().execute(query).fetchall()
        seen: dict[str, str] = {}
        for name, val in rows:
            if name not in seen:
                seen[name] = val
        return seen
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def build_cookie_header(cookies: dict[str, str]) -> str:
    """
    Собирает заголовок Cookie из извлеченных параметров сессии.

    Проверяет наличие критического Session_id и возвращает единую строку.
    """
    if "Session_id" not in cookies:
        raise ValueError("В профиле Zen Browser отсутствует активная Session_id Яндекса")
    parts = []
    for name in REQUIRED_COOKIE_NAMES:
        if name in cookies:
            parts.append(f"{name}={cookies[name]}")
    return "; ".join(parts)


def verify_yandex_cookie(cookie_hdr: str, test_url: str = TEST_DOC_URL) -> bool:
    """
    Проверяет валидность строки Cookie запросом к документу.

    Проверяет наличие конфигурации client-config в DOM и отсутствие редиректа на логин.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru,en;q=0.9",
        "Cookie": cookie_hdr,
    }
    req = urllib.request.Request(test_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            body = res.read().decode("utf-8", errors="replace")
            return 'id="client-config"' in body and "Авторизация" not in body
    except Exception as exc:
        print(f"Ошибка проверки Cookie в Яндекс Документах: {exc}", file=sys.stderr)
        return False


def update_env_file(env_path: Path, cookie_hdr: str) -> None:
    """
    Атомарно обновляет переменную YANDEX_COOKIE в указанном .env файле.

    Если переменная отсутствует, добавляет её в конец файла.
    """
    if not env_path.exists():
        return
    lines = env_path.read_text(encoding="utf-8").splitlines()
    found = False
    new_lines = []
    for line in lines:
        if line.startswith("YANDEX_COOKIE="):
            new_lines.append(f'YANDEX_COOKIE="{cookie_hdr}"')
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f'YANDEX_COOKIE="{cookie_hdr}"')
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def send_cookie_to_remote_env(cookie_hdr: str, host: str = "home", remote_dir: str = "/root/para") -> None:
    """
    Обновляет YANDEX_COOKIE в файле .env на удаленном сервере по SSH.

    Использует base64 кодирование для исключения конфликтов кавычек в bash.
    """
    b64 = base64.b64encode(cookie_hdr.encode("utf-8")).decode("ascii")
    py = (
        f"import base64, re, os; "
        f"p = '{remote_dir}/.env'; "
        f"c = base64.b64decode('{b64}').decode('utf-8'); "
        f"s = open(p).read() if os.path.exists(p) else ''; "
        f"v = f'YANDEX_COOKIE=\"{{c}}\"\\n'; "
        f"res = re.sub(r'YANDEX_COOKIE=.*\\n', v, s) if 'YANDEX_COOKIE=' in s else s + v; "
        f"open(p, 'w').write(res)"
    )
    subprocess.run(["ssh", host, f"python3 -c \"{py}\""], check=True)


def update_remote_redis_and_restart(cookie_hdr: str, host: str = "home", remote_dir: str = "/root/para") -> None:
    """
    Обновляет сессию в Redis и перезапускает para-worker на сервере.

    Сбрасывает ключ yandex:session_cookie и применяет изменения через docker compose.
    """
    b64 = base64.b64encode(cookie_hdr.encode("utf-8")).decode("ascii")
    py = (
        f"import base64, subprocess; "
        f"c = base64.b64decode('{b64}').decode('utf-8'); "
        f"subprocess.run(['docker', 'exec', 'para-redis', 'redis-cli', 'set', 'yandex:session_cookie', c, 'ex', '604800'], check=True); "
        f"subprocess.run(['docker', 'compose', 'restart', 'worker'], cwd='{remote_dir}', check=True)"
    )
    subprocess.run(["ssh", host, f"python3 -c \"{py}\""], check=True)


def sync_cookies(host: str = "home") -> bool:
    """
    Основной пайплайн синхронизации Cookie из Zen Browser на сервер.

    Координирует поиск, валидацию, локальное и удаленное обновление.
    """
    print("1. Поиск базы данных cookies в профиле Zen Browser...")
    db_path = find_zen_cookies_db()
    raw_cookies = extract_raw_yandex_cookies(db_path)
    cookie_hdr = build_cookie_header(raw_cookies)
    print("2. Проверка валидности Cookie через запрос к Яндекс Документам...")
    if not verify_yandex_cookie(cookie_hdr):
        print("Ошибка: извлеченные Cookie не прошли авторизацию в Яндекс Документах!")
        return False
    print("3. Обновление локального .env...")
    local_env = Path(__file__).resolve().parent.parent / ".env"
    update_env_file(local_env, cookie_hdr)
    print(f"4. Обновление .env на удаленном сервере ({host})...")
    send_cookie_to_remote_env(cookie_hdr, host)
    print("5. Обновление Redis и перезапуск para-worker...")
    update_remote_redis_and_restart(cookie_hdr, host)
    print("Успех: Cookie обновлены, воркер перезапущен и готов к работе!")
    return True


if __name__ == "__main__":
    target_host = sys.argv[1] if len(sys.argv) > 1 else "home"
    is_ok = sync_cookies(target_host)
    sys.exit(0 if is_ok else 1)
