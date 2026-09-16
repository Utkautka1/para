"""
Сервис обращения к DeepSeek Vision API для авторешения ДЗ.

Отправляет изображение/текст в режиме без сохранения контекста (stateless)
и с отключенным мышлением/думающим режимом.
"""

import base64
from typing import List, Optional
from openai import AsyncOpenAI
import config
from core.logger import get_logger

log = get_logger("deepseek_solver")

client = AsyncOpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_API_BASE
)

SYSTEM_PROMPT = (
    "Ты — профессиональный преподаватель высшей математики и точных наук. "
    "Твоя задача — внимательно распознать текст/файлы и задания с картинки или документа "
    "и написать идеальный отчет по ГОСТ 7.32-2017. "
    "СТРОГО СТРУКТУРИРУЙ ответ по разделам с помощью Markdown заголовков первой категории '# ':\n"
    "# ВВЕДЕНИЕ (краткая постановка задачи и цели)\n"
    "# РЕШЕНИЕ ЗАДАНИЯ (пошаговые рассуждения, вычисления, подзаголовки '## ')\n"
    "# ЗАКЛЮЧЕНИЕ (итоги и финальная сводка ответов)\n"
    "СТРОГО УЧИТЫВАЙ инструкции пользователя (например: 'реши только номер 2', 'вариант 3'). "
    "Форматируй математику наглядно без сложного LaTeX-кода, используй символы (Δ, ·, ║) и таблицы."
)


def encode_image_bytes(image_bytes: bytes) -> str:
    """
    Кодирует байты изображения в Base64 формат.

    :param image_bytes: Исходные байты изображения
    :return: Base64 строка
    """
    return base64.b64encode(image_bytes).decode('utf-8')


def build_deepseek_messages(image_bytes: Optional[bytes], text_prompt: Optional[str]) -> List[dict]:
    """
    Формирует список сообщений для отправки в DeepSeek API.
    """
    content: List[dict] = [{"type": "text", "text": text_prompt or "Реши все задания с листа."}]
    if image_bytes:
        b64 = encode_image_bytes(image_bytes)
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}]


async def solve_homework(image_bytes: Optional[bytes] = None, text_prompt: Optional[str] = None) -> str:
    """
    Вызывает DeepSeek Vision API для решения ДЗ без контекста.
    """
    log.info("Отправка запроса на авторешение в DeepSeek Vision API...")
    messages = build_deepseek_messages(image_bytes, text_prompt)
    try:
        response = await client.chat.completions.create(
            model=config.DEEPSEEK_MODEL_NAME,
            messages=messages,
            temperature=0.0
        )
        log.info("Решение от DeepSeek успешно получено!")
        return response.choices[0].message.content or "Не удалось получить ответ от модели."
    except Exception as e:
        log.error(f"Ошибка при вызове DeepSeek API: {e}")
        raise e
