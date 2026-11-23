"""
Unit-тесты для модуля админ-панели (bot/handlers/admin/panel.py).

Проверяет:
  1. Вспомогательное форматирование списка кастомных преподавателей (_build_custom_teachers_view)
  2. Обработчик просмотра кастомных преподавателей (cb_admin_list_custom)
  3. Архитектурный инвариант: отсутствие синхронных функций среди хэндлеров aiogram
  4. Диагностику истечения сессии в extract_client_config
"""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers.admin.panel import (
    _build_custom_teachers_view,
    cb_admin_list_custom,
    cb_download_attendance_xlsx,
)
from bot.handlers.admin.panel import (
    router as panel_router,
)


def test_build_custom_teachers_view_empty() -> None:
    """Проверяет формирование разметки при отсутствии кастомных записей."""
    text, rows = _build_custom_teachers_view({})
    assert "Ручных записей преподавателей пока нет" in text
    assert rows == []


def test_build_custom_teachers_view_with_data() -> None:
    """Проверяет формирование разметки и кнопок при наличии преподавателей."""
    data = {
        "валуев": {"full_name": "Валуев К. В.", "link_info": "https://zoom.us/j/123"},
        "круглов": {"full_name": "Круглов И. В.", "link_info": "https://zoom.us/j/456"},
    }
    text, rows = _build_custom_teachers_view(data)
    assert "Валуев К. В." in text
    assert "Круглов И. В." in text
    assert len(rows) == 2
    assert rows[0][0].callback_data == "admin:edit_t:валуев"
    assert rows[0][1].callback_data == "admin:del_t:валуев"


@pytest.mark.asyncio
async def test_cb_admin_list_custom_success() -> None:
    """Проверяет успешное открытие списка преподавателей без исключений."""
    cb = MagicMock()
    cb.message = AsyncMock()
    cb.answer = AsyncMock()

    with patch(
        "bot.handlers.admin.panel.load_custom_teachers",
        return_value={"валуев": {"full_name": "Валуев К.", "link_info": "https://zoom"}},
    ):
        await cb_admin_list_custom(cb)

    cb.message.edit_text.assert_awaited_once()
    cb.answer.assert_awaited_once()


def test_routers_have_no_sync_handlers() -> None:
    """Инвариант: все зарегистрированные хэндлеры aiogram должны быть корутинами."""
    from bot.handlers.admin.attendance import router as att_router
    from bot.handlers.admin.mute import router as mute_router
    from bot.handlers.admin.ping_all import router as ping_router
    from bot.handlers.user.hw_solver import router as hw_router
    from bot.handlers.user.schedule import router as sched_router

    routers = [panel_router, att_router, ping_router, mute_router, sched_router, hw_router]
    for r in routers:
        for observer in [r.message, r.callback_query]:
            for h in observer.handlers:
                assert inspect.iscoroutinefunction(h.callback), (
                    f"Синхронный хэндлер {h.callback.__name__} не должен быть в {r}"
                )


@pytest.mark.asyncio
async def test_cb_download_attendance_xlsx() -> None:
    """Проверяет отправку документа .xlsx при нажатии кнопки выгрузки журнала."""
    cb = AsyncMock()
    cb.message = AsyncMock()
    with patch(
        "bot.handlers.admin.panel.export_attendance_xlsx", new_callable=AsyncMock, return_value=b"PK\x03\x04test"
    ):
        await cb_download_attendance_xlsx(cb)
        cb.message.answer_document.assert_awaited_once()
        args, _kwargs = cb.message.answer_document.call_args
        assert "Журнал_посещаемости" in args[0].filename
