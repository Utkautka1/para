"""
Модуль обратной совместимости генерации DOCX отчетов.

Основная реализация вынесена в утилитарный слой utils/doc_generator.py.
"""
import sys
import utils.doc_generator as _mod

sys.modules[__name__] = _mod
