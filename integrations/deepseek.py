"""
Интеграция с нейросетевым API DeepSeek (модели Vision/Flash).

Отвечает за подготовку промптов по ГОСТ 7.32-2017, кодирование изображений
в Base64 и выполнение асинхронных запросов на решение задач.
"""

import base64

from openai import AsyncOpenAI

import config
from core.logger import get_logger

log = get_logger("deepseek")
_deepseek_client: AsyncOpenAI | None = None

SYSTEM_PROMPT = config.DEEPSEEK_SYSTEM_PROMPT


def get_deepseek_client() -> AsyncOpenAI:
    """
    Предоставляет синглтон асинхронного клиента для взаимодействия с API DeepSeek.

    Инициализирует клиент OpenAI SDK с переопределенным base_url и системным ключом,
    переиспользуя постоянный пул соединений между вызовами.

    Возвращает настроенный экземпляр openai.AsyncOpenAI.
    """
    global _deepseek_client
    if _deepseek_client is None:
        _deepseek_client = AsyncOpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_API_BASE,
        )
    return _deepseek_client


async def close_deepseek_client() -> None:
    """
    Корректно закрывает сетевую сессию и пул соединений клиента DeepSeek.

    Предотвращает предупреждения unclosed client session при завершении процессов
    воркера и решателя задач.

    Не возвращает значений; сбрасывает ссылку на клиент в None.
    """
    global _deepseek_client
    if _deepseek_client is not None:
        await _deepseek_client.close()
        _deepseek_client = None


def encode_image_bytes(image_bytes: bytes) -> str:
    """
    Кодирует сырые байты изображения задания в строку формата Base64.

    Необходима для передачи графических условий задач в мультимодальное API
    нейросети через Data URL без сохранения файлов на публичных хостингах.

    Возвращает текстовую строку в кодировке Base64 UTF-8.
    """
    return base64.b64encode(image_bytes).decode("utf-8")


def build_deepseek_messages(
    image_bytes: bytes | None,
    text_prompt: str | None,
) -> list[dict]:
    """
    Формирует изолированный массив контекстных сообщений для API нейросети.

    Изолирует пользовательский промпт в защитные XML-теги <учебное_задание>
    для предотвращения атак prompt injection и подмешивает системный ГОСТ-промпт.

    Возвращает список словарей формата сообщений OpenAI Chat Completions.
    """
    prompt_val = text_prompt or "Реши все задания с листа."
    content: list[dict] = [
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


async def solve_homework(
    image_bytes: bytes | None = None,
    text_prompt: str | None = None,
) -> str:
    """
    Отправляет мультимодальный запрос в нейросеть DeepSeek и возвращает готовое решение.

    Применяет детерминированную температуру 0.0 и настраиваемый таймаут
    для гарантированного получения академически точного оформления по ГОСТ.

    Возвращает строку с полным текстом решения или выбрасывает исключение.
    """
    messages = build_deepseek_messages(image_bytes, text_prompt)
    try:
        client = get_deepseek_client()
        response = await client.chat.completions.create(
            model=config.DEEPSEEK_MODEL_NAME,
            messages=messages,
            temperature=0.0,
            timeout=config.DEEPSEEK_TIMEOUT_SECONDS,
        )
        if not response.choices:
            return "Пустой ответ модели."
        return response.choices[0].message.content or "Пустой ответ модели."
    except Exception as e:
        log.error(f"Ошибка при вызове DeepSeek API: {e}")
        raise
