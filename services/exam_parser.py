"""
Сервис парсинга и взаимодействия с экзаменами и аттестациями КТМУ.

Извлекает полную нагрузку (loads), аттестации (Зачёты, Зачёты с оценкой, 
Контрольные работы) с точной привязкой к неделям семестра.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from config import GROUP_ID
from core.logger import get_logger
from services.schedule_parser import (
    clean_subject_title,
    extract_entity_maps,
    fetch_schedule_data,
    resolve_room_address,
)
from services.docx_parser import get_teacher_links

log = get_logger("exam_parser")

EXAM_TYPE_MAPPING = {
    "yvorytrz": "Контрольная работа",
    "aeybq2f1": "Зачёт",
    "dacst0q5": "Диф. зачёт",
    "dop7h4j9": "Курсовая работа",
    "3wwyelmr": "Зачёт",
    "z5w84vq0": "Диф. зачёт",
    "8p7q22hc": "Контрольная работа",
}


class ExamItem(BaseModel):
    """Модель контрольного мероприятия/экзамена."""
    subject: str
    exam_type: str
    teacher: str
    room: str
    address: str
    weeks: List[int]
    subgroup: int = 0
    format_str: str = "Очно"


async def get_group_exams() -> List[ExamItem]:
    """
    Извлекает аттестации как из расписания (schedule.instances), так и из нагрузки (loads).

    :return: Список объектов ExamItem
    """
    data = await fetch_schedule_data(force_refresh=False)
    if not data:
        return []

    sched = data.get("schedule", {})
    instances = sched.get("instances", [])
    loads = data.get("loads", [])
    entity_maps = extract_entity_maps(data)
    subjs, teachs, rms, _, l_types = entity_maps
    teacher_links = await get_teacher_links(force_refresh=False)

    exams_dict: Dict[str, ExamItem] = {}

    # 1. Считываем из loads (учебного плана семестра)
    for load in loads:
        if not isinstance(load, dict) or load.get("groupId") != GROUP_ID:
            continue
        type_id = load.get("typeId")
        type_name = EXAM_TYPE_MAPPING.get(type_id) or l_types.get(type_id, "")
        if type_name not in ("Контрольная работа", "Зачёт", "Диф. зачёт", "Курсовая работа"):
            continue

        subj_name = clean_subject_title(subjs.get(load.get("subjectId"), "Аттестация"))
        raw_teacher = teachs.get(load.get("teacherId"), "Преподаватель")
        is_remote = load.get("format") == "remote"

        last_name = raw_teacher.split()[0].lower() if raw_teacher else ""
        t_info = teacher_links.get(last_name)
        teacher_name = t_info.get("full_name") if t_info else raw_teacher

        weeks_str_keys = list(load.get("weeklyPairs", {}).keys())
        weeks = [int(w) for w in weeks_str_keys if w.isdigit()] if weeks_str_keys else load.get("customWeeks", [])
        subgroup = load.get("subgroup", 0)

        key = f"{subj_name}_{type_name}_{subgroup}"
        exams_dict[key] = ExamItem(
            subject=subj_name,
            exam_type=type_name,
            teacher=teacher_name,
            room="Дистанционно" if is_remote else "Кабинет уточняется",
            address=resolve_room_address("Дистанционно" if is_remote else "", is_remote),
            weeks=sorted(weeks),
            subgroup=subgroup,
            format_str="🌐 Дистанционно" if is_remote else "📍 Очно",
        )

    # 2. Уточняем кабинеты из запланированных сеткой экземпляров (instances)
    for inst in instances:
        if not isinstance(inst, dict) or inst.get("groupId") != GROUP_ID:
            continue
        type_id = inst.get("typeId")
        type_name = EXAM_TYPE_MAPPING.get(type_id) or l_types.get(type_id, "")
        if type_name not in ("Контрольная работа", "Зачёт", "Диф. зачёт", "Курсовая работа"):
            continue

        subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Аттестация"))
        subgroup = inst.get("subgroup", 0)
        key = f"{subj_name}_{type_name}_{subgroup}"

        is_remote = inst.get("format") == "remote"
        room_name = rms.get((inst.get("preferredRoomIds") or [""])[0], "Кабинет уточняется") if not is_remote else "Дистанционно"
        address = resolve_room_address(room_name, is_remote)

        if key in exams_dict:
            exams_dict[key].room = room_name
            exams_dict[key].address = address
            if inst.get("customWeeks"):
                exams_dict[key].weeks = sorted(inst.get("customWeeks", []))

    result = list(exams_dict.values())
    result.sort(key=lambda x: (min(x.weeks) if x.weeks else 99, x.subject))
    return result
