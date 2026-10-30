"""
Сервис парсинга и взаимодействия с экзаменами и аттестациями КТМУ.

Извлекает полную нагрузку (loads), аттестации (Зачёты, Зачёты с оценкой,
Контрольные работы) с точной привязкой к неделям семестра.

Официальный раздел «Промежуточная аттестация» на сайте КТМУ пока пуст, поэтому
источник — план нагрузки и черновая сетка. Если аттестация уже поставлена в сетку
(assignment), берём оттуда кабинет, дату и пару. Недели позже последней
опубликованной (publishedWeeks) помечаются как предварительные.
"""

from datetime import date
from typing import Any

from config import GROUP_ID, KTMU_EXAM_TYPE_MAPPING
from core.logger import get_logger
from integrations.docx_parser import get_teacher_links
from services.models import EXAM_ROOM_TBD, ExamItem
from services.schedule_parser import (
    clean_subject_title,
    extract_entity_maps,
    fetch_schedule_data,
    get_period_time_str,
    is_item_for_group,
    resolve_room_address,
    week_day_to_date,
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
        room="Дистанционно" if is_remote else EXAM_ROOM_TBD,
        address=resolve_room_address("Дистанционно", True) if is_remote else "",
        weeks=extract_load_weeks(load),
        subgroup=subgroup,
        format_str="🌐 Дистанционно" if is_remote else "📍 Очно",
    )
    return f"{subj_name}_{type_name}_{subgroup}", item


def apply_exam_slot(item: ExamItem, inst: dict[str, Any], asgn: dict[str, Any] | None, data: dict[str, Any]) -> None:
    """
    Проставляет дату, номер и звонки пары, если аттестация стоит в сетке.

    Слот однозначен только у инстанса одной недели с назначенным днём —
    иначе оставляем диапазон недели. Без semesterStart дату не угадываем.

    Ничего не возвращает (модифицирует item in-place).
    """
    weeks = inst.get("customWeeks") or []
    cfg = data.get("config", {})
    if not asgn or asgn.get("day") is None or len(weeks) != 1 or not cfg.get("semesterStart"):
        return

    week, day, period = weeks[0], asgn["day"], asgn.get("period", 0)
    group_data = extract_entity_maps(data)[3]
    item.exam_date = week_day_to_date(week, day, cfg["semesterStart"])
    item.pair_number = period + 1
    item.time_str = get_period_time_str(group_data, day, period, week, cfg)


def resolve_exam_room(asgn: dict[str, Any] | None, rms: dict[str, str], is_remote: bool) -> str:
    """
    Определяет кабинет аттестации по назначению в сетке.

    Возвращает название кабинета, 'Дистанционно' или 'Кабинет уточняется'.
    """
    if is_remote:
        return "Дистанционно"

    return rms.get((asgn or {}).get("roomId") or "", EXAM_ROOM_TBD)


def enrich_exam_from_instance(
    inst: dict[str, Any],
    data: dict[str, Any],
    entity_maps: tuple[dict, dict, dict, dict, dict],
    exams_dict: dict[str, ExamItem],
) -> None:
    """
    Обогащает аттестацию кабинетом, неделями и слотом из сетки расписания.

    Кабинет берём только из фактического назначения (assignment.roomId):
    preferredRoomIds — пожелание планировщика, и у назначенных аттестаций
    оно расходится с реальным кабинетом (философия: 40 вместо 50).

    Ничего не возвращает (модифицирует переданный словарь exams_dict in-place).
    """
    subjs, _, rms, _, l_types = entity_maps
    valid, type_name = is_assessment_type(inst.get("typeId", ""), l_types)
    if not valid or not is_item_for_group(inst, GROUP_ID):
        return
    subj_name = clean_subject_title(subjs.get(inst.get("subjectId"), "Аттестация"))
    item = exams_dict.get(f"{subj_name}_{type_name}_{inst.get('subgroup', 0)}")
    if not item:
        return

    asgn = data.get("schedule", {}).get("assignment", {}).get(inst.get("instId", ""))
    is_remote = inst.get("format") == "remote"
    item.room = resolve_exam_room(asgn, rms, is_remote)
    # Без назначенного кабинета корпус неизвестен — не угадываем адрес по умолчанию
    item.address = "" if item.room == EXAM_ROOM_TBD else resolve_room_address(item.room, is_remote)
    if inst.get("customWeeks"):
        item.weeks = sorted(inst["customWeeks"])
    apply_exam_slot(item, inst, asgn, data)


def mark_preliminary(exams: list[ExamItem], published_weeks: list[int]) -> None:
    """
    Помечает аттестации на неделях, которые ещё не опубликованы на сайте.

    Без publishedWeeks (старый снапшот) ничего не помечаем, чтобы не пугать
    ложной пометкой.

    Ничего не возвращает (модифицирует exams in-place).
    """
    if not published_weeks:
        return

    last_published = max(published_weeks)
    for ex in exams:
        ex.is_preliminary = bool(ex.weeks) and min(ex.weeks) > last_published


def _collect_exams_from_loads(
    data: dict[str, Any], entity_maps: tuple[dict, dict, dict, dict, dict], teacher_links: dict[str, Any]
) -> dict[str, ExamItem]:
    """
    Строит реестр аттестаций группы из плана учебной нагрузки.

    Возвращает словарь {ключ_предмет_тип_подгруппа: ExamItem}.
    """
    exams_dict: dict[str, ExamItem] = {}
    for load in data.get("loads", []):
        if parsed := parse_exam_from_load(load, entity_maps, teacher_links):
            exams_dict[parsed[0]] = parsed[1]
    return exams_dict


async def get_group_exams() -> list[ExamItem]:
    """
    Извлекает полный реестр экзаменов и аттестаций группы на текущий семестр.

    Объединяет учебную нагрузку (loads) с сеткой фактически назначенных пар,
    сортируя мероприятия по датам, затем по номерам недель.

    Возвращает отсортированный хронологический список объектов ExamItem.
    """
    data = await fetch_schedule_data(force_refresh=False)
    if not data:
        return []
    entity_maps = extract_entity_maps(data)
    teacher_links = await get_teacher_links(force_refresh=False)
    exams_dict = _collect_exams_from_loads(data, entity_maps, teacher_links)
    for inst in data.get("schedule", {}).get("instances", []):
        enrich_exam_from_instance(inst, data, entity_maps, exams_dict)

    result = list(exams_dict.values())
    mark_preliminary(result, data.get("publishedWeeks", []))
    result.sort(key=lambda x: (min(x.weeks) if x.weeks else 99, x.exam_date or date.max, x.pair_number or 0, x.subject))
    return result
