"""
Интеграция с нейросетевым API DeepSeek (модели Vision/Flash).

Отвечает за подготовку промптов по ГОСТ 7.32-2017, кодирование изображений
в Base64, санитарную фильтрацию промптов, защиту Circuit Breaker и повторные запросы.
"""

import base64
from typing import Any, cast

from openai import AsyncOpenAI

import config
from core.circuit_breaker import CircuitBreaker, async_retry_with_backoff
from core.logger import get_logger
from core.prompt_sanitizer import sanitize_prompt

log = get_logger("deepseek")
_deepseek_client: AsyncOpenAI | None = None

# Circuit Breaker для изоляции сбоев и предотвращения каскадных падений при деградации API DeepSeek
deepseek_circuit_breaker = CircuitBreaker("deepseek", failure_threshold=3, recovery_timeout=30.0)

SYSTEM_PROMPT = config.DEEPSEEK_SYSTEM_PROMPT


def get_deepseek_client() -> AsyncOpenAI:
    """Предоставляет синглтон асинхронного клиента для взаимодействия с API DeepSeek."""
    global _deepseek_client
    if _deepseek_client is None:
        _deepseek_client = AsyncOpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_API_BASE,
        )
    return _deepseek_client


async def close_deepseek_client() -> None:
    """Корректно закрывает сетевую сессию и пул соединений клиента DeepSeek."""
    global _deepseek_client
    if _deepseek_client is not None:
        await _deepseek_client.close()
        _deepseek_client = None


def encode_image_bytes(image_bytes: bytes) -> str:
    """Кодирует сырые байты изображения задания в строку формата Base64."""
    return base64.b64encode(image_bytes).decode("utf-8")


def build_deepseek_messages(
    image_bytes: bytes | None,
    text_prompt: str | None,
) -> list[dict[str, Any]]:
    """Формирует изолированный массив контекстных сообщений с санитарной очисткой."""
    sanitized = sanitize_prompt(text_prompt)
    prompt_val = sanitized.clean_text
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": f"<учебное_задание>\n{prompt_val}\n</учебное_задание>",
        }
    ]
    if image_bytes:
        b64 = encode_image_bytes(image_bytes)
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


async def _call_deepseek_api(messages: list[dict[str, Any]]) -> str:
    """Выполняет единичный асинхронный вызов OpenAI SDK для получения ответа DeepSeek."""
    client = get_deepseek_client()
    response = await client.chat.completions.create(
        model=config.DEEPSEEK_MODEL_NAME,
        messages=cast(Any, messages),
        temperature=0.0,
        timeout=config.DEEPSEEK_TIMEOUT_SECONDS,
    )
    if not response.choices:
        return "Пустой ответ модели."
    return response.choices[0].message.content or "Пустой ответ модели."


async def solve_homework(
    image_bytes: bytes | None = None,
    text_prompt: str | None = None,
) -> str:
    """Отправляет мультимодальный запрос в DeepSeek с защитой Circuit Breaker и retry backoff."""
    messages = build_deepseek_messages(image_bytes, text_prompt)
    await deepseek_circuit_breaker.check_permission()
    try:
        result = await async_retry_with_backoff(
            lambda: _call_deepseek_api(messages),
            max_retries=2,
            base_delay=1.0,
        )
        await deepseek_circuit_breaker.record_success()
        return result
    except Exception as e:
        await deepseek_circuit_breaker.record_failure(e)
        log.error(f"Ошибка при вызове DeepSeek API: {e}")
        raise
