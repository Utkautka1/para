"""
Модуль парсинга API расписания КТМУ с расчетом звонков по четности недели.

Определяет точное время звонков с учетом измененных расписаний (dayPeriodTimesByParity),
вычисляет дату, предмет, тип пары (Лек/Пр), адреса корпусов и кэширует данные.
"""

import asyncio
import json
import re
import time
from datetime import date, timedelta
from typing import Any

import httpx

from config import (
    CAMPUS_ADDRESS_REMOTE,
    CAMPUS_ADDRESS_TSVETOCHNAYA,
    CAMPUS_ADDRESS_VOZNESENSKY,
    GROUP_ID,
    HTTP_CLIENT_TIMEOUT_SECONDS,
    HTTP_POOL_MAX_CONNECTIONS,
    HTTP_POOL_MAX_KEEPALIVE_CONNECTIONS,
    SCHEDULE_API_URL,
    SCHEDULE_CACHE_TTL_SECONDS,
    SCHEDULE_COOLDOWN_SECONDS,
    SCHEDULE_FALLBACK_API_URL,
)
from core.logger import get_logger
from integrations.docx_parser import TeacherData, get_teacher_links
from services.models import Lesson

log = get_logger("schedule_parser")

_DATA_CACHE: tuple[float, dict[str, Any] | None] = (0.0, None)
_LAST_PUBLISHED_AT: str | None = None
_RESOLVED_DAY_CACHE: dict[date, list[Lesson]] = {}


def clear_resolved_day_cache() -> None:
    """
    Сбрасывает оперативный L1 in-memory кэш предрассчитанных занятий.

    Вызывается при обновлении расписания из API или получении новых ссылок
    на преподавателей, гарантируя инвалидацию закэшированных моделей Lesson.

    Ничего не возвращает.
    """
    _RESOLVED_DAY_CACHE.clear()


def resolve_room_address(room_name: str, is_remote: bool) -> str:
    """
    Определяет физический адрес учебного корпуса по номеру аудитории.

    Распознает маркер дистанционного формата и префикс 'В-' (Вознесенский проспект),
    по умолчанию относя все остальные кабинеты к корпусу на Цветочной улице.

    Возвращает строку с адресом или отметку 'Дистанционно'.
    """
    if is_remote:
        return CAMPUS_ADDRESS_REMOTE

    if room_name.lower().startswith("в-"):
        return CAMPUS_ADDRESS_VOZNESENSKY

    return CAMPUS_ADDRESS_TSVETOCHNAYA


def extract_zoom_creds(text: str) -> tuple[str | None, str | None, str | None]:
    """
    Извлекает URL подключения, Meeting ID и пароль конференции из текста преподавателя.

    Использует регулярные выражения для поиска ссылок на Zoom/Телемост/Teams
    и числовых кодов доступа, нормализуя пробелы и протоколы.

    Возвращает кортеж (url, meeting_id, passcode).
    """
    if not text:
        return None, None, None

    clean_text = re.sub(r"https?\s+://|http\s+s://", "https://", text, flags=re.IGNORECASE)
    url_m = re.search(r"https?://[^\s<>\"\'\`]+", clean_text)
    id_m = re.search(r"(?:Идентификатор(?:\s+конференции)?|Meeting\s+ID)[:\s]+([0-9\s]{8,15})", text, re.IGNORECASE)
    pass_m = re.search(r"(?:Код(?:\s+доступа)?|Passcode)[:\s]+([A-Za-z0-9]+)", text, re.IGNORECASE)

    url = url_m.group(0) if url_m else None
    mid = id_m.group(1).strip() if id_m else None
    code = pass_m.group(1).strip() if pass_m else None

    return url, mid, code


def clean_subject_title(subject: str) -> str:
    """
    Устраняет дублирование наименований учебных дисциплин.

    Обрабатывает распространенный артефакт выгрузки 1С/КТМУ со слэшем ('Мат / Математика'),
    выбирая более полное и точное наименование.

    Возвращает очищенное строковое название дисциплины.
    """
    parts = [p.strip() for p in subject.split("/") if p.strip()]

    if len(parts) == 2 and parts[0].lower() in parts[1].lower():
        return parts[1]

    return subject


def calculate_week_number(target_date: date, semester_start_str: str) -> int:
    """
    Рассчитывает порядковый номер учебной недели относительно даты старта семестра.

    Привязывает отсчет к понедельнику первой недели семестра, возвращая 1
    для дат, предшествующих началу учебного периода.

    Возвращает целочисленный номер недели (начиная с 1).
    """
    start_date = date.fromisoformat(semester_start_str)
    start_monday = start_date - timedelta(days=start_date.weekday())
    days_diff = (target_date - start_monday).days

    if days_diff < 0:
        return 1

    return (days_diff // 7) + 1


def is_instance_active_for_week(inst: dict[str, Any], week_num: int) -> bool:
    """
    Проверяет актуальность занятия для конкретного номера учебной недели.

    Интерпретирует шаблоны 'all' (еженедельно), 'even' (четная), 'odd' (нечетная)
    и 'custom' с явным перечислением недель проведения в customWeeks.

    Возвращает True, если пара проводится на указанной неделе, иначе False.
    """
    pattern = inst.get("weekPattern", "all")

    if pattern == "custom":
        return week_num in inst.get("customWeeks", [])

    if pattern == "even":
        return week_num % 2 == 0

    if pattern == "odd":
        return week_num % 2 == 1

    return True


def is_item_for_group(item: dict[str, Any], group_id: str) -> bool:
    """
    Проверяет принадлежность занятия или нагрузки к целевой академической группе.

    Учитывает как прямую принадлежность groupId/groupIds, так и участие группы
    в межгрупповых потоках (streamGroupIds, streamParticipants).

    Возвращает True, если занятие адресовано группе, иначе False.
    """
    if not isinstance(item, dict):
        return False

    if item.get("groupId") == group_id or group_id in item.get("groupIds", []):
        return True

    if group_id in item.get("streamGroupIds", []):
        return True

    participants = item.get("streamParticipants", [])
    return any(p.get("groupId") == group_id for p in participants if isinstance(p, dict))


def is_stream_lesson(inst: dict[str, Any]) -> bool:
    """
    Определяет, является ли занятие потоковой лекцией для нескольких групп.

    Анализирует наличие списка streamGroupIds, участников потока и идентификатора streamId
    для корректного бейджа в расписании.

    Возвращает True для потоковых пар, иначе False.
    """
    if not isinstance(inst, dict):
        return False

    if len(inst.get("streamGroupIds", [])) > 0:
        return True

    if len(inst.get("streamParticipants", [])) > 0:
        return True

    return bool(inst.get("streamId"))


def extract_subgroup(inst: dict[str, Any], group_id: str) -> int:
    """
    Извлекает номер подгруппы целевой группы с учетом потокового участия.

    Проверяет локальный атрибут subgroup инстанса либо ищет запись группы
    в массиве streamParticipants.

    Возвращает номер подгруппы (0 - вся группа, 1 или 2 - подгруппа).
    """
    if not isinstance(inst, dict):
        return 0

    if inst.get("groupId") == group_id:
        return int(inst.get("subgroup", 0) or 0)

    for sp in inst.get("streamParticipants", []):
        if isinstance(sp, dict) and sp.get("groupId") == group_id:
            return int(sp.get("subgroup", 0) or 0)

    return int(inst.get("subgroup", 0) or 0)


def _lookup_period_time(times_list: list[str], period_idx: int) -> str | None:
    """
    Безопасно извлекает временной интервал пары по индексу периода.

    Проверяет границы массива и наличие непустого строкового значения.

    Возвращает строку времени ('09:00 - 10:30') или None.
    """
    if period_idx < len(times_list) and times_list[period_idx]:
        return times_list[period_idx]

    return None


def _find_group_period_time(group_data: dict[str, Any], day_idx: int, period_idx: int, parity: str) -> str | None:
    """
    Ищет звонки пары в расписании группы по четности или обычному дню.

    Возвращает строку времени или None.
    """
    p_map = group_data.get("dayPeriodTimesByParity", {}).get(parity, {}).get(str(day_idx), [])
    return _lookup_period_time(p_map, period_idx) or _lookup_period_time(
        group_data.get("dayPeriodTimes", {}).get(str(day_idx), []), period_idx
    )


def get_period_time_str(
    group_data: dict[str, Any],
    day_idx: int,
    period_idx: int,
    week_num: int,
    global_config: dict[str, Any] | None = None,
) -> str:
    """
    Определяет точный временной интервал пары с учетом четности недели и дня.

    Использует каскадный поиск звонков: расписание группы, затем глобальный конфиг.

    Возвращает строку звонков пары (например, '10:45 - 12:15').
    """
    parity = "even" if week_num % 2 == 0 else "odd"
    res = _find_group_period_time(group_data, day_idx, period_idx, parity)

    if res:
        return res

    if global_config and (g_res := _lookup_period_time(global_config.get("periodTimes", []), period_idx)):
        return g_res

    return "Время уточняется"


_HTTP_CLIENT: httpx.AsyncClient | None = None
_LAST_ETAG: str | None = None
_LAST_MODIFIED: str | None = None
_COOLDOWN_UNTIL: float = 0.0
_COOLDOWN_SECONDS: float = float(SCHEDULE_COOLDOWN_SECONDS)


def _create_http_client() -> httpx.AsyncClient:
    """
    Создает новый настроенный экземпляр HTTP-клиента с пулом соединений.

    Конфигурирует User-Agent браузера, Keep-Alive лимиты и тайм-ауты сети.

    Возвращает экземпляр httpx.AsyncClient.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    limits = httpx.Limits(
        max_keepalive_connections=HTTP_POOL_MAX_KEEPALIVE_CONNECTIONS,
        max_connections=HTTP_POOL_MAX_CONNECTIONS,
        keepalive_expiry=60.0,
    )
    timeout = httpx.Timeout(
        HTTP_CLIENT_TIMEOUT_SECONDS,
        connect=10.0,
        read=HTTP_CLIENT_TIMEOUT_SECONDS,
    )

    return httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True, limits=limits)


def get_http_client() -> httpx.AsyncClient:
    """
    Предоставляет общий синглтон HTTP-клиента с пулом постоянных соединений.

    Защищает от исчерпания сокетов ОС, переиспользуя активный клиент.

    Возвращает настроенный экземпляр httpx.AsyncClient.
    """
    global _HTTP_CLIENT

    if _HTTP_CLIENT is None or _HTTP_CLIENT.is_closed:
        _HTTP_CLIENT = _create_http_client()

    return _HTTP_CLIENT


def update_cache_headers(headers: httpx.Headers) -> None:
    """
    Сохраняет заголовки HTTP ETag и Last-Modified из ответа сервера КТМУ.

    Используется для последующих условных GET-запросов (If-None-Match),
    позволяя экономить трафик и мгновенно получать HTTP 304 Not Modified.

    Ничего не возвращает.
    """
    global _LAST_ETAG, _LAST_MODIFIED

    if "etag" in headers:
        _LAST_ETAG = headers["etag"]

    if "last-modified" in headers:
        _LAST_MODIFIED = headers["last-modified"]


def _filter_group_schedule(sched: dict[str, Any]) -> tuple[list, dict]:
    """
    Фильтрует инстансы и назначения для целевой академической группы.

    Возвращает кортеж (group_instances, group_assignments).
    """
    group_insts = [i for i in sched.get("instances", []) if is_item_for_group(i, GROUP_ID)]
    group_ids = {i["instId"] for i in group_insts if "instId" in i}
    group_assigns = {k: v for k, v in sched.get("assignment", {}).items() if k in group_ids}

    return group_insts, group_assigns


def filter_snapshot_for_target_group(snapshot: dict[str, Any]) -> dict[str, Any]:
    """
    Очищает объемный 50 МБ снимок всего колледжа, оставляя только данные 1-КПД-3.

    Фильтрует занятия, связки аудиторий и экзаменационные нагрузки группы,
    сокращая объем занимаемой оперативной памяти на 95%.

    Возвращает компактный словарь среза данных расписания группы.
    """
    group_insts, group_assigns = _filter_group_schedule(snapshot.get("schedule", {}))
    group_loads = [l for l in snapshot.get("loads", []) if is_item_for_group(l, GROUP_ID)]

    return {
        "config": snapshot.get("config", {}),
        "publishedAt": snapshot.get("publishedAt"),
        "subjects": snapshot.get("subjects", []),
        "teachers": snapshot.get("teachers", []),
        "rooms": snapshot.get("rooms", []),
        "groups": snapshot.get("groups", []),
        "lessonTypes": snapshot.get("lessonTypes", []),
        "loads": group_loads,
        "schedule": {"instances": group_insts, "assignment": group_assigns},
    }


def _parse_and_clean_payload(content: bytes) -> tuple[str | None, dict[str, Any]]:
    """
    Синхронно парсит сырой бинарный JSON API и фильтрует целевую группу.

    Запускается в asyncio.to_thread для изоляции десериализации 50 МБ данных
    от основного цикла событий веб-сервера.

    Возвращает кортеж (published_at, cleaned_snapshot).
    """
    val = json.loads(content).get("value", {})
    snapshot = val.get("publishedSnapshot") or val
    pub_at = snapshot.get("publishedAt")
    cleaned = filter_snapshot_for_target_group(snapshot)

    return pub_at, cleaned


def _persist_snapshot_to_redis(snapshot: dict[str, Any]) -> None:
    """
    Сохраняет нормализованный снимок расписания и HTTP-заголовки в Redis.

    Запускается как detached asyncio.create_task без блокировки отдачи ответа клиенту.

    Ничего не возвращает.
    """
    from core.redis_cache import save_schedule_snapshot

    meta = {
        "etag": _LAST_ETAG,
        "last_modified": _LAST_MODIFIED,
        "published_at": _LAST_PUBLISHED_AT,
    }
    asyncio.create_task(save_schedule_snapshot(snapshot, meta))


def _handle_non_200_status(status_code: int, now: float) -> tuple[float, dict[str, Any] | None]:
    """
    Определяет статус кулдауна и кэша при кодах ответов API отличных от HTTP 200.

    При HTTP 304 сбрасывает кулдаун и подтверждает валидность текущего кэша,
    при других кодах активирует 5-минутный защитный кулдаун.

    Возвращает кортеж (new_cooldown_until, cache_data).
    """
    if status_code == 304:
        return 0.0, _DATA_CACHE[1]

    log.error(f"Ошибка API КТМУ: HTTP {status_code} (кулдаун 5 мин)")
    return now + _COOLDOWN_SECONDS, _DATA_CACHE[1]


def _apply_new_snapshot(pub_at: str | None, cleaned: dict[str, Any], now: float) -> None:
    """
    Применяет обновленный снимок расписания, сбрасывая кэш и сохраняя в Redis.

    Ничего не возвращает.
    """
    global _DATA_CACHE, _LAST_PUBLISHED_AT, _COOLDOWN_UNTIL

    if pub_at and pub_at != _LAST_PUBLISHED_AT:
        log.info(f"Обнаружена новая публикация расписания КТМУ от: {pub_at}")
        _LAST_PUBLISHED_AT = pub_at

    _DATA_CACHE, _COOLDOWN_UNTIL = (now, cleaned), 0.0
    clear_resolved_day_cache()
    _persist_snapshot_to_redis(cleaned)


async def process_api_response(res: httpx.Response, now: float) -> dict[str, Any] | None:
    """
    Обрабатывает HTTP-ответ от сервера расписания КТМУ.

    Обновляет кэш-заголовки, десериализует полезную нагрузку и инвалидирует L1-кэш
    при обнаружении более свежей даты публикации расписания.

    Возвращает отфильтрованный срез расписания или текущий кэш при ошибке.
    """
    global _DATA_CACHE, _COOLDOWN_UNTIL

    if res.status_code != 200:
        _COOLDOWN_UNTIL, data = _handle_non_200_status(res.status_code, now)
        _DATA_CACHE = (now, data)
        return data

    update_cache_headers(res.headers)
    pub_at, cleaned = await asyncio.to_thread(_parse_and_clean_payload, res.content)
    _apply_new_snapshot(pub_at, cleaned, now)

    return cleaned


_IS_REFRESHING: bool = False


def _build_cache_headers() -> dict[str, str]:
    """
    Формирует заголовки условного HTTP-запроса If-None-Match и If-Modified-Since.

    Используется для минимизации трафика и мгновенного подтверждения неизменности данных.

    Возвращает словарь HTTP-заголовков.
    """
    headers: dict[str, str] = {}

    if _LAST_ETAG:
        headers["If-None-Match"] = _LAST_ETAG

    if _LAST_MODIFIED:
        headers["If-Modified-Since"] = _LAST_MODIFIED

    return headers


async def _fetch_single_endpoint(url: str, headers: dict[str, str]) -> httpx.Response:
    """
    Выполняет HTTP GET запрос к конкретному URL расписания с коротким таймаутом.

    Позволяет быстро обнаружить сетевую недоступность и переключиться на резерв.

    Возвращает объект httpx.Response.
    """
    return await get_http_client().get(url, headers=headers, timeout=10.0)


async def _try_fetch_endpoint(url: str, idx: int, headers: dict[str, str]) -> httpx.Response | None:
    """
    Пытается выполнить запрос к конкретному эндпоинту расписания.

    Обрабатывает коды 200/304 и логирует переключение на резервный URL.

    Возвращает Response при успехе, иначе None при невалидном HTTP-коде.
    """
    res = await _fetch_single_endpoint(url, headers)

    if res.status_code in (200, 304):
        if idx > 0:
            log.info(f"Основной API недоступен, данные получены из запасного API: {url}")
        return res

    log.warning(f"Эндпоинт {url} вернул статус {res.status_code}, переключаемся...")
    return None


async def _fetch_remote_schedule() -> httpx.Response:
    """
    Запрашивает расписание из основного API с авто-переходом на резервный URL.

    Опрашивает эндпоинты по цепочке, гарантируя отказоустойчивость при сетевых сбоях.

    Возвращает HTTP-ответ с кодом 200 или 304.
    """
    headers = _build_cache_headers()
    endpoints = [u for u in (SCHEDULE_API_URL, SCHEDULE_FALLBACK_API_URL) if u]
    last_exc: Exception | None = None

    for idx, url in enumerate(endpoints):
        try:
            res = await _try_fetch_endpoint(url, idx, headers)
            if res is not None:
                return res
        except Exception as e:
            last_exc = e
            log.warning(f"Сбой подключения к эндпоинту расписания ({url}): {e}")

    if last_exc:
        raise last_exc

    raise RuntimeError("Все доступные эндпоинты расписания КТМУ недоступны")


async def refresh_schedule_in_background(force: bool = False) -> None:
    """
    Асинхронно опрашивает API расписания в фоновом режиме с защитой от спама.

    При сетевых сбоях устанавливает 5-минутный кулдаун _COOLDOWN_UNTIL,
    предотвращая лавину запросов при недоступности внешнего сервиса.

    Ничего не возвращает.
    """
    global _IS_REFRESHING, _COOLDOWN_UNTIL

    now = time.time()
    if _IS_REFRESHING or (now < _COOLDOWN_UNTIL and not force):
        return

    _IS_REFRESHING = True
    try:
        res = await _fetch_remote_schedule()
        await process_api_response(res, now)
    except Exception as e:
        _COOLDOWN_UNTIL = now + _COOLDOWN_SECONDS
        err_msg = repr(e) if str(e) == "" else f"{type(e).__name__}: {e}"
        log.warning(f"Фоновое обновление API КТМУ не удалось ({err_msg}). Используется кэш (кулдаун 5 мин).")
    finally:
        _IS_REFRESHING = False


async def init_schedule_cache_from_redis(now: float) -> bool:
    """
    Восстанавливает снимок расписания и ETag из Redis при холодном старте сервиса.

    Позволяет контейнерам para-api и para-bot мгновенно отвечать на запросы
    пользователей сразу после старта без ожидания сетевого ответа от КТМУ.

    Возвращает True в случае успешной загрузки из Redis, иначе False.
    """
    global _DATA_CACHE, _LAST_ETAG, _LAST_MODIFIED, _LAST_PUBLISHED_AT

    from core.redis_cache import load_schedule_snapshot

    snap, meta = await load_schedule_snapshot()
    if snap and meta:
        _DATA_CACHE = (now, snap)
        _LAST_ETAG = meta.get("etag")
        _LAST_MODIFIED = meta.get("last_modified")
        _LAST_PUBLISHED_AT = meta.get("published_at")
        clear_resolved_day_cache()
        log.info("Кэш расписания успешно восстановлен из Redis (мгновенный cold-start)")
        return True

    return False


async def _trigger_stale_refresh(now: float) -> None:
    """
    Запускает фоновое обновление расписания при истечении кулдауна.

    Предотвращает лавину сетевых запросов при сбоях внешнего сервиса КТМУ.

    Ничего не возвращает.
    """
    if now >= _COOLDOWN_UNTIL:
        asyncio.create_task(refresh_schedule_in_background())


async def _get_cached_or_revalidate(now: float) -> dict[str, Any] | None:
    """
    Возвращает кэшированный снимок расписания, запуская фоновое обновление при устаревании.

    Возвращает снимок данных расписания либо None.
    """
    if _DATA_CACHE[1] is None and await init_schedule_cache_from_redis(now):
        await _trigger_stale_refresh(now)
        return _DATA_CACHE[1]

    if _DATA_CACHE[1] is not None:
        if now - _DATA_CACHE[0] >= SCHEDULE_CACHE_TTL_SECONDS:
            await _trigger_stale_refresh(now)
        return _DATA_CACHE[1]

    return None


async def fetch_schedule_data(force_refresh: bool = False) -> dict[str, Any] | None:
    """
    Предоставляет актуальный снимок расписания из памяти, Redis или внешнего API.

    Реализует паттерн Stale-While-Revalidate с защитой от блокировки клиента.

    Возвращает очищенный словарь среза расписания группы или None при ошибке.
    """
    now = time.time()

    if force_refresh:
        await refresh_schedule_in_background(force=True)
        if _DATA_CACHE[1] is None:
            await init_schedule_cache_from_redis(now)
        return _DATA_CACHE[1]

    cached = await _get_cached_or_revalidate(now)
    if cached is not None:
        return cached

    await refresh_schedule_in_background()
    return _DATA_CACHE[1]


def extract_entity_maps(data: dict[str, Any]) -> tuple[dict, dict, dict, dict, dict]:
    """
    Формирует быстрые O(1) словари соответствия сущностей по их ID.

    Строит таблицы трансляции для предметов, преподавателей, аудиторий,
    группы 1-КПД-3 и типов занятий.

    Возвращает кортеж (subjs, teachs, rms, group_data, l_types).
    """
    subjs = {s["id"]: s.get("name", "") for s in data.get("subjects", []) if isinstance(s, dict)}
    teachs = {t["id"]: t.get("name", "") for t in data.get("teachers", []) if isinstance(t, dict)}
    rms = {r["id"]: r.get("name", "") for r in data.get("rooms", []) if isinstance(r, dict)}
    groups = {g["id"]: g for g in data.get("groups", []) if isinstance(g, dict)}
    l_types = {l["id"]: l.get("name", "") for l in data.get("lessonTypes", []) if isinstance(l, dict)}

    return (subjs, teachs, rms, groups.get(GROUP_ID, {}), l_types)


def _handle_missing_remote_teacher(raw_teacher: str, subj_name: str) -> None:
    """
    Инициирует фоновое оповещение старосты об отсутствующей ссылке преподавателя.

    Ничего не возвращает.
    """
    from services.notifier import notify_missing_teacher

    asyncio.create_task(notify_missing_teacher(raw_teacher, subj_name))


def _extract_existing_teacher_creds(
    t_info: TeacherData, raw_teacher: str, is_remote: bool
) -> tuple[str, str | None, str | None, str | None]:
    """
    Извлекает ФИО и доступы к Zoom/Телемост для найденного в реестре преподавателя.

    Возвращает кортеж (ФИО, url, meeting_id, passcode).
    """
    name = t_info.get("full_name") or raw_teacher
    creds = extract_zoom_creds(t_info["link_info"]) if (is_remote and t_info.get("link_info")) else (None, None, None)
    return (name, *creds)


def resolve_teacher_contact_info(
    raw_teacher: str,
    teacher_data_map: dict[str, TeacherData],
    is_remote: bool,
    subj_name: str,
) -> tuple[str, str | None, str | None, str | None]:
    """
    Сопоставляет преподавателя с реестром ссылок и извлекает Zoom/Телемост доступы.

    При отсутствии ссылки на дистант отправляет фоновое уведомление старосте.

    Возвращает кортеж (полное_ФИО, url_ссылки, meeting_id, passcode).
    """
    if not raw_teacher:
        return "Преподаватель", None, None, None

    last_name = raw_teacher.split()[0].lower()
    t_info = teacher_data_map.get(last_name)
    if t_info:
        return _extract_existing_teacher_creds(t_info, raw_teacher, is_remote)

    if is_remote:
        _handle_missing_remote_teacher(raw_teacher, subj_name)

    return raw_teacher, None, None, None


def resolve_room_name(asgn: dict[str, Any], inst: dict[str, Any], rms: dict[str, str], is_remote: bool) -> str:
    """
    Определяет текстовый номер аудитории или маркер дистанта.

    Использует фактическое назначение roomId, либо предпочитаемый кабинет инстанса.

    Возвращает строковый номер кабинета или 'Дистанционно'.
    """
    if is_remote:
        return "Дистанционно"

    room_id = asgn.get("roomId") or (inst.get("preferredRoomIds") or [""])[0]
    return rms.get(room_id, room_id)


def _resolve_lesson_meta(
    inst: dict[str, Any],
    asgn: dict[str, Any],
    maps: tuple[dict, dict, dict, dict, dict],
    teacher_map: dict[str, TeacherData],
):
    """
    Определяет формат, аудиторию, адрес и контакты преподавателя для занятия.

    Возвращает кортеж метаданных занятия.
    """
    subjs, teachs, rms, _, _ = maps
    is_remote = inst.get("format") == "remote"
    r_name = resolve_room_name(asgn, inst, rms, is_remote)
    subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Занятие"))
    t_name, link, mid, passc = resolve_teacher_contact_info(
        teachs.get(inst.get("teacherId"), ""), teacher_map, is_remote, subj_name
    )
    return is_remote, r_name, subj_name, t_name, link, mid, passc


def _build_lesson_payload(
    inst: dict[str, Any],
    asgn: dict[str, Any],
    maps: tuple[dict, dict, dict, dict, dict],
    day_idx: int,
    week_num: int,
    teacher_map: dict[str, TeacherData],
    cfg: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Формирует словарь полей для валидации и создания Pydantic-модели Lesson.

    Возвращает словарь аргументов модели Lesson.
    """
    _, _, _, group_data, l_types = maps
    period = asgn.get("period", 0)
    time_str = get_period_time_str(group_data, day_idx, period, week_num, cfg)
    is_rem, r_name, subj, t_name, link, mid, passc = _resolve_lesson_meta(inst, asgn, maps, teacher_map)

    return {
        "period": period,
        "time_str": time_str,
        "subject": subj,
        "lesson_type": l_types.get(inst.get("typeId"), "") or "Пара",
        "teacher": t_name,
        "is_remote": is_rem,
        "room": r_name,
        "address": resolve_room_address(r_name, is_rem),
        "subgroup": extract_subgroup(inst, GROUP_ID),
        "is_stream": is_stream_lesson(inst),
        "remote_link": link,
        "remote_passcode": passc,
        "remote_meeting_id": mid,
    }


def build_lesson_object(
    inst: dict[str, Any],
    asgn: dict[str, Any],
    maps: tuple[dict, dict, dict, dict, dict],
    day_idx: int,
    week_num: int,
    teacher_map: dict[str, TeacherData],
    cfg: dict[str, Any] | None = None,
) -> Lesson:
    """
    Конструирует объект Lesson с точным расписанием звонков, адресом и ссылками.

    Возвращает валидированный экземпляр Pydantic-модели Lesson.
    """
    payload = _build_lesson_payload(inst, asgn, maps, day_idx, week_num, teacher_map, cfg)
    return Lesson(**payload)


def is_placed_lesson_active(inst: dict[str, Any], asgn: dict[str, Any] | None, day_idx: int, week_num: int) -> bool:
    """
    Проверяет, размещено ли занятие в сетке расписания на указанный день и неделю.

    Сопоставляет день недели в сетке и активность недели проведения пары.

    Возвращает True, если занятие назначено, иначе False.
    """
    if not asgn:
        return False

    return asgn.get("day") == day_idx and is_instance_active_for_week(inst, week_num)


def _collect_day_instances(
    insts: list[dict[str, Any]],
    asgns: dict[str, Any],
    maps: tuple[dict, dict, dict, dict, dict],
    day_idx: int,
    week_num: int,
    links: dict[str, TeacherData],
    cfg: dict[str, Any] | None,
) -> list[Lesson]:
    """
    Фильтрует и конструирует объекты Lesson для активных занятий академической группы.

    Возвращает список занятий Lesson.
    """
    lessons: list[Lesson] = []

    for inst in insts:
        if not is_item_for_group(inst, GROUP_ID):
            continue
        asgn = asgns.get(inst.get("instId", ""))
        if is_placed_lesson_active(inst, asgn, day_idx, week_num):
            lessons.append(build_lesson_object(inst, asgn, maps, day_idx, week_num, links, cfg))

    return lessons


def _extract_lessons_for_day(
    data: dict[str, Any],
    day_idx: int,
    week_num: int,
    links: dict[str, TeacherData],
) -> list[Lesson]:
    """
    Извлекает и упорядочивает список занятий для группы на указанный день недели.

    Фильтрует пары по дню и неделе, сопоставляет преподавателей и сортирует по периодам.

    Возвращает упорядоченный список объектов Lesson.
    """
    sched = data.get("schedule", {})
    insts = sched.get("instances", [])
    asgns = sched.get("assignment", {})
    maps = extract_entity_maps(data)
    cfg = data.get("config", {})

    lessons = _collect_day_instances(insts, asgns, maps, day_idx, week_num, links, cfg)
    lessons.sort(key=lambda x: x.period)

    return lessons


async def get_schedule_for_date(target_date: date, force_refresh: bool = False) -> list[Lesson]:
    """
    Формирует список занятий группы на целевую дату с двухуровневым кэшированием L1/L2.

    При попадании в L1 оперативный кэш возвращает готовые модели Lesson мгновенно,
    при промахе производит расчет относительно даты старта семестра.

    Возвращает отсортированный по времени список занятий Lesson на выбранный день.
    """
    if not force_refresh and target_date in _RESOLVED_DAY_CACHE:
        return _RESOLVED_DAY_CACHE[target_date]

    data = await fetch_schedule_data(force_refresh=force_refresh)
    if not data:
        return []

    sem_start = data.get("config", {}).get("semesterStart", "2026-09-01")
    week_num = calculate_week_number(target_date, sem_start)
    day_idx = target_date.weekday()

    links = await get_teacher_links(force_refresh=False)
    lessons = _extract_lessons_for_day(data, day_idx, week_num, links)

    _RESOLVED_DAY_CACHE[target_date] = lessons
    return lessons


async def get_week_schedule(monday_date: date, force_refresh: bool = False) -> list[tuple[date, list[Lesson]]]:
    """
    Формирует структурированное расписание на всю учебную неделю (пн-сб).

    Последовательно запрашивает расписание на 6 дней недели от переданного понедельника,
    сохраняя кэш каждого дня для мгновенного последующего доступа.

    Возвращает список кортежей вида [(дата, [Lesson, ...]), ...].
    """
    if force_refresh:
        clear_resolved_day_cache()
        await fetch_schedule_data(force_refresh=True)

    result: list[tuple[date, list[Lesson]]] = []
    for i in range(6):
        day_date = monday_date + timedelta(days=i)
        lessons = await get_schedule_for_date(day_date, force_refresh=False)
        result.append((day_date, lessons))

    return result
