"""
Применение замен (substitutions) API КТМУ к сетке расписания группы.

Базовая сетка (schedule.instances + assignment) не знает о разовых изменениях:
сдвиг пары, смена кабинета/преподавателя/формата, отмены и переносы на другой день
лежат отдельным списком substitutions с привязкой к дате. Сайт накладывает их
поверх сетки — этот модуль делает то же самое для бота и API.

Замена ссылается на занятие по instId без суффикса публикации '__PUBW<n>':
'X__EXACT_W9' в замене соответствует инстансу 'X__EXACT_W9__PUBW9' в снапшоте.
"""

import re
from typing import Any

# Суффикс, который публикация дописывает к instId недельной копии занятия
_PUBLISH_SUFFIX_RE = re.compile(r"__PUBW\d+$")

# Типы замен, при которых пара в исходную дату не проводится
CANCEL_TYPES = frozenset({"cancel", "cancel_assignment", "pending_move", "excursion", "moved"})

# Типы замен, которые меняют параметры пары в ту же дату
PATCH_TYPES = frozenset({"sub", "join_subgroup"})


def base_inst_id(inst_id: str) -> str:
    """
    Приводит instId инстанса к виду, в котором на него ссылаются замены.

    Возвращает instId без суффикса публикации '__PUBW<n>'.
    """
    return _PUBLISH_SUFFIX_RE.sub("", inst_id)


def filter_group_substitutions(subs: list[dict[str, Any]], group_insts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Оставляет только замены, относящиеся к занятиям группы.

    Нужен при фильтрации снапшота: в API ~150 замен на весь колледж,
    а храним в Redis и памяти только срез одной группы.

    Возвращает список замен группы.
    """
    group_ids = {base_inst_id(i["instId"]) for i in group_insts if "instId" in i}
    return [s for s in subs if isinstance(s, dict) and s.get("instId") in group_ids]


def index_day_substitutions(subs: list[dict[str, Any]], iso_date: str) -> dict[str, dict[str, Any]]:
    """
    Индексирует замены, действующие в исходную дату, по instId занятия.

    Возвращает словарь {instId: замена}.
    """
    return {s["instId"]: s for s in subs if s.get("date") == iso_date and s.get("instId")}


def moved_in_substitutions(subs: list[dict[str, Any]], iso_date: str) -> list[dict[str, Any]]:
    """
    Отбирает переносы, у которых целевая дата совпадает с запрошенной.

    Возвращает список замен типа 'moved' с targetDate == iso_date.
    """
    return [s for s in subs if s.get("type") == "moved" and s.get("targetDate") == iso_date]


def is_cancelled_for_group(sub: dict[str, Any], group_id: str) -> bool:
    """
    Проверяет, снимает ли замена пару группы в исходную дату.

    stream_group_cancel отменяет потоковую пару только у групп из excludedGroupIds,
    остальные группы потока занимаются по расписанию.

    Возвращает True, если пару нужно убрать из дня.
    """
    sub_type = sub.get("type")
    if sub_type == "stream_group_cancel":
        return group_id in (sub.get("excludedGroupIds") or [])

    return sub_type in CANCEL_TYPES


def _patch_assignment(asgn: dict[str, Any], sub: dict[str, Any], period_key: str) -> dict[str, Any]:
    """
    Накладывает новую пару и кабинет замены на копию назначения.

    Пустые/None-поля замены означают «без изменений», поэтому их пропускаем.

    Возвращает новый словарь назначения.
    """
    patched = dict(asgn)
    if sub.get(period_key) is not None:
        patched["period"] = sub[period_key]
    if sub.get("newRoomId"):
        patched["roomId"] = sub["newRoomId"]
    return patched


def _patch_instance(inst: dict[str, Any], sub: dict[str, Any]) -> dict[str, Any]:
    """
    Накладывает нового преподавателя и формат замены на копию инстанса.

    Возвращает новый словарь инстанса.
    """
    patched = dict(inst)
    if sub.get("newTeacherId"):
        patched["teacherId"] = sub["newTeacherId"]
    if sub.get("newFormat"):
        patched["format"] = sub["newFormat"]
    return patched


def apply_substitution(
    inst: dict[str, Any], asgn: dict[str, Any], sub: dict[str, Any], period_key: str = "newPeriod"
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Возвращает копии инстанса и назначения с изменениями из замены.

    period_key — 'newPeriod' для замены в тот же день, 'targetPeriod' для переноса.
    Исходные словари не мутируются: они живут в общем кэше снапшота.

    Возвращает кортеж (инстанс, назначение).
    """
    return _patch_instance(inst, sub), _patch_assignment(asgn, sub, period_key)
