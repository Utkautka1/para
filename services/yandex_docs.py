"""
Модуль обратной совместимости интеграции с Яндекс Документами.

Основная реализация перенесена в integrations/yandex_docs.py.
"""
import sys
import integrations.yandex_docs as _mod

sys.modules[__name__] = _mod
