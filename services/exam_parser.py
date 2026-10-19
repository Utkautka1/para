"""
Сервис парсинга и взаимодействия с экзаменами и аттестациями КТМУ.

Извлекает полную нагрузку (loads), аттестации (Зачёты, Зачёты с оценкой,
Контрольные работы) с точной привязкой к неделям семестра.
"""

from typing import Any

from config import GROUP_ID, KTMU_EXAM_TYPE_MAPPING
from core.logger import get_logger
from integrations.docx_parser import get_teacher_links
from services.models import ExamItem
from services.schedule_parser import (
    clean_subject_title,
    extract_entity_maps,
    fetch_schedule_data,
    is_item_for_group,
    resolve_room_address,
)

log = get_logger("exam_parser")

EXAM_TYPE_MAPPING = KTMU_EXAM_TYPE_MAPPING


def is_assessment_type(type_id: str, l_types: dict[str, str]) -> tuple[bool, str]:
    """
    Проверяет принадлежность идентификатора занятия к формам промежуточной аттестации.

    Использует сопоставление внутренних хешей КТМУ и справочника lessonTypes для
    выделения зачетов, дифференцированных зачетов, контрольных и курсовых работ.

    Возвращает кортеж (is_valid, type_name).
    """
    t_name = EXAM_TYPE_MAPPING.get(type_id) or l_types.get(type_id, "")
    is_valid = t_name in ("Контрольная работа", "Зачёт", "Диф. зачёт", "Курсовая работа")
    return is_valid, t_name


def resolve_teacher_name(raw_teacher: str, teacher_links: dict[str, Any]) -> str:
    """
    Определяет актуальное полное ФИО преподавателя по справочнику контактов.

    Извлекает фамилию для регистронезависимого поиска, предотвращая сокращение
    инициалов в академических отчетах.

    Возвращает строку с полным ФИО или исходное значение.
    """
    last_name = raw_teacher.split()[0].lower() if raw_teacher else ""
    t_info = teacher_links.get(last_name)
    return t_info.get("full_name") if t_info else raw_teacher


def extract_load_weeks(load: dict[str, Any]) -> list[int]:
    """
    Извлекает и упорядочивает номера учебных недель проведения аттестации.

    Анализирует ключи словаря weeklyPairs или список customWeeks, отсекая нечисловые значения.

    Возвращает отсортированный по возрастанию список номеров недель.
    """
    weeks_keys = list(load.get("weeklyPairs", {}).keys())
    weeks = [int(w) for w in weeks_keys if w.isdigit()] if weeks_keys else load.get("customWeeks", [])
    return sorted(weeks)


def parse_exam_from_load(
    load: dict[str, Any], entity_maps: tuple[dict, dict, dict, dict, dict], teacher_links: dict[str, Any]
) -> tuple[str, ExamItem] | None:
    """
    Формирует объект аттестации ExamItem из блока учебной нагрузки (loads).

    Фильтрует нагрузки только для группы 1-КПД-3, разрешает адрес корпуса
    и форматирует бейдж очного/дистанционного формата.

    Возвращает кортеж (уникальный_ключ, ExamItem) или None.
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
        subject=subj_name,
        exam_type=type_name,
        teacher=teacher_name,
        room="Дистанционно" if is_remote else "Кабинет уточняется",
        address=resolve_room_address("Дистанционно" if is_remote else "", is_remote),
        weeks=extract_load_weeks(load),
        subgroup=subgroup,
        format_str="🌐 Дистанционно" if is_remote else "📍 Очно",
    )
    return f"{subj_name}_{type_name}_{subgroup}", item


def enrich_exam_from_instance(
    inst: dict[str, Any], entity_maps: tuple[dict, dict, dict, dict, dict], exams_dict: dict[str, ExamItem]
) -> None:
    """
    Обогащает данные аттестации точным номером аудитории и неделями из сетки расписания.

    Связывает плановую нагрузку с фактическим расписанием пар (instances),
    уточняя аудиторию и адрес корпуса.

    Ничего не возвращает (модифицирует переданный словарь exams_dict in-place).
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
        room_name = (
            rms.get((inst.get("preferredRoomIds") or [""])[0], "Кабинет уточняется")
            if not is_remote
            else "Дистанционно"
        )
        exams_dict[key].room = room_name
        exams_dict[key].address = resolve_room_address(room_name, is_remote)
        if inst.get("customWeeks"):
            exams_dict[key].weeks = sorted(inst.get("customWeeks", []))


async def get_group_exams() -> list[ExamItem]:
    """
    Извлекает полный реестр экзаменов и аттестаций группы на текущий семестр.

    Объединяет учебную нагрузку (loads) с сеткой фактически назначенных пар,
    сортируя мероприятия по номерам ближайших недель проведения.

    Возвращает отсортированный хронологический список объектов ExamItem.
    """
    data = await fetch_schedule_data(force_refresh=False)
    if not data:
        return []
    entity_maps = extract_entity_maps(data)
    teacher_links = await get_teacher_links(force_refresh=False)
    exams_dict: dict[str, ExamItem] = {}
    for load in data.get("loads", []):
        parsed = parse_exam_from_load(load, entity_maps, teacher_links)
        if parsed:
            exams_dict[parsed[0]] = parsed[1]
    for inst in data.get("schedule", {}).get("instances", []):
        enrich_exam_from_instance(inst, entity_maps, exams_dict)
    result = list(exams_dict.values())
    result.sort(key=lambda x: (min(x.weeks) if x.weeks else 99, x.subject))
    return result
