"""
Инициализация aiogram Bot и Dispatcher.

Создает синглтоны bot и dp с HTML форматированием
и отключенным предпросмотром ссылок (link preview) по умолчанию.
"""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from config import BOT_TOKEN, PROXY_URL
from core.logger import get_logger

log = get_logger("bot_core")

session = AiohttpSession(proxy=PROXY_URL, timeout=30.0) if PROXY_URL else AiohttpSession(timeout=10.0)
if PROXY_URL:
    log.info("SOCKS5 Прокси успешно подключен для Telegram API")

bot = Bot(
    token=BOT_TOKEN,
    session=session,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True
    )
)

dp = Dispatcher()
