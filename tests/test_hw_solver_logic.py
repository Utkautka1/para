"""
Unit-тесты валидации и подготовки заданий в модуле hw_solver.

Проверяет:
  1. Фильтрацию спама/флуда и распознавание учебных запросов
  2. Детерминированное вычисление SHA256-хэша для анти-дубликатов
  3. Корректное объединение инструкций реплая и основного задания
"""

from unittest.mock import MagicMock
from aiogram.types import Message

from bot.handlers.user.hw_solver import (
    combine_prompt_and_instructions,
    compute_content_hash,
    is_valid_homework_prompt,
)


def test_is_valid_homework_prompt_rejects_flood():
    """Проверяет, что короткие приветствия и флуд отклоняются."""
    assert is_valid_homework_prompt("привет", has_media=False) is False
    assert is_valid_homework_prompt("ок", has_media=False) is False
    assert is_valid_homework_prompt("хай", has_media=False) is False
    assert is_valid_homework_prompt("123", has_media=False) is False


def test_is_valid_homework_prompt_accepts_keywords():
    """Проверяет, что сообщения с ключевыми словами ДЗ принимаются."""
    assert is_valid_homework_prompt("реши пожалуйста номер 5", has_media=False) is True
    assert is_valid_homework_prompt("вот задание по матану", has_media=False) is True
    assert is_valid_homework_prompt("вариант 3 задача 2", has_media=False) is True


def test_is_valid_homework_prompt_accepts_media():
    """Проверяет, что при наличии медиа (фото/документ) промпт считается валидным."""
    assert is_valid_homework_prompt("", has_media=True) is True
    assert is_valid_homework_prompt(None, has_media=True) is True


def test_compute_content_hash_deterministic():
    """Проверяет детерминированность хэша SHA256 от текста и ID файла."""
    h1 = compute_content_hash("Задание 1", "file_abc_123")
    h2 = compute_content_hash("Задание 1", "file_abc_123")
    h3 = compute_content_hash("Задание 2", "file_abc_123")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64


def test_combine_prompt_and_instructions():
    """Проверяет слияние инструкций реплая и основного текста задания."""
    reply_msg = MagicMock(spec=Message)
    reply_msg.text = "Реши только четные"
    reply_msg.caption = None

    target_msg = MagicMock(spec=Message)
    target_msg.text = "Вариант 2, номера 1-6"
    target_msg.caption = None

    res = combine_prompt_and_instructions(reply_msg, target_msg)
    assert "Инструкция: Реши только четные" in res
    assert "Задание: Вариант 2, номера 1-6" in res
