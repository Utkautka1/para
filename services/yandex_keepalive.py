"""
Модуль обратной совместимости keep-alive сессии Яндекс Документов.

Основная реализация перенесена в integrations/yandex_keepalive.py.
"""
import sys
import integrations.yandex_keepalive as _mod

sys.modules[__name__] = _mod
