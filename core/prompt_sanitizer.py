"""
Санитайзер и валидатор входных пользовательских промптов для нейросетевых моделей.

Защищает нейросетевой пайплайн от атак Prompt Injection, попыток побега
из контекстных XML-тегов (jailbreak) и утечки системного промпта.
"""

import html
import re
import unicodedata
from dataclasses import dataclass

from core.logger import get_logger

log = get_logger("prompt_sanitizer")

# Регулярные выражения для поиска опасных паттернов prompt injection
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|system)\s+(prompts?|instructions?)", re.IGNORECASE),
    re.compile(r"system\s+prompt\s*(leak|reveal|output|display|show)", re.IGNORECASE),
    re.compile(r"(reveal|print|show)\s+(your\s+)?(initial|system|secret)\s+instructions?", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(DAN|unrestricted|in\s+developer\s+mode)", re.IGNORECASE),
    re.compile(r"забудь\s+(все\s+)?(предыдущие|прошлые)\s+инструкции", re.IGNORECASE),
    re.compile(r"(покажи|выведи|раскрой)\s+(свой\s+)?системный\s+промпт", re.IGNORECASE),
]

_CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F\u200B-\u200D\uFEFF]")


@dataclass(frozen=True)
class SanitizeResult:
    """Результат санитарной обработки пользовательского промпта."""

    clean_text: str
    is_suspicious: bool
    flags: tuple[str, ...]


def remove_invisible_control_chars(text: str) -> str:
    """Удаляет нулевые байты и невидимые управляющие символы."""
    normalized = unicodedata.normalize("NFKC", text)
    return _CONTROL_CHARS_PATTERN.sub("", normalized)


def escape_context_delimiters(text: str) -> str:
    """
    Экранирует теги XML и угловые скобки для изоляции контекста.

    Предотвращает закрытие защитного тега </учебное_задание>.
    """
    escaped = html.escape(text, quote=False)
    return escaped.replace("</учебное_задание>", "&lt;/учебное_задание&gt;")


def detect_injection_indicators(text: str) -> list[str]:
    """Сканирует текст на наличие сигнатур prompt injection и jailbreak."""
    matched_flags: list[str] = []
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            matched_flags.append(pattern.pattern)
    return matched_flags


def sanitize_prompt(raw_text: str | None, max_length: int = 15000) -> SanitizeResult:
    """
    Санирует пользовательский запрос перед встраиванием в шаблон LLM.

    Очищает управляющие символы, обрезает по лимиту длины, экранирует XML
    и проверяет на попытки инъекций.
    """
    if not raw_text:
        return SanitizeResult(clean_text="Реши все задания с листа.", is_suspicious=False, flags=())

    cleaned = remove_invisible_control_chars(raw_text.strip())[:max_length]
    flags = detect_injection_indicators(cleaned)
    is_suspicious = len(flags) > 0

    if is_suspicious:
        log.warning("⚠️ Обнаружен подозрительный ввод (Prompt Injection): %s", flags)

    safe_text = escape_context_delimiters(cleaned)
    return SanitizeResult(clean_text=safe_text, is_suspicious=is_suspicious, flags=tuple(flags))
