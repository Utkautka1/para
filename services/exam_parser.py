"""
Сервис парсинга и взаимодействия с экзаменами и аттестациями КТМУ.

Скачивает промежуточную и итоговую аттестацию (зачёты, диф. зачёты, экзамены, КП),
сортирует их по неделям и формирует расписание для топика 'Экзамены'.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from config import EXAM_SCHEDULE_API_URL, GROUP_ID
from core.logger import get_logger
from services.schedule_parser import (
    calculate_week_number,
    clean_subject_title,
    extract_entity_maps,
    fetch_schedule_data,
    resolve_room_address,
)
from services.docx_parser import get_teacher_links

log = get_logger("exam_parser")

# Типы аттестаций (Экзамен, Зачёт, Диф. зачёт, Курсовая работа, Контрольная)
EXAM_TYPE_IDS = {
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
    Формирует полный список зачётов и экзаменов для группы.

    :return: Список объектов ExamItem
    """
    data = await fetch_schedule_data(force_refresh=False)
    if not data:
        return []

    sched = data.get("schedule", {})
    instances = sched.get("instances", [])
    entity_maps = extract_entity_maps(data)
    subjs, teachs, rms, _, l_types = entity_maps
    teacher_links = await get_teacher_links(force_refresh=False)

    exams: List[ExamItem] = []
    for inst in instances:
        if not isinstance(inst, dict) or inst.get("groupId") != GROUP_ID:
            continue
        type_id = inst.get("typeId")
        if type_id not in EXAM_TYPE_IDS and l_types.get(type_id) not in ("Зч", "ЗчО", "КонтрРабота", "КурсРабота"):
            continue

        subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Аттестация"))
        type_name = EXAM_TYPE_IDS.get(type_id) or l_types.get(type_id, "Экзамен/Зачёт")
        raw_teacher = teachs.get(inst.get("teacherId"), "Преподаватель")
        is_remote = inst.get("format") == "remote"
        room_name = rms.get(inst.get("preferredRoomIds", [""])[0], "Кабинет уточняется") if not is_remote else "Дистанционно"
        address = resolve_room_address(room_name, is_remote)

        last_name = raw_teacher.split()[0].lower() if raw_teacher else ""
        t_info = teacher_links.get(last_name)
        teacher_name = t_info.get("full_name") if t_info else raw_teacher

        weeks = inst.get("customWeeks", [])
        subgroup = inst.get("subgroup", 0)

        exams.append(
            ExamItem(
                subject=subj_name,
                exam_type=type_name,
                teacher=teacher_name,
                room=room_name,
                address=address,
                weeks=weeks,
                subgroup=subgroup,
                format_str="🌐 Дистанционно" if is_remote else "📍 Очно",
            )
        )
    exams.sort(key=lambda x: (min(x.weeks) if x.weeks else 99, x.subject))
    return exams
