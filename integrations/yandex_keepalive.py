"""
Фоновый сервис автоматического продления (Keep-Alive) сессии Яндекс Документов.

Каждые 6 часов отправляет фоновый запрос к документу посещаемости,
предотвращая инвалидацию сессии по неактивности и сохраняя обновленные
токены Set-Cookie (_yasc, yandex_360_session_exp_cache) в Redis.
"""

import asyncio

from config import ATTENDANCE_DOC_URL, YANDEX_KEEPALIVE_INTERVAL_SECONDS
from core.logger import get_logger
from integrations.yandex_docs import extract_client_config, fetch_page_dom

log = get_logger("yandex_keepalive")

# Интервал фонового подогрева сессии
KEEPALIVE_INTERVAL_SECONDS = YANDEX_KEEPALIVE_INTERVAL_SECONDS


async def ping_yandex_session() -> bool:
    """
    Выполняет одиночный проверочный запрос для продления сессии и обновления Cookie.

    Возвращает True, если сессия валидна и client-config извлечён.
    """
    try:
        html = await fetch_page_dom(ATTENDANCE_DOC_URL)
        config = extract_client_config(html)
        if config.get("officeActionData"):
            log.info("✅ Сессия Яндекс Документов успешно продлена (Keep-Alive OK)")
            return True
    except Exception as e:
        log.warning(f"⚠️ Ошибка фонового продления сессии Яндекс Документов: {e}")
    return False


async def yandex_session_keepalive_loop(interval: int = KEEPALIVE_INTERVAL_SECONDS) -> None:
    """
    Бесконечный цикл периодического пинга сессии Яндекс Документов.

    Первый запуск происходит через 60 секунд после старта воркера,
    затем повторяется каждые interval секунд.
    """
    log.info(f"Запущен фоновый мониторинг сессии Яндекс (интервал: {interval} сек)")
    await asyncio.sleep(60)
    while True:
        try:
            await ping_yandex_session()
        except asyncio.CancelledError:
            log.info("Цикл keepalive сессии Яндекс остановлен")
            break
        except Exception as e:
            log.error(f"Непредвиденная ошибка в keepalive цикле Яндекс: {e}")
        await asyncio.sleep(interval)
