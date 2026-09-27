"""
Сервис парсинга и взаимодействия с экзаменами и аттестациями КТМУ.

Извлекает полную нагрузку (loads), аттестации (Зачёты, Зачёты с оценкой, 
Контрольные работы) с точной привязкой к неделям семестра.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

from config import GROUP_ID
from core.logger import get_logger
from services.schedule_parser import (
    clean_subject_title,
    extract_entity_maps,
    fetch_schedule_data,
    is_item_for_group,
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


def is_assessment_type(type_id: str, l_types: Dict[str, str]) -> Tuple[bool, str]:
    """
    Проверяет, относится ли пара к видам аттестаций/экзаменов.

    :return: Кортеж (флаг_успеха, название_типа)
    """
    t_name = EXAM_TYPE_MAPPING.get(type_id) or l_types.get(type_id, "")
    is_valid = t_name in ("Контрольная работа", "Зачёт", "Диф. зачёт", "Курсовая работа")
    return is_valid, t_name


def resolve_teacher_name(raw_teacher: str, teacher_links: Dict[str, Any]) -> str:
    """
    Определяет полное имя преподавателя с учетом ссылок.
    """
    last_name = raw_teacher.split()[0].lower() if raw_teacher else ""
    t_info = teacher_links.get(last_name)
    return t_info.get("full_name") if t_info else raw_teacher


def extract_load_weeks(load: Dict[str, Any]) -> List[int]:
    """
    Извлекает и сортирует номера учебных недель из нагрузки.
    """
    weeks_keys = list(load.get("weeklyPairs", {}).keys())
    weeks = [int(w) for w in weeks_keys if w.isdigit()] if weeks_keys else load.get("customWeeks", [])
    return sorted(weeks)


def parse_exam_from_load(
    load: Dict[str, Any], entity_maps: Tuple[Dict, Dict, Dict, Dict, Dict], teacher_links: Dict[str, Any]
) -> Optional[Tuple[str, ExamItem]]:
    """
    Создает элемент ExamItem из нагрузки (loads) учебного плана.
    """
    subjs, teachs, _, _, l_types = entity_maps
    valid, type_name = is_assessment_type(load.get("typeId", ""), l_types)
    if not valid or not is_item_for_group(load, GROUP_ID):
        return None

    subj_name = clean_subject_title(subjs.get(load.get("subjectId"), "Аттестация"))
    teacher_name = resolve_teacher_name(teachs.get(load.get("teacherId"), "Преподаватель"), teacher_links)
    is_remote = load.get("format") == "remote"
    subgroup = load.get("subgroup", 0)

    item = ExamItem(
        subject=subj_name, exam_type=type_name, teacher=teacher_name,
        room="Дистанционно" if is_remote else "Кабинет уточняется",
        address=resolve_room_address("Дистанционно" if is_remote else "", is_remote),
        weeks=extract_load_weeks(load), subgroup=subgroup,
        format_str="🌐 Дистанционно" if is_remote else "📍 Очно",
    )
    return f"{subj_name}_{type_name}_{subgroup}", item


def enrich_exam_from_instance(
    inst: Dict[str, Any], entity_maps: Tuple[Dict, Dict, Dict, Dict, Dict], exams_dict: Dict[str, ExamItem]
) -> None:
    """
    Уточняет аудиторию и недели из запланированного экземпляра в сетке.
    """
    subjs, _, rms, _, l_types = entity_maps
    valid, type_name = is_assessment_type(inst.get("typeId", ""), l_types)
    if not valid or not is_item_for_group(inst, GROUP_ID):
        return

    subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Аттестация"))
    subgroup = inst.get("subgroup", 0)
    key = f"{subj_name}_{type_name}_{subgroup}"

    if key in exams_dict:
        is_remote = inst.get("format") == "remote"
        room_name = rms.get((inst.get("preferredRoomIds") or [""])[0], "Кабинет уточняется") if not is_remote else "Дистанционно"
        exams_dict[key].room = room_name
        exams_dict[key].address = resolve_room_address(room_name, is_remote)
        if inst.get("customWeeks"):
            exams_dict[key].weeks = sorted(inst.get("customWeeks", []))


async def get_group_exams() -> List[ExamItem]:
    """
    Извлекает аттестации как из расписания (instances), так и из нагрузки (loads).

    :return: Список объектов ExamItem
    """
    data = await fetch_schedule_data(force_refresh=False)
    if not data:
        return []

    entity_maps = extract_entity_maps(data)
    teacher_links = await get_teacher_links(force_refresh=False)
    exams_dict: Dict[str, ExamItem] = {}

    for load in data.get("loads", []):
        parsed = parse_exam_from_load(load, entity_maps, teacher_links)
        if parsed:
            exams_dict[parsed[0]] = parsed[1]

    for inst in data.get("schedule", {}).get("instances", []):
        enrich_exam_from_instance(inst, entity_maps, exams_dict)

    result = list(exams_dict.values())
    result.sort(key=lambda x: (min(x.weeks) if x.weeks else 99, x.subject))
    return result
