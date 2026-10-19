"""
Модуль-фасад для санитайзера промптов в пакете solver.

Реэкспортирует функции очистки и валидации из базового модуля core.prompt_sanitizer.
"""

from core.prompt_sanitizer import (
    SanitizeResult,
    detect_injection_indicators,
    escape_context_delimiters,
    remove_invisible_control_chars,
    sanitize_prompt,
)

__all__ = [
    "SanitizeResult",
    "detect_injection_indicators",
    "escape_context_delimiters",
    "remove_invisible_control_chars",
    "sanitize_prompt",
]
