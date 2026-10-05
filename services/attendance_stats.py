"""
Сервис агрегации сквозной статистики посещаемости студентов.

Отвечает за:
  1. Выгрузку и обход всех доступных месяцев (СЕНТ, ОКТ, ...) в таблице Яндекс Документов
  2. Подсчёт суммарных отметок (П, О, У, Н) по каждому студенту за всё время
  3. Кэширование агрегированных данных в Redis для мгновенного отклика UI и топика
  4. Формирование персонализированной аналитики для команды /my_attendance
"""

import json
from typing import Any, Dict, List, Optional
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

from core.logger import get_logger
from services.redis_cache import cache_flush, cache_get, cache_set
from services.yandex_docs import (
    MONTH_SHEET_MAP,
    download_workbook,
    init_wopi_session,
    normalize_fio,
)

log = get_logger("attendance_stats")
REDIS_STATS_KEY = "att:stats:all_time"
CACHE_TTL_SECONDS = 3600


def _init_student_stat(fio: str) -> Dict[str, Any]:
    """Инициализирует структуру счетчиков посещаемости студента."""
    return {
        "fio": fio,
        "total": {"П": 0, "О": 0, "У": 0, "Н": 0},
        "months": {},
    }


def _count_row_marks(sheet: Worksheet, row: int, mc: int) -> Dict[str, int]:
    """Подсчитывает отметки посещаемости студента в строке конкретного месяца."""
    row_counts = {"П": 0, "О": 0, "У": 0, "Н": 0}
    for col in range(3, mc + 1):
        val = sheet.cell(row, col).value
        if not val or not isinstance(val, str):
            continue
        clean_mark = val.strip().upper()
        if clean_mark in row_counts:
            row_counts[clean_mark] += 1
    return row_counts


def _aggregate_sheet_stats(
    sheet: Worksheet, s_name: str, stats: Dict[str, Dict[str, Any]]
) -> None:
    """Обрабатывает один лист месяца и накапливает отметки в общий реестр."""
    mc = sheet.max_column
    for r in range(5, 45):
        raw_fio = sheet.cell(r, 2).value
        if not raw_fio:
            continue
        fio = normalize_fio(str(raw_fio))
        if not fio:
            continue
        if fio not in stats:
            stats[fio] = _init_student_stat(fio)
        row_counts = _count_row_marks(sheet, r, mc)
        stats[fio]["months"][s_name] = row_counts
        for mark, cnt in row_counts.items():
            stats[fio]["total"][mark] += cnt


def parse_workbook_attendance(wb: openpyxl.Workbook) -> Dict[str, Dict[str, Any]]:
    """Извлекает отметки всех студентов по всем месяцам из книги openpyxl."""
    stats: Dict[str, Dict[str, Any]] = {}
    valid_months = set(MONTH_SHEET_MAP.values())
    for s_name in wb.sheetnames:
        if s_name in valid_months:
            log.debug(f"Обработка листа месяца посещаемости: {s_name}")
            _aggregate_sheet_stats(wb[s_name], s_name, stats)
    log.info(f"Собрана статистика посещаемости для {len(stats)} студентов")
    return stats


async def _load_from_redis_cache() -> Optional[Dict[str, Dict[str, Any]]]:
    """Считывает закэшированную статистику из Redis."""
    cached = await cache_get(REDIS_STATS_KEY)
    if not cached:
        return None
    try:
        return json.loads(cached)
    except Exception as e:
        log.warning(f"Ошибка десериализации кэша статистики: {e}")
        return None


async def _save_to_redis_cache(stats: Dict[str, Dict[str, Any]]) -> None:
    """Сохраняет структуру статистики в Redis с TTL 1 час."""
    try:
        payload = json.dumps(stats, ensure_ascii=False)
        await cache_set(REDIS_STATS_KEY, payload, ttl=CACHE_TTL_SECONDS)
        log.debug("Статистика посещаемости успешно закэширована в Redis")
    except Exception as e:
        log.warning(f"Не удалось закэшировать статистику в Redis: {e}")


async def invalidate_attendance_stats_cache() -> None:
    """Принудительно сбрасывает кэш сквозной статистики посещаемости."""
    await cache_flush(f"{REDIS_STATS_KEY}*")
    log.info("Кэш сквозной статистики посещаемости сброшен")


async def fetch_all_time_attendance(
    force_refresh: bool = False
) -> Dict[str, Dict[str, Any]]:
    """Возвращает сквозную статистику посещаемости с Redis-кэшированием."""
    if not force_refresh:
        cached = await _load_from_redis_cache()
        if cached:
            return cached
    log.info("Загрузка и пересчёт статистики посещаемости из Яндекс Документов...")
    wopi = await init_wopi_session()
    wb = await download_workbook(wopi)
    stats = parse_workbook_attendance(wb)
    await _save_to_redis_cache(stats)
    return stats


def find_student_attendance(
    stats: Dict[str, Dict[str, Any]], target_name: str
) -> Optional[Dict[str, Any]]:
    """Находит статистику студента по точному или частичному совпадению ФИО."""
    target_clean = normalize_fio(target_name).lower()
    for fio, data in stats.items():
        low = fio.lower()
        if target_clean in low or low in target_clean:
            return data
    parts = target_clean.split()
    if parts:
        last_name = parts[0]
        for fio, data in stats.items():
            if last_name in fio.lower():
                return data
    return None
