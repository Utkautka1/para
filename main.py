"""
Точка входа обратной совместимости для запуска Telegram-бота.

Делегирует управление сервису bot.py согласно модульной архитектуре проекта.
"""

import asyncio
from bot import main

if __name__ == "__main__":
    asyncio.run(main())
