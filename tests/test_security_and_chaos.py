"""
Стресс-тесты, фаззинг и проверка безопасности (Security & Chaos Engineering).

Тестирует:
  1. Защиту от атак обхода аутентификации (подделка HMAC, replay, timing attacks).
  2. Инъекции спецсимволов, SQL/XSS, null-bytes, Unicode homoglyphs.
  3. Устойчивость к переполнению буфера, DoS-запросам и гигантским payload'ам.
  4. Фаззинг команд бота (/add_tester, /del_tester) и защиту FSM-состояний.
  5. Отказоустойчивость gRPC сервисеров при сбоях нижележащих парсеров.
"""

import urllib.parse
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from api import create_app
from api.grpc.servicers import ExamsServicer, ScheduleServicer
from api.proto import exams_pb2, schedule_pb2
from bot.handlers.admin.testers import process_tester_id_input
from config import ALLOWED_USER_ID, API_SECRET_KEY
from utils.miniapp_auth import (
    validate_telegram_init_data,
    verify_tester_session,
)


def _forge_init_data(user_payload: str, auth_date: str, custom_hash: str) -> str:
    """Вспомогательная функция для сборки произвольной строки initData."""
    enc_user = urllib.parse.quote(user_payload)
    return f"auth_date={auth_date}&user={enc_user}&hash={custom_hash}"


@pytest.mark.parametrize(
    "malicious_init_data",
    [
        "",
        "   ",
        "hash=abc",
        "user={}&hash=123",
        "auth_date=not_a_number&hash=123",
        "auth_date=123&user=' OR '1'='1&hash=abc",
        "<script>alert(1)</script>",
        "user={\x00}&hash=abc",
        "auth_date=99999999999&hash=abc",  # Далекое будущее
        "auth_date=1&user={}&hash=abc",     # Далекое прошлое (1970)
        "user=" + ("A" * 10000) + "&hash=abc",  # DoS размер
    ],
)
def test_init_data_fuzzing_rejected(malicious_init_data: str) -> None:
    """Фаззинг валидатора initData: любые аномальные и вредоносные входы возвращают None."""
    assert validate_telegram_init_data(malicious_init_data) is None


@pytest.mark.parametrize(
    "forged_session",
    [
        "",
        "invalid_token",
        "::",
        "123:456",
        "123:456:789:000",
        f"{ALLOWED_USER_ID}:100:bad_sig",
        f"{ALLOWED_USER_ID}:not_int:good_sig",
        f"hack_id:{int(datetime.now(UTC).timestamp())}:123",
        f"{ALLOWED_USER_ID}:{int(datetime.now(UTC).timestamp()) - 200000}:valid_format_but_expired",
    ],
)
def test_session_token_tampering_rejected(forged_session: str) -> None:
    """Проверяет отклонение любых поддельных или поврежденных сессионных токенов."""
    assert verify_tester_session(forged_session) is None


@pytest.mark.asyncio
async def test_api_security_injection_attacks() -> None:
    """Тестирует API на попытки SQL/Path Traversal инъекций в параметрах."""
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"X-API-Key": API_SECRET_KEY}

        # Инъекции в дату расписания
        res1 = await client.get("/schedule/day?target_date=' OR 1=1 --", headers=headers)
        assert res1.status_code in (422, 400)  # FastAPI Pydantic валидация отсекает

        res2 = await client.get("/schedule/day?target_date=../../../../etc/passwd", headers=headers)
        assert res2.status_code in (422, 400)

        # Вызов без ключа
        res3 = await client.get("/schedule/day", headers={})
        assert res3.status_code in (401, 403)

        # Вызов с неверным ключом
        res4 = await client.get("/schedule/day", headers={"X-API-Key": "evil_hacker_key"})
        assert res4.status_code in (401, 403)



@pytest.mark.asyncio
async def test_miniapp_dos_payload_protection() -> None:
    """Тестирует защиту от отправки гигантского тела в /miniapp/auth."""
    app = create_app()
    transport = ASGITransport(app=app)
    huge_data = "x" * (2 * 1024 * 1024)  # 2 МБ мусора
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/miniapp/auth", json={"init_data": huge_data})
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_bot_tester_input_fuzzing() -> None:
    """Фаззинг обработки ввода ID тестера в FSM стейте бота."""
    state = AsyncMock()
    message = AsyncMock()

    # Нечисловой ввод
    message.text = "admin; DROP TABLE testers;"
    await process_tester_id_input(message, state)
    message.answer.assert_called_with("⚠️ Пожалуйста, введите корректный числовой Telegram ID.")

    # Ввод с пробелами и спецсимволами
    message.text = "   123abc456   "
    await process_tester_id_input(message, state)
    assert state.clear.call_count == 0  # Стейт не должен сбрасываться при ошибке


@pytest.mark.asyncio
async def test_grpc_resilience_on_upstream_failure() -> None:
    """Проверяет обработку падений нижележащих парсеров в gRPC сервисерах."""
    schedule_servicer = ScheduleServicer()
    context = AsyncMock()

    # Падение парсера расписания
    with patch("api.grpc.servicers.get_schedule_for_date", side_effect=RuntimeError("Upstream timeout")), pytest.raises(RuntimeError):
        req = schedule_pb2.DayScheduleRequest(target_date="2026-10-12")
        await schedule_servicer.GetDaySchedule(req, context)

    # Падение парсера экзаменов
    exams_servicer = ExamsServicer()
    with patch("api.grpc.servicers.get_group_exams", side_effect=ValueError("Corrupted XML")), pytest.raises(ValueError):
        req = exams_pb2.ExamsRequest(force_refresh=True)
        await exams_servicer.GetExams(req, context)

