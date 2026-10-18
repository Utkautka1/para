"""
Утилита парсинга строк времени мута в секунды.

Преобразует выражения типа '5с', '10м', '2ч', '1д' в секунды
для передачи в Bot.restrict_chat_member.
"""

from config import DURATION_MULTIPLIERS, DURATION_REGEX


def parse_duration_to_seconds(time_str: str) -> int | None:
    """
    Парсит текстовое выражение длительности ('5с', '10м', '2ч', '1д') в секунды.

    Использует регулярное выражение для гибкого извлечения числа и единицы измерения,
    по умолчанию применяя минуты при отсутствии суффикса.

    Возвращает целочисленное количество секунд или None при невалидном формате строки.
    """
    match = DURATION_REGEX.match(time_str.strip().lower())
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2) or "м"
    return amount * DURATION_MULTIPLIERS.get(unit, 60)

