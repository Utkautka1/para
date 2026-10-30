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


async def _dispatch_yandex_alert(details: str) -> None:
    """Отправляет уведомление администратору об инвалидации кук Яндекс."""
    try:
        from services.alerting import IncidentType, send_admin_alert

        await send_admin_alert(
            incident_type=IncidentType.YANDEX_COOKIE_EXPIRED,
            title="Сессия Яндекс Документов не активна",
            description=f"Сбой Keep-Alive: {details}. Обновите куки через scripts/sync_yandex_cookie.py.",
            severity="WARNING",
        )
    except Exception as exc:
        log.debug("Не удалось отправить алерт Яндекс: %s", exc)


async def ping_yandex_session() -> bool:
    """Выполняет одиночный проверочный запрос для продления сессии и обновления Cookie."""
    try:
        html = await fetch_page_dom(ATTENDANCE_DOC_URL)
        config = extract_client_config(html)
        if config.get("officeActionData"):
            log.info("✅ Сессия Яндекс Документов успешно продлена (Keep-Alive OK)")
            return True
        await _dispatch_yandex_alert("В ответе отсутствует officeActionData")
    except Exception as e:
        log.warning("⚠️ Ошибка фонового продления сессии Яндекс Документов: %s", e)
        await _dispatch_yandex_alert(str(e))
    return False


async def yandex_session_keepalive_loop(
    interval: int = KEEPALIVE_INTERVAL_SECONDS,
) -> None:
    """
    Запускает бесконечный цикл периодического пинга сессии Яндекс Документов.

    Предотвращает истечение токенов доступа при отсутствии пользовательской активности,
    выжидая 60 секунд перед первым запуском для стабилизации сети при старте контейнера.

    Ничего не возвращает (работает до завершения приложения или отмены задачи).
    """
    log.info("Запущен фоновый мониторинг сессии Яндекс (интервал: %s сек)", interval)
    await asyncio.sleep(60)
    while True:
        try:
            await ping_yandex_session()
        except asyncio.CancelledError:
            log.info("Цикл keepalive сессии Яндекс остановлен")
            break
        except Exception as e:
            log.error("Непредвиденная ошибка в keepalive цикле Яндекс: %s", e)
        await asyncio.sleep(interval)
