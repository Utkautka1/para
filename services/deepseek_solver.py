"""
Модуль обратной совместимости для решения ДЗ через DeepSeek API.

Основная реализация перенесена в integrations/deepseek.py.
"""
import sys
import integrations.deepseek as _mod

sys.modules[__name__] = _mod
