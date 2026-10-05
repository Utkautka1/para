"""
Интеграция с DeepSeek API для распознавания заданий и генерации решений.
"""
import base64
from typing import List, Optional

from openai import AsyncOpenAI

import config
from core.logger import get_logger

log = get_logger("deepseek")

SYSTEM_PROMPT = (
    "Ты — преподаватель высшей математики и точных наук. "
    "Внимательно распознай задания с картинки или текста "
    "и напиши решение в виде отчета по ГОСТ 7.32-2017. "
    "Структурируй ответ с помощью заголовков первого уровня '# ':\n"
    "# ВВЕДЕНИЕ\n"
    "# РЕШЕНИЕ ЗАДАНИЯ\n"
    "# ЗАКЛЮЧЕНИЕ\n"
    "Учитывай указания студента (номер варианта, конкретные номера). "
    "Форматируй математику наглядно без сложного LaTeX, используй символы (Δ, ·, ║) и таблицы."
)


def encode_image_bytes(image_bytes: bytes) -> str:
    """Кодирует байты изображения в Base64."""
    return base64.b64encode(image_bytes).decode("utf-8")


def build_deepseek_messages(
    image_bytes: Optional[bytes],
    text_prompt: Optional[str]
) -> List[dict]:
    """Формирует список сообщений для отправки в DeepSeek API."""
    content: List[dict] = [{
        "type": "text",
        "text": text_prompt or "Реши все задания с листа."
    }]
    if image_bytes:
        b64 = encode_image_bytes(image_bytes)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content}
    ]


async def solve_homework(
    image_bytes: Optional[bytes] = None,
    text_prompt: Optional[str] = None
) -> str:
    """Отправляет запрос в DeepSeek API и возвращает текст решения."""
    messages = build_deepseek_messages(image_bytes, text_prompt)
    try:
        client = AsyncOpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_API_BASE
        )
        response = await client.chat.completions.create(
            model=config.DEEPSEEK_MODEL_NAME,
            messages=messages,
            temperature=0.0
        )
        return response.choices[0].message.content or "Пустой ответ модели."
    except Exception as e:
        log.error(f"Ошибка при вызове DeepSeek API: {e}")
        raise
