"""
Модуль парсинга API расписания КТМУ с расчетом звонков по четности недели.

Определяет точное время звонков с учетом измененных расписаний (dayPeriodTimesByParity),
вычисляет дату, предмет, тип пары (Лек/Пр), адреса корпусов и кэширует данные.
"""

import re
import time
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import httpx
from pydantic import BaseModel

from config import GROUP_ID, SCHEDULE_API_URL, SCHEDULE_CACHE_TTL_SECONDS
from core.logger import get_logger
from services.docx_parser import TeacherData, get_teacher_links

log = get_logger("schedule_parser")

import json
import os

_DATA_CACHE: Tuple[float, Optional[Dict[str, Any]]] = (0.0, None)
_LAST_PUBLISHED_AT: Optional[str] = None
SCHEDULE_DISK_CACHE_FILE = "data/schedule_cache.json"


def load_schedule_from_disk() -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Загружает с диска кэшированный JSON расписания и метку времени публикации.

    :return: Кортеж (published_at, snapshot)
    """
    if os.path.exists(SCHEDULE_DISK_CACHE_FILE):
        try:
            with open(SCHEDULE_DISK_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("published_at"), data.get("snapshot")
        except Exception as e:
            log.error(f"Ошибка чтения schedule_cache.json: {e}")
    return None, None


def save_schedule_to_disk(published_at: Optional[str], snapshot: Dict[str, Any]) -> None:
    """
    Сохраняет расписание КТМУ на диск для мгновенного восстановления после рестарта.

    :param published_at: Метка времени публикации
    :param snapshot: Данные расписания
    """
    os.makedirs(os.path.dirname(SCHEDULE_DISK_CACHE_FILE), exist_ok=True)
    try:
        with open(SCHEDULE_DISK_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"published_at": published_at, "snapshot": snapshot}, f, ensure_ascii=False)
    except Exception as e:
        log.error(f"Ошибка записи schedule_cache.json: {e}")


def _init_cache_if_empty() -> Optional[Dict[str, Any]]:
    """Инициализирует кэш в памяти данными с диска при старте."""
    global _DATA_CACHE, _LAST_PUBLISHED_AT
    if _DATA_CACHE[1] is None:
        pub_at, snapshot = load_schedule_from_disk()
        if snapshot:
            _LAST_PUBLISHED_AT = pub_at
            _DATA_CACHE = (time.time(), snapshot)
            log.info("Расписание успешно восстановлено из локального дискового кэша")
    return _DATA_CACHE[1]


async def fetch_schedule_data(force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Скачивает JSON расписания КТМУ с использованием HTTP заголовков и дискового кэша.

    :param force_refresh: Принудительно запросить свежие данные
    :return: Словарь данных или None
    """
    global _DATA_CACHE, _LAST_PUBLISHED_AT
    cached_data = _init_cache_if_empty()
    now = time.time()
    if not force_refresh and (now - _DATA_CACHE[0] < SCHEDULE_CACHE_TTL_SECONDS) and cached_data:
        return cached_data

    headers = {}
    if _LAST_PUBLISHED_AT:
        headers["If-Modified-Since"] = _LAST_PUBLISHED_AT

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(SCHEDULE_API_URL, headers=headers)
            if res.status_code == 304:
                _DATA_CACHE = (now, cached_data)
                return cached_data
            if res.status_code != 200:
                log.error(f"Ошибка API КТМУ: HTTP {res.status_code}")
                return cached_data
            val = res.json().get("value", {})
            snapshot = val.get("publishedSnapshot") or val
            pub_at = snapshot.get("publishedAt")
            _LAST_PUBLISHED_AT = pub_at
            _DATA_CACHE = (now, snapshot)
            save_schedule_to_disk(pub_at, snapshot)
            log.info(f"Обновлено расписание КТМУ от: {pub_at}")
            return snapshot
    except Exception as e:
        log.warning(f"Ошибка запроса к API КТМУ: {e}. Используем кэш.")
        return cached_data



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


def build_lesson_object(
    inst: Dict[str, Any],
    asgn: Dict[str, Any],
    entity_maps: Tuple[Dict, Dict, Dict, Dict, Dict],
    day_idx: int,
    week_num: int,
    teacher_data_map: Dict[str, TeacherData],
    global_config: Optional[Dict[str, Any]] = None
) -> Lesson:
    """
    Собирает объект Lesson с точным расписанием звонков по четности недели.

    :return: Объект Lesson
    """
    subjs, teachs, rms, group_data, l_types = entity_maps
    period = asgn.get("period", 0)
    time_str = get_period_time_str(group_data, day_idx, period, week_num, global_config)
    subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Занятие"))
    raw_type = l_types.get(inst.get("typeId"), "")
    lesson_type = raw_type if raw_type else "Пара"
    raw_teacher = teachs.get(inst.get("teacherId"), "Преподаватель")
    is_remote = inst.get("format") == "remote"
    room_id = asgn.get("roomId") or (inst.get("preferredRoomIds") or [""])[0]
    room_name = rms.get(room_id, room_id) if not is_remote else "Дистанционно"
    address = resolve_room_address(room_name, is_remote)

    teacher_name, remote_link, meeting_id, passcode = raw_teacher, None, None, None
    if raw_teacher:
        last_name = raw_teacher.split()[0].lower()
        t_info = teacher_data_map.get(last_name)
        if t_info:
            teacher_name = t_info.get("full_name") or raw_teacher
            if is_remote and t_info.get("link_info"):
                remote_link, meeting_id, passcode = extract_zoom_creds(t_info["link_info"])
        elif is_remote:
            import asyncio
            from services.notifier import notify_missing_teacher
            asyncio.create_task(notify_missing_teacher(raw_teacher, subj_name))

    subgroup = inst.get("subgroup", 0)
    return Lesson(
        period=period, time_str=time_str, subject=subj_name,
        lesson_type=lesson_type, teacher=teacher_name, is_remote=is_remote,
        room=room_name, address=address, subgroup=subgroup, remote_link=remote_link,
        remote_passcode=passcode, remote_meeting_id=meeting_id
    )


async def get_schedule_for_date(target_date: date, force_refresh: bool = False) -> List[Lesson]:
    """
    Формирует список пар для группы на указанную дату.

    :param target_date: Целевая дата
    :param force_refresh: Принудительный запрос свежих данных
    :return: Список объектов Lesson
    """
    data = await fetch_schedule_data(force_refresh=force_refresh)
    if not data:
        return []
    sem_start = data.get("config", {}).get("semesterStart", "2026-09-01")
    week_num = calculate_week_number(target_date, sem_start)
    day_idx = target_date.weekday()
    sched = data.get("schedule", {})
    instances = sched.get("instances", [])
    assignment = sched.get("assignment", {})
    entity_maps = extract_entity_maps(data)
    teacher_links = await get_teacher_links(force_refresh=force_refresh)
    lessons: List[Lesson] = []
    for inst in instances:
        if not isinstance(inst, dict) or inst.get("groupId") != GROUP_ID:
            continue
        inst_id = inst.get("instId")
        if not inst_id or inst_id not in assignment:
            continue
        asgn = assignment[inst_id]
        if asgn.get("day") == day_idx and is_instance_active_for_week(inst, week_num):
            cfg = data.get("config", {})
            lesson = build_lesson_object(inst, asgn, entity_maps, day_idx, week_num, teacher_links, cfg)
            lessons.append(lesson)
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
