"""
Модуль обратной совместимости операций с кэшем Redis.

Основная реализация перенесена в core/redis_cache.py.
"""
import sys
import core.redis_cache as _mod

sys.modules[__name__] = _mod
