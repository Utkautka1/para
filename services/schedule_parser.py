"""
Модуль парсинга API расписания КТМУ с расчетом звонков по четности недели.

Определяет точное время звонков с учетом измененных расписаний (dayPeriodTimesByParity),
вычисляет дату, предмет, тип пары (Лек/Пр), адреса корпусов и кэширует данные.
"""

import asyncio
import json
import re
import time
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import httpx
from pydantic import BaseModel

from config import GROUP_ID, SCHEDULE_API_URL, SCHEDULE_CACHE_TTL_SECONDS
from core.logger import get_logger
from services.docx_parser import TeacherData, get_teacher_links
from services.models import Lesson

log = get_logger("schedule_parser")

_DATA_CACHE: Tuple[float, Optional[Dict[str, Any]]] = (0.0, None)
_LAST_PUBLISHED_AT: Optional[str] = None



def resolve_room_address(room_name: str, is_remote: bool) -> str:
    """
    Определяет адрес корпуса КТМУ по номеру кабинета.

    :param room_name: Кабинет
    :param is_remote: Флаг дистанта
    :return: Адрес корпуса
    """
    if is_remote:
        return "Дистанционно"
    if room_name.lower().startswith("в-"):
        return "Вознесенский пр., 44"
    return "ул. Цветочная, д. 8"


def extract_zoom_creds(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Извлекает URL, ID конференции и пароль Zoom/Телемоста.

    :param text: Текст из таблицы преподавателя
    :return: Кортеж (url, meeting_id, passcode)
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
    Очищает дублирующиеся названия предметов.

    :param subject: Название предмета
    :return: Чистое название
    """
    parts = [p.strip() for p in subject.split("/") if p.strip()]
    if len(parts) == 2 and parts[0].lower() in parts[1].lower():
        return parts[1]
    return subject


def calculate_week_number(target_date: date, semester_start_str: str) -> int:
    """
    Вычисляет порядковый номер учебной недели.

    :param target_date: Целевая дата
    :param semester_start_str: Старт семестра
    :return: Номер недели
    """
    start_date = datetime.strptime(semester_start_str, "%Y-%m-%d").date()
    start_monday = start_date - timedelta(days=start_date.weekday())
    days_diff = (target_date - start_monday).days
    if days_diff < 0:
        return 1
    return (days_diff // 7) + 1


def is_instance_active_for_week(inst: Dict[str, Any], week_num: int) -> bool:
    """
    Проверяет проведение пары на неделе.

    :param inst: Занятие
    :param week_num: Номер недели
    :return: True, если проводится
    """
    pattern = inst.get("weekPattern", "all")
    if pattern == "custom":
        return week_num in inst.get("customWeeks", [])
    if pattern == "even":
        return week_num % 2 == 0
    if pattern == "odd":
        return week_num % 2 == 1
    return True


def is_item_for_group(item: Dict[str, Any], group_id: str) -> bool:
    """
    Проверяет принадлежность занятия или нагрузки к целевой группе, включая потоки.

    :param item: Словарь занятия или нагрузки
    :param group_id: ID целевой группы
    :return: True если занятие предназначено для группы
    """
    if not isinstance(item, dict):
        return False
    if item.get("groupId") == group_id or group_id in item.get("groupIds", []):
        return True
    if group_id in item.get("streamGroupIds", []):
        return True
    participants = item.get("streamParticipants", [])
    return any(p.get("groupId") == group_id for p in participants if isinstance(p, dict))


def is_stream_lesson(inst: Dict[str, Any]) -> bool:
    """
    Определяет, является ли занятие потоковым (объединяет несколько групп).

    :param inst: Экземпляр занятия
    :return: True если пара потоковая
    """
    if not isinstance(inst, dict):
        return False
    if len(inst.get("streamGroupIds", [])) > 0:
        return True
    if len(inst.get("streamParticipants", [])) > 0:
        return True
    return bool(inst.get("streamId"))


def extract_subgroup(inst: Dict[str, Any], group_id: str) -> int:
    """
    Извлекает номер подгруппы для целевой группы с учетом участия в потоке.

    :param inst: Экземпляр занятия
    :param group_id: ID целевой группы
    :return: Номер подгруппы (0 если общая)
    """
    if not isinstance(inst, dict):
        return 0
    if inst.get("groupId") == group_id:
        return int(inst.get("subgroup", 0) or 0)
    for sp in inst.get("streamParticipants", []):
        if isinstance(sp, dict) and sp.get("groupId") == group_id:
            return int(sp.get("subgroup", 0) or 0)
    return int(inst.get("subgroup", 0) or 0)


def _lookup_period_time(times_list: List[str], period_idx: int) -> Optional[str]:
    """Извлекает время пары по индексу, если оно задано в списке звонков."""
    if period_idx < len(times_list) and times_list[period_idx]:
        return times_list[period_idx]
    return None


def get_period_time_str(
    group_data: Dict[str, Any],
    day_idx: int,
    period_idx: int,
    week_num: int,
    global_config: Optional[Dict[str, Any]] = None
) -> str:
    """Определяет интервал времени пары строго из API КТМУ."""
    parity = "even" if week_num % 2 == 0 else "odd"
    by_parity = group_data.get("dayPeriodTimesByParity", {}).get(parity, {}).get(str(day_idx), [])
    res = _lookup_period_time(by_parity, period_idx) or _lookup_period_time(
        group_data.get("dayPeriodTimes", {}).get(str(day_idx), []), period_idx
    )
    if res:
        return res
    if global_config:
        res = _lookup_period_time(global_config.get("periodTimes", []), period_idx)
        if res:
            return res
    return "Время уточняется"


_HTTP_CLIENT: Optional[httpx.AsyncClient] = None
_LAST_ETAG: Optional[str] = None
_LAST_MODIFIED: Optional[str] = None
_COOLDOWN_UNTIL: float = 0.0
_COOLDOWN_SECONDS: float = 300.0


def get_http_client() -> httpx.AsyncClient:
    """Возвращает персистентный HTTP клиент с пулом соединений и увеличенным таймаутом."""
    global _HTTP_CLIENT
    if _HTTP_CLIENT is None or _HTTP_CLIENT.is_closed:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10, keepalive_expiry=60.0)
        timeout = httpx.Timeout(60.0, connect=10.0, read=60.0)
        _HTTP_CLIENT = httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True, limits=limits)
    return _HTTP_CLIENT


def update_cache_headers(headers: httpx.Headers) -> None:
    """
    Обновляет локальные ETag и Last-Modified заголовки.
    """
    global _LAST_ETAG, _LAST_MODIFIED
    if "etag" in headers:
        _LAST_ETAG = headers["etag"]
    if "last-modified" in headers:
        _LAST_MODIFIED = headers["last-modified"]


def filter_snapshot_for_target_group(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Очищает сырой 40 МБ JSON от чужих групп с сохранением потоковых пар."""
    sched = snapshot.get("schedule", {})
    group_insts = [i for i in sched.get("instances", []) if is_item_for_group(i, GROUP_ID)]
    group_ids = set(i["instId"] for i in group_insts if "instId" in i)
    group_assigns = {k: v for k, v in sched.get("assignment", {}).items() if k in group_ids}

    # loads — нагрузки (аттестации/экзамены), сохраняем с учетом потоков
    group_loads = [l for l in snapshot.get("loads", []) if is_item_for_group(l, GROUP_ID)]

    return {
        "config": snapshot.get("config", {}), "publishedAt": snapshot.get("publishedAt"),
        "subjects": snapshot.get("subjects", []), "teachers": snapshot.get("teachers", []),
        "rooms": snapshot.get("rooms", []), "groups": snapshot.get("groups", []),
        "lessonTypes": snapshot.get("lessonTypes", []),
        "loads": group_loads,
        "schedule": {"instances": group_insts, "assignment": group_assigns}
    }


def _parse_and_clean_payload(content: bytes) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Синхронно в пуле потоков парсит 50 МБ JSON и фильтрует целевую группу.

    Используется в asyncio.to_thread, чтобы не блокировать event loop FastAPI.
    Возвращает (published_at, cleaned_snapshot).
    """
    val = json.loads(content).get("value", {})
    snapshot = val.get("publishedSnapshot") or val
    pub_at = snapshot.get("publishedAt")
    cleaned = filter_snapshot_for_target_group(snapshot)
    return pub_at, cleaned


def _persist_snapshot_to_redis(snapshot: Dict[str, Any]) -> None:
    """В фоновом режиме сохраняет снимок и ETag в Redis."""
    from services.redis_cache import save_schedule_snapshot
    meta = {"etag": _LAST_ETAG, "last_modified": _LAST_MODIFIED, "published_at": _LAST_PUBLISHED_AT}
    asyncio.create_task(save_schedule_snapshot(snapshot, meta))


async def process_api_response(res: httpx.Response, now: float) -> Optional[Dict[str, Any]]:
    """
    Обрабатывает ответ API КТМУ (304 или 200) без блокировки основного потока.

    Возвращает очищенный срез расписания или текущий кэш при ошибке.
    """
    global _DATA_CACHE, _LAST_PUBLISHED_AT
    if res.status_code == 304:
        _DATA_CACHE = (now, _DATA_CACHE[1])
        return _DATA_CACHE[1]
    if res.status_code != 200:
        log.error(f"Ошибка API КТМУ: HTTP {res.status_code}")
        return _DATA_CACHE[1]
    update_cache_headers(res.headers)
    pub_at, cleaned = await asyncio.to_thread(_parse_and_clean_payload, res.content)
    if pub_at and pub_at != _LAST_PUBLISHED_AT:
        log.info(f"Обнаружена новая публикация расписания КТМУ от: {pub_at}")
        _LAST_PUBLISHED_AT = pub_at
    _DATA_CACHE = (now, cleaned)
    _persist_snapshot_to_redis(cleaned)
    return cleaned


_IS_REFRESHING: bool = False


async def _fetch_remote_schedule() -> httpx.Response:
    """Выполняет HTTP-запрос к расписанию КТМУ с заголовками кэширования."""
    client = get_http_client()
    headers = {}
    if _LAST_ETAG:
        headers["If-None-Match"] = _LAST_ETAG
    if _LAST_MODIFIED:
        headers["If-Modified-Since"] = _LAST_MODIFIED
    return await client.get(SCHEDULE_API_URL, headers=headers)


async def refresh_schedule_in_background(force: bool = False) -> None:
    """
    Асинхронно обновляет расписание КТМУ с защитой от частых сбоев.

    При ошибке сети включает 5-минутный кулдаун для предотвращения спама.
    """
    global _IS_REFRESHING, _COOLDOWN_UNTIL
    if _IS_REFRESHING:
        return
    _IS_REFRESHING = True
    now = time.time()
    try:
        res = await _fetch_remote_schedule()
        await process_api_response(res, now)
        _COOLDOWN_UNTIL = 0.0
    except Exception as e:
        _COOLDOWN_UNTIL = now + _COOLDOWN_SECONDS
        err_msg = repr(e) if str(e) == "" else f"{type(e).__name__}: {e}"
        log.warning(f"Фоновое обновление API КТМУ не удалось ({err_msg}). Используется кэш (кулдаун 5 мин).")
    finally:
        _IS_REFRESHING = False


async def init_schedule_cache_from_redis(now: float) -> bool:
    """Загружает срез расписания и метаданные из Redis для мгновенного холодного старта."""
    global _DATA_CACHE, _LAST_ETAG, _LAST_MODIFIED, _LAST_PUBLISHED_AT
    from services.redis_cache import load_schedule_snapshot
    snap, meta = await load_schedule_snapshot()
    if snap and meta:
        _DATA_CACHE = (now, snap)
        _LAST_ETAG = meta.get("etag")
        _LAST_MODIFIED = meta.get("last_modified")
        _LAST_PUBLISHED_AT = meta.get("published_at")
        log.info("Кэш расписания успешно восстановлен из Redis (мгновенный cold-start)")
        return True
    return False


async def fetch_schedule_data(force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Отдаёт расписание из памяти/Redis или обновляет данные с учетом кулдауна.

    Предотвращает цикличные зависания и обеспечивает мгновенный холодный старт.
    """
    now = time.time()
    if force_refresh:
        await refresh_schedule_in_background(force=True)
        if _DATA_CACHE[1] is None:
            await init_schedule_cache_from_redis(now)
        return _DATA_CACHE[1]
    if _DATA_CACHE[1] is None and await init_schedule_cache_from_redis(now):
        if now >= _COOLDOWN_UNTIL:
            asyncio.create_task(refresh_schedule_in_background())
        return _DATA_CACHE[1]
    cache_valid = (now - _DATA_CACHE[0] < SCHEDULE_CACHE_TTL_SECONDS)
    if _DATA_CACHE[1] is not None:
        if not cache_valid and now >= _COOLDOWN_UNTIL:
            asyncio.create_task(refresh_schedule_in_background())
        return _DATA_CACHE[1]
    await refresh_schedule_in_background()
    return _DATA_CACHE[1]


def extract_entity_maps(data: Dict[str, Any]) -> Tuple[Dict, Dict, Dict, Dict, Dict]:
    """
    Извлекает маппинги предмет/учитель/кабинет/группа/типы пар.

    :param data: JSON данные
    :return: Кортеж словарей
    """
    subjs = {s["id"]: s.get("name", "") for s in data.get("subjects", []) if isinstance(s, dict)}
    teachs = {t["id"]: t.get("name", "") for t in data.get("teachers", []) if isinstance(t, dict)}
    rms = {r["id"]: r.get("name", "") for r in data.get("rooms", []) if isinstance(r, dict)}
    groups = {g["id"]: g for g in data.get("groups", []) if isinstance(g, dict)}
    l_types = {l["id"]: l.get("name", "") for l in data.get("lessonTypes", []) if isinstance(l, dict)}
    return (subjs, teachs, rms, groups.get(GROUP_ID, {}), l_types)


def resolve_teacher_contact_info(
    raw_teacher: str,
    teacher_data_map: Dict[str, TeacherData],
    is_remote: bool,
    subj_name: str
) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
    """
    Получает актуальные ФИО преподавателя и ссылки на видеоконференцию.
    """
    if not raw_teacher:
        return "Преподаватель", None, None, None
    last_name = raw_teacher.split()[0].lower()
    t_info = teacher_data_map.get(last_name)
    if t_info:
        name = t_info.get("full_name") or raw_teacher
        creds = extract_zoom_creds(t_info["link_info"]) if (is_remote and t_info.get("link_info")) else (None, None, None)
        return (name, *creds)
    if is_remote:
        import asyncio
        from services.notifier import notify_missing_teacher
        asyncio.create_task(notify_missing_teacher(raw_teacher, subj_name))
    return raw_teacher, None, None, None


def resolve_room_name(asgn: Dict[str, Any], inst: Dict[str, Any], rms: Dict[str, str], is_remote: bool) -> str:
    """Определяет наименование аудитории или бейдж дистанта."""
    if is_remote:
        return "Дистанционно"
    room_id = asgn.get("roomId") or (inst.get("preferredRoomIds") or [""])[0]
    return rms.get(room_id, room_id)


def build_lesson_object(
    inst: Dict[str, Any], asgn: Dict[str, Any], maps: Tuple[Dict, Dict, Dict, Dict, Dict],
    day_idx: int, week_num: int, teacher_map: Dict[str, TeacherData], cfg: Optional[Dict[str, Any]] = None
) -> Lesson:
    """Собирает объект Lesson с точным расписанием звонков и признаком потока."""
    subjs, teachs, rms, group_data, l_types = maps
    period = asgn.get("period", 0)
    time_str = get_period_time_str(group_data, day_idx, period, week_num, cfg)
    subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Занятие"))
    is_remote = inst.get("format") == "remote"
    r_name = resolve_room_name(asgn, inst, rms, is_remote)
    t_name, link, mid, passc = resolve_teacher_contact_info(teachs.get(inst.get("teacherId"), ""), teacher_map, is_remote, subj_name)
    return Lesson(
        period=period, time_str=time_str, subject=subj_name, lesson_type=l_types.get(inst.get("typeId"), "") or "Пара",
        teacher=t_name, is_remote=is_remote, room=r_name, address=resolve_room_address(r_name, is_remote),
        subgroup=extract_subgroup(inst, GROUP_ID), is_stream=is_stream_lesson(inst),
        remote_link=link, remote_passcode=passc, remote_meeting_id=mid
    )


def is_placed_lesson_active(inst: Dict[str, Any], asgn: Optional[Dict[str, Any]], day_idx: int, week_num: int) -> bool:
    """Проверяет, размещено ли занятие в сетке на указанный день и неделю."""
    if not asgn:
        return False
    return asgn.get("day") == day_idx and is_instance_active_for_week(inst, week_num)


async def get_schedule_for_date(target_date: date, force_refresh: bool = False) -> List[Lesson]:
    """Формирует список пар для группы на указанную дату с учетом потоков."""
    data = await fetch_schedule_data(force_refresh=force_refresh)
    if not data:
        return []
    sem_start = data.get("config", {}).get("semesterStart", "2026-09-01")
    week_num, day_idx = calculate_week_number(target_date, sem_start), target_date.weekday()
    sched = data.get("schedule", {})
    insts, asgns = sched.get("instances", []), sched.get("assignment", {})
    maps, links, cfg = extract_entity_maps(data), await get_teacher_links(force_refresh=force_refresh), data.get("config", {})
    lessons: List[Lesson] = []
    for inst in insts:
        if not is_item_for_group(inst, GROUP_ID):
            continue
        asgn = asgns.get(inst.get("instId", ""))
        if is_placed_lesson_active(inst, asgn, day_idx, week_num):
            lessons.append(build_lesson_object(inst, asgn, maps, day_idx, week_num, links, cfg))
    lessons.sort(key=lambda x: x.period)
    return lessons


async def get_week_schedule(monday_date: date, force_refresh: bool = False) -> List[Tuple[date, List[Lesson]]]:
    """
    Быстро формирует расписание на всю неделю в 1 проход.

    :param monday_date: Дата понедельника
    :param force_refresh: Принудительное обновление
    :return: Список кортежей (дата, список_пар)
    """
    result: List[Tuple[date, List[Lesson]]] = []
    for i in range(6):
        day_date = monday_date + timedelta(days=i)
        lessons = await get_schedule_for_date(day_date, force_refresh=force_refresh)
        result.append((day_date, lessons))
    return result
