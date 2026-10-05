"""
Модуль обратной совместимости загрузки и парсинга контактов преподавателей.

Основная реализация перенесена в integrations/docx_parser.py.
"""
import sys
import integrations.docx_parser as _mod

sys.modules[__name__] = _mod
