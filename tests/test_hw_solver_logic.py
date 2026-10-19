"""
Unit-тесты валидации и подготовки заданий в модуле hw_solver (bot/handlers/user/hw_solver.py).

Проверяет:
  1. Фильтрацию спама/флуда и распознавание учебных запросов (is_valid_homework_prompt)
  2. Детерминированное вычисление SHA256-хэша для анти-дубликатов (compute_content_hash)
  3. Корректное объединение инструкций реплая и основного задания (combine_prompt_and_instructions)
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Message

from bot.handlers.user.hw_solver import (
    combine_prompt_and_instructions,
    compute_content_hash,
    is_valid_homework_prompt,
    validate_hw_file_size,
)


@pytest.mark.parametrize(
    "flood_text",
    [
        "привет",
        "ок",
        "хай",
        "123",
        "спасибо",
        "доброе утро",
        "ясно",
        "понял",
        "lol",
        "кринж",
        "",
        "   ",
        "а",
        "хм",
        "👍",
        "бот",
        "тест",
    ],
)
def test_is_valid_homework_prompt_rejects_flood(flood_text: str) -> None:
    """Проверяет отклонение флуда, смайлов и коротких приветствий без медиа."""
    assert is_valid_homework_prompt(flood_text, has_media=False) is False


@pytest.mark.parametrize(
    "homework_text",
    [
        "реши пожалуйста номер 5",
        "вот задание по матану",
        "вариант 3 задача 2",
        "домашнее дз по физике",
        "лабораторное задание 1",
        "вычислить определитель матрицы",
        "найди пожалуйста предел функции",
        "упражнение номер 15",
        "составить алгоритм решения задачи",
        "практическое задание номер 4",
        "задание к зачету по математике",
        "доказать тождество для матрицы",
        "x + y = 10 найти решение",
        "билет № 12 вопрос 3",
    ],
)
def test_is_valid_homework_prompt_accepts_keywords(homework_text: str) -> None:
    """Проверяет принятие запросов с ключевыми словами учебных заданий."""
    assert is_valid_homework_prompt(homework_text, has_media=False) is True


@pytest.mark.parametrize(
    "text,has_media",
    [
        ("", True),
        (None, True),
        ("   ", True),
        ("учебник по физике", True),
        ("конспект лекции", True),
        ("фото", True),
    ],
)
def test_is_valid_homework_prompt_rejects_naked_media(text: str, has_media: bool) -> None:
    """Проверяет, что 'голые' файлы без учебного промпта отклоняются."""
    assert is_valid_homework_prompt(text, has_media=has_media) is False


@pytest.mark.parametrize(
    "text,has_media",
    [
        ("реши пожалуйста", True),
        ("задание номер 4", True),
        ("домашнее дз по физике с фото", True),
        ("вариант 2 реши задачу", True),
    ],
)
def test_is_valid_homework_prompt_accepts_media_with_prompt(text: str, has_media: bool) -> None:
    """Проверяет, что файлы с явной учебной просьбой принимаются."""
    assert is_valid_homework_prompt(text, has_media=has_media) is True


@pytest.mark.parametrize(
    "prompt,file_id",
    [
        ("Задание 1", "file_abc_123"),
        ("Задание 2", "file_abc_123"),
        ("Задание 1", "file_def_456"),
        ("", "file_only"),
        ("Текст без файла", None),
        ("Кириллица с символами: <>&%$#@", "unicode_file"),
    ],
)
def test_compute_content_hash_properties(prompt: str, file_id: str) -> None:
    """Проверяет длину 64 символа и детерминированность SHA256-хэша."""
    h1 = compute_content_hash(prompt, file_id)
    h2 = compute_content_hash(prompt, file_id)
    assert h1 == h2
    assert len(h1) == 64
    assert all(c in "0123456789abcdef" for c in h1)


def test_combine_prompt_and_instructions_texts() -> None:
    """Проверяет объединение текстовых сообщений из реплая и оригинала."""
    reply_msg = MagicMock(spec=Message, text="Реши только четные", caption=None)
    target_msg = MagicMock(spec=Message, text="Вариант 2, номера 1-6", caption=None)
    res = combine_prompt_and_instructions(reply_msg, target_msg)
    assert "Инструкция: Реши только четные" in res
    assert "Задание: Вариант 2, номера 1-6" in res


def test_combine_prompt_and_instructions_captions() -> None:
    """Проверяет обработку подписей к медиафайлам (caption) при реплае."""
    reply_msg = MagicMock(spec=Message, text=None, caption="Оформи в Word")
    target_msg = MagicMock(spec=Message, text=None, caption="Билет № 4")
    res = combine_prompt_and_instructions(reply_msg, target_msg)
    assert "Инструкция: Оформи в Word" in res
    assert "Задание: Билет № 4" in res


@pytest.mark.asyncio
async def test_is_hw_allowed_admin_rate_limit_bypass() -> None:
    """Проверяет, что администратор игнорирует ограничения rate-limit."""
    from bot.handlers.user.hw_solver import is_hw_allowed
    from config import ALLOWED_USER_ID

    msg = MagicMock(spec=Message, message_id=1, text="реши задачу 1", caption=None, photo=[], document=None)
    with (
        patch("bot.handlers.user.hw_solver.check_user_rate_limit", AsyncMock(return_value=False)),
        patch("bot.handlers.user.hw_solver.is_message_processed", AsyncMock(return_value=False)),
    ):
        assert await is_hw_allowed(msg, msg, 999999) is False
        assert await is_hw_allowed(msg, msg, ALLOWED_USER_ID) is True


@pytest.mark.asyncio
async def test_validate_hw_file_size_allowed() -> None:
    """Проверяет пропуск файлов допустимого размера (< 20 МБ)."""
    bot = MagicMock()
    bot.set_message_reaction = AsyncMock()
    msg = MagicMock(spec=Message, chat=MagicMock(id=123), message_id=456)

    # 5 МБ
    is_valid = await validate_hw_file_size(bot, msg, 5 * 1024 * 1024, "test.pdf")
    assert is_valid is True
    bot.set_message_reaction.assert_not_called()


@pytest.mark.asyncio
async def test_validate_hw_file_size_rejected() -> None:
    """Проверяет отклонение файлов более 20 МБ с установкой реакции-плеча."""
    bot = MagicMock()
    bot.set_message_reaction = AsyncMock()
    msg = MagicMock(spec=Message, chat=MagicMock(id=123), message_id=456)

    # 25 МБ
    is_valid = await validate_hw_file_size(bot, msg, 25 * 1024 * 1024, "large.pdf")
    assert is_valid is False
    bot.set_message_reaction.assert_awaited_once()
