"""
Утилита парсинга строк времени мута в секунды.

Преобразует выражения типа '5с', '10м', '2ч', '1д' в секунды
для передачи в Bot.restrict_chat_member.
"""

import re
from typing import Optional, Tuple


def parse_duration_to_seconds(time_str: str) -> Optional[int]:
    """
    Парсит строку формата '5с', '10м', '2ч', '1д' в интервал в секундах.

    :param time_str: Строка с периодом
    :return: Секунды или None при неверном формате
    """
    match = re.match(r"^(\d+)\s*([сsмmчhдd])?$", time_str.strip().lower())
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2) or "м"
    multipliers = {
        "с": 1, "s": 1,
        "м": 60, "m": 60,
        "ч": 3600, "h": 3600,
        "д": 86400, "d": 86400
    }
    return amount * multipliers.get(unit, 60)
