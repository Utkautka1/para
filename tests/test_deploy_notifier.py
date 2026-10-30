"""
Тесты CLI-уведомления о результате автодеплоя (services/deploy_notifier.py).

Проверяет разбор аргументов, уровень алерта и тип инцидента для успеха и сбоя.
"""

from unittest.mock import AsyncMock, patch

import pytest

from db.sqlite.models import IncidentSeverity
from services import deploy_notifier
from services.alerting import IncidentType


@pytest.mark.parametrize("argv", [[], ["deploy", "abc", "x"], ["success", "abc"]])
def test_invalid_arguments_return_usage_code(argv: list[str]) -> None:
    """Неверные аргументы не отправляют алерт и дают код выхода 2."""
    with patch.object(deploy_notifier, "send_admin_alert", AsyncMock()) as alert:
        assert deploy_notifier.main(argv) == 2
    alert.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("succeeded", "incident", "severity"),
    [
        (True, IncidentType.DEPLOY_SUCCESS, IncidentSeverity.INFO),
        (False, IncidentType.DEPLOY_FAILED, IncidentSeverity.CRITICAL),
    ],
)
async def test_notify_deploy_routes_incident(succeeded: bool, incident: str, severity: str) -> None:
    """Успех уходит как INFO DEPLOY_SUCCESS, сбой — как CRITICAL DEPLOY_FAILED."""
    with patch.object(deploy_notifier, "send_admin_alert", AsyncMock(return_value=True)) as alert:
        assert await deploy_notifier.notify_deploy(succeeded, "abc1234", "детали")
    args, kwargs = alert.call_args
    assert args[0] == incident
    assert kwargs["severity"] == severity
    assert "abc1234" in args[1]
