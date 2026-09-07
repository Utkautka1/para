"""
Инициализация aiogram Bot и Dispatcher.

Создает синглтоны bot и dp с HTML форматированием
и отключенным предпросмотром ссылок (link preview) по умолчанию.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from core.logger import get_logger

log = get_logger("bot_core")

# Бот с отключенными превью ссылок по умолчанию
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True
    )
)

dp = Dispatcher()
