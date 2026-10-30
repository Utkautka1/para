"""
CLI-уведомление администратора о результате деплоя.

Запускается серверным scripts/autodeploy.sh внутри контейнера worker:
    docker exec para-worker python -m services.deploy_notifier success <sha> "<детали>"
Внутри контейнера уже настроены бот, прокси Telegram и журнал инцидентов,
поэтому shell-скрипту не нужен ни токен бота, ни свой выход в Telegram.
"""

import asyncio
import sys

from core.logger import get_logger
from db.sqlite.models import IncidentSeverity
from services.alerting import IncidentType, send_admin_alert

log = get_logger("deploy_notifier")


async def notify_deploy(succeeded: bool, revision: str, details: str) -> bool:
    """
    Отправляет администратору алерт об успешном или упавшем автодеплое.

    Возвращает True, если алерт отправлен.
    """
    if succeeded:
        return await send_admin_alert(
            IncidentType.DEPLOY_SUCCESS, f"Задеплоен {revision}", details, severity=IncidentSeverity.INFO
        )
    return await send_admin_alert(
        IncidentType.DEPLOY_FAILED, f"Автодеплой {revision} не прошёл", details, severity=IncidentSeverity.CRITICAL
    )


async def _notify_and_close(succeeded: bool, revision: str, details: str) -> bool:
    """Отправляет алерт и закрывает HTTP-сессию бота, чтобы короткий процесс завершился чисто."""
    from core.bot import bot

    try:
        return await notify_deploy(succeeded, revision, details)
    finally:
        await bot.session.close()


def main(argv: list[str]) -> int:
    """
    Разбирает аргументы `success|failure <sha> <детали>` и отправляет алерт.

    Возвращает код выхода процесса: 0 — отправлено, 1 — нет, 2 — неверные аргументы.
    """
    if len(argv) != 3 or argv[0] not in {"success", "failure"}:
        log.error("Использование: python -m services.deploy_notifier success|failure <sha> <детали>")
        return 2
    sent = asyncio.run(_notify_and_close(argv[0] == "success", argv[1], argv[2]))
    return 0 if sent else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
