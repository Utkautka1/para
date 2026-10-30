"""
Утилита автоматической синхронизации Cookie Яндекс Документов из Zen Browser.

Скрипт решает проблему истекающих сессий в Yandex Docs:
  1. Извлекает свежие Cookie авторизации (.yandex.ru) из профиля Zen Browser.
  2. Продлевает сессию через сервис обновления Яндекс Паспорта.
  3. Проверяет валидность прямым HTTP-запросом к документу посещаемости.
  4. Обновляет YANDEX_COOKIE и API URLs в локальном и удаленном файлах .env.
  5. Сбрасывает устаревший кэш в Redis и перезапускает сервисы.
"""

import base64
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# Обеспечиваем доступность корневого пакета при автономном вызове скрипта
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    REDIS_COOKIE_TTL_SECONDS,
    REDIS_YANDEX_COOKIE_KEY,
    SAFE_HOST_REGEX,
    SAFE_PATH_REGEX,
    YANDEX_COOKIE_TEST_DOC_URL,
    YANDEX_REQUIRED_COOKIE_NAMES,
)

REQUIRED_COOKIE_NAMES = YANDEX_REQUIRED_COOKIE_NAMES
TEST_DOC_URL = YANDEX_COOKIE_TEST_DOC_URL


def _validate_ssh_target(host: str, remote_dir: str) -> None:
    """
    Проверяет безопасность целевого SSH-хоста и пути на сервере.

    Защищает от инъекций шелл-команд через непроверенные аргументы командной строки.
    Использует строгие regex-паттерны разрешенных символов.

    Выбрасывает ValueError, если параметры содержат запрещенные символы.
    """
    if not SAFE_HOST_REGEX.match(host):
        raise ValueError(f"Недопустимое имя SSH хоста: {host}")
    if not SAFE_PATH_REGEX.match(remote_dir):
        raise ValueError(f"Недопустимый путь удаленной директории: {remote_dir}")


def get_target_doc_url() -> str:
    """
    Получает целевой URL таблицы посещаемости из боевой конфигурации.

    Использует ATTENDANCE_DOC_URL из config.py с отказоустойчивым переключением
    на тестовый URL документа при отсутствии значения.

    Возвращает строку с полным URL таблицы посещаемости.
    """
    try:
        from config import ATTENDANCE_DOC_URL

        return ATTENDANCE_DOC_URL or TEST_DOC_URL
    except Exception:
        return TEST_DOC_URL


def find_zen_cookies_db() -> Path:
    """
    Определяет путь к активной базе данных cookies.sqlite браузера Zen.

    Сканирует все профили в каталоге ~/.config/zen и выбирает файл с самой
    последней датой модификации для работы с активной сессией.

    Возвращает Path к найденному cookies.sqlite или выбрасывает FileNotFoundError.
    """
    zen_dir = Path.home() / ".config" / "zen"
    if not zen_dir.exists():
        raise FileNotFoundError(f"Каталог Zen Browser не найден: {zen_dir}")
    candidates = list(zen_dir.glob("*/cookies.sqlite"))
    if not candidates:
        raise FileNotFoundError("Файл cookies.sqlite не найден в профилях Zen Browser")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def extract_raw_yandex_cookies(db_path: Path) -> dict[str, str]:
    """
    Извлекает куки авторизации Яндекс из базы данных профиля браузера.

    Создает временную копию SQLite базы во избежание конфликтов блокировки (database locked)
    с запущенным процессом браузера, после чего читает куки домена .yandex.ru.

    Возвращает словарь {имя_куки: значение} с актуальными токенами.
    """
    import tempfile

    tmp_path = Path(tempfile.gettempdir()) / f"zen_cookies_{os.getpid()}.sqlite"  # nosec B108
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


def refresh_yandex_session(cookies: dict[str, str], target_url: str) -> dict[str, str]:
    """
    Продлевает срок жизни сессии Яндекс через эндпоинт обновления Паспорта.

    Отправляет запрос на passport.yandex.ru/auth/update без следования редиректам,
    перехватывая свежие Set-Cookie (Session_id, sessar) из заголовков ответа.

    Возвращает дополненный словарь cookies с обновленными токенами сессии.
    """
    encoded_url = urllib.parse.quote(target_url, safe="")
    passport_url = (
        f"https://passport.yandex.ru/auth/update/?from=cloud&origin=disk_client_web_signin_ru&retpath={encoded_url}"
    )
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
    req = urllib.request.Request(passport_url, headers={"User-Agent": "Mozilla/5.0", "Cookie": cookie_str})

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    try:
        urllib.request.build_opener(NoRedirect).open(req, timeout=10)
    except urllib.error.HTTPError as exc:
        for sc in exc.headers.get_all("Set-Cookie") or []:
            part = sc.split(";")[0]
            if "=" in part:
                k, v = part.split("=", 1)
                cookies[k] = v
    return cookies


def build_cookie_header(cookies: dict[str, str]) -> str:
    """
    Формирует строку HTTP-заголовка Cookie из словаря параметров сессии.

    Проверяет наличие обязательного Session_id и включает только необходимые
    параметры из YANDEX_REQUIRED_COOKIE_NAMES для минимизации размера заголовка.

    Возвращает готовую строку формата 'name=value; name2=value2'.
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
    Проверяет валидность сгенерированного Cookie-заголовка прямым HTTP-запросом.

    Запрашивает HTML документа Яндекс и проверяет наличие блока client-config,
    убеждаясь, что сессия не перенаправлена на форму входа Яндекс ID.

    Возвращает True, если авторизация успешна, иначе False.
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
    Обновляет переменную YANDEX_COOKIE в локальном файле переменных окружения.

    Ищет существующую запись YANDEX_COOKIE или добавляет новую в конец файла,
    сохраняя все остальные переменные и комментарии без искажения.

    Не возвращает значений; перезаписывает целевой .env файл в UTF-8.
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
    Передает и обновляет YANDEX_COOKIE в файле .env на удаленном сервере через SSH.

    Кодирует значение в Base64 для безопасной передачи без проблем с экранированием
    кавычек и спецсимволов в shell-команде.

    Не возвращает значений; выбрасывает CalledProcessError при сбое SSH.
    """
    _validate_ssh_target(host, remote_dir)
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
    subprocess.run(["ssh", host, "python3 -"], input=py.encode("utf-8"), check=True)


def _build_env_update_script(remote_dir: str, b64_payload: str) -> str:
    """Генерирует безопасную команду python с base64-скриптом обновления .env файла."""
    script = (
        "import json, base64, os\n"
        f"p = '{remote_dir}/.env'\n"
        f"u = json.loads(base64.b64decode('{b64_payload}').decode('utf-8'))\n"
        "lines = open(p, encoding='utf-8').read().splitlines() if os.path.exists(p) else []\n"
        "seen = set()\n"
        "out = []\n"
        "for l in lines:\n"
        "    if '=' in l and not l.strip().startswith('#'):\n"
        "        k = l.split('=', 1)[0].strip()\n"
        "        if k in u:\n"
        '            out.append(f"{k}={u[k]}")\n'
        "            seen.add(k)\n"
        "            continue\n"
        "    out.append(l)\n"
        "for k, v in u.items():\n"
        "    if k not in seen:\n"
        '        out.append(f"{k}={v}")\n'
        "open(p, 'w', encoding='utf-8').write(chr(10).join(out) + chr(10))\n"
    )
    return script


def send_api_urls_to_remote_env(
    primary_url: str = "https://raspisanie-ktmu.ru/api/storage/schedule-data-v2",
    fallback_url: str = "https://nikkhl0358-max-time-f5e2.twc1.net/api/storage/schedule-data-v2",
    host: str = "home",
    remote_dir: str = "/root/para",
) -> None:
    """Синхронизирует основной и резервный URL-адреса API расписания на сервере."""
    _validate_ssh_target(host, remote_dir)
    updates = {
        "SCHEDULE_API_URL": primary_url,
        "SCHEDULE_FALLBACK_API_URL": fallback_url,
        "DEFAULT_FALLBACK_SCHEDULE_API_URL": fallback_url,
        "EXAM_SCHEDULE_API_URL": primary_url,
        "EXAM_SCHEDULE_FALLBACK_API_URL": fallback_url,
    }
    b64 = base64.b64encode(json.dumps(updates).encode("utf-8")).decode("ascii")
    py = _build_env_update_script(remote_dir, b64)
    subprocess.run(["ssh", host, "python3 -"], input=py.encode("utf-8"), check=True)


def update_remote_redis_and_restart(cookie_hdr: str, host: str = "home", remote_dir: str = "/root/para") -> None:
    """
    Записывает актуальные Cookie в Redis на сервере и перезапускает сервисы.

    Устанавливает сессию с TTL в REDIS_YANDEX_COOKIE_KEY и перезапускает контейнеры
    para-worker и para-bot для применения свежих учетных данных без даунтайма.

    Не возвращает значений; выбрасывает CalledProcessError при сбое Docker.
    """
    _validate_ssh_target(host, remote_dir)
    b64 = base64.b64encode(cookie_hdr.encode("utf-8")).decode("ascii")
    py = (
        f"import base64, subprocess; "
        f"c = base64.b64decode('{b64}').decode('utf-8'); "
        f"subprocess.run(['docker', 'exec', 'para-redis', 'redis-cli', 'set', '{REDIS_YANDEX_COOKIE_KEY}', c, 'ex', '{REDIS_COOKIE_TTL_SECONDS}'], check=True); "
        f"subprocess.run(['docker', 'compose', 'up', '-d', 'worker', 'bot'], cwd='{remote_dir}', check=True)"
    )
    # Скрипт идёт через stdin, а не `python3 -c "..."`: удалённый shell не разбирает
    # содержимое, и кавычки в путях или ключах не могут сломать/подменить команду
    subprocess.run(["ssh", host, "python3 -"], input=py.encode("utf-8"), check=True)


def sync_cookies(host: str = "home") -> bool:
    """
    Выполняет полный цикл синхронизации учетных данных Яндекса из браузера на сервер.

    Координирует извлечение, обновление, валидацию и распространение cookie в локальное
    окружение и на удаленный хост инфраструктуры проекта.

    Возвращает True в случае успешной синхронизации, False при ошибке проверки.
    """
    print("1. Поиск базы данных cookies в профиле Zen Browser...")
    db_path = find_zen_cookies_db()
    raw_cookies = extract_raw_yandex_cookies(db_path)
    target_url = get_target_doc_url()
    print("2. Продление сессии через Яндекс Паспорт...")
    refreshed_cookies = refresh_yandex_session(raw_cookies, target_url)
    cookie_hdr = build_cookie_header(refreshed_cookies)
    print("3. Проверка валидности Cookie через запрос к Яндекс Документам...")
    if not verify_yandex_cookie(cookie_hdr, target_url):
        print("Ошибка: извлеченные Cookie не прошли авторизацию в Яндекс Документах!")
        return False
    print("4. Обновление локального .env...")
    update_env_file(Path(__file__).resolve().parent.parent / ".env", cookie_hdr)
    print(f"5. Обновление .env на удаленном сервере ({host})...")
    send_cookie_to_remote_env(cookie_hdr, host)
    send_api_urls_to_remote_env(host=host)
    print("6. Обновление Redis и перезапуск сервисов...")
    update_remote_redis_and_restart(cookie_hdr, host)
    print("Успех: Cookie и API URLs обновлены, сервисы перезапущены!")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("Использование: python scripts/sync_yandex_cookie.py [SSH_HOST]")
        print("По умолчанию SSH_HOST = 'home'")
        sys.exit(0)
    target_host = sys.argv[1] if len(sys.argv) > 1 else "home"
    is_ok = sync_cookies(target_host)
    sys.exit(0 if is_ok else 1)
