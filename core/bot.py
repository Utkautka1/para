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

def create_bot_session() -> AiohttpSession:
    """Создает сессию aiohttp с пулом соединений (limit=50) и SOCKS5 прокси."""
    if PROXY_URL:
        log.info("SOCKS5 Прокси успешно подключен для Telegram API (limit=50, timeout=30s)")
        return AiohttpSession(proxy=PROXY_URL, limit=50, timeout=30.0)
    return AiohttpSession(limit=50, timeout=15.0)


session = create_bot_session()

bot = Bot(
    token=BOT_TOKEN,
    session=session,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled=True
    )
)

dp = Dispatcher()
