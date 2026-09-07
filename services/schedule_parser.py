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

_DATA_CACHE: Tuple[float, Optional[Dict[str, Any]]] = (0.0, None)
_LAST_PUBLISHED_AT: Optional[str] = None


class Lesson(BaseModel):
    """Модель данных одного занятия в расписании."""
    period: int
    time_str: str
    subject: str
    lesson_type: str
    teacher: str
    is_remote: bool
    room: str
    address: str
    subgroup: int = 0
    remote_link: Optional[str] = None
    remote_passcode: Optional[str] = None
    remote_meeting_id: Optional[str] = None


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
    url_m = re.search(r"https?://[^\s<>\"\'\`]+", text)
    id_m = re.search(r"(?:Идентификатор(?:\s+конференции)?|Meeting\s+ID)[:\s]+([0-9\s]{8,15})", text, re.IGNORECASE)
    pass_m = re.search(r"(?:Код(?:\s+доступа)?|Passcode)[:\s]+([A-Za-z0-9]+)", text, re.IGNORECASE)
    url = url_m.group(0) if url_m else (text if text.startswith("http") else None)
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


def get_period_time_str(
    group_data: Dict[str, Any],
    day_idx: int,
    period_idx: int,
    week_num: int,
    global_config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Определяет интервал времени пары строго из API КТМУ без сомнительных угадываний.

    :param group_data: Метаданные группы
    :param day_idx: День недели (0-6)
    :param period_idx: Номер пары (0-indexed)
    :param week_num: Номер недели
    :param global_config: Глобальный конфиг API КТМУ
    :return: Точная строка времени или бейдж "Время уточняется"
    """
    parity = "even" if week_num % 2 == 0 else "odd"
    # 1. Проверяем измененные звонки по четности недели группы
    by_parity = group_data.get("dayPeriodTimesByParity", {}).get(parity, {}).get(str(day_idx), [])
    if period_idx < len(by_parity) and by_parity[period_idx]:
        return by_parity[period_idx]

    # 2. Проверяем стандартные звонки группы
    period_times = group_data.get("dayPeriodTimes", {}).get(str(day_idx), [])
    if period_idx < len(period_times) and period_times[period_idx]:
        return period_times[period_idx]

    # 3. Проверяем общие звонки КТМУ из config.periodTimes
    if global_config and "periodTimes" in global_config:
        g_times = global_config["periodTimes"]
        if period_idx < len(g_times) and g_times[period_idx]:
            return g_times[period_idx]

    return "Время уточняется"


async def fetch_schedule_data(force_refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    Скачивает JSON расписания КТМУ с отслеживанием времени публикации.

    :param force_refresh: Принудительно запросить свежие данные
    :return: Словарь данных или None
    """
    global _DATA_CACHE, _LAST_PUBLISHED_AT
    now = time.time()
    if not force_refresh and (now - _DATA_CACHE[0] < SCHEDULE_CACHE_TTL_SECONDS) and _DATA_CACHE[1]:
        return _DATA_CACHE[1]
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(SCHEDULE_API_URL)
            if res.status_code != 200:
                log.error(f"Ошибка API КТМУ: HTTP {res.status_code}")
                return _DATA_CACHE[1]
            val = res.json().get("value", {})
            snapshot = val.get("publishedSnapshot") or val
            pub_at = snapshot.get("publishedAt")
            if pub_at and pub_at != _LAST_PUBLISHED_AT:
                log.info(f"Обнаружена новая публикация расписания КТМУ от: {pub_at}")
                _LAST_PUBLISHED_AT = pub_at
            _DATA_CACHE = (now, snapshot)
            return snapshot
    except Exception as e:
        log.error(f"Исключение при запросе к API КТМУ: {e}", exc_info=True)
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
