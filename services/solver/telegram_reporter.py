"""
Модуль доставки готовых решений и уведомлений в Telegram.

Формирует посты с решениями ДЗ по ГОСТ, создает ссылки на
оригинальные сообщения и отправляет уведомления о сбоях обработки.
"""

from aiogram import Bot
from aiogram.types import FSInputFile

import config
from core.logger import get_logger

log = get_logger("solver_reporter")


def build_post_link(chat_id: int, message_id: int) -> str:
    """
    Формирует прямую t.me-ссылку на оригинальное сообщение задания в Telegram.

    Очищает префикс супергруппы '-100' для построения валидного deep-link URL.
    Позволяет студентам в топике готовых решений перейти к исходному вопросу.

    Возвращает строку постоянной ссылки вида https://t.me/c/...
    """
    clean_id = str(chat_id).replace("-100", "")
    return f"https://t.me/c/{clean_id}/{message_id}"


async def send_solution_to_telegram(tg_bot: Bot, task: dict, doc_path: str) -> None:
    """
    Отправляет готовый .docx файл решения в топик готовых ДЗ.

    Формирует кликабельную подпись со ссылкой на исходное задание в группе.
    Публикует документ по ГОСТ в целевой топик готовых домашних заданий.

    Ничего не возвращает.
    """
    chat_id = task.get("chat_id", config.TOPIC_CHAT_ID)
    msg_id = task.get("message_id", 0)
    caption = f"✅ <b>Готовое решение ДЗ</b>\n\n📌 Ссылка на задание: {build_post_link(chat_id, msg_id)}"
    doc_file = FSInputFile(doc_path, filename=f"Решение_ДЗ_{msg_id}.docx")

    await tg_bot.send_document(
        chat_id=config.TOPIC_CHAT_ID,
        message_thread_id=config.HW_OUTPUT_TOPIC_THREAD_ID,
        document=doc_file,
        caption=caption,
        parse_mode="HTML",
    )


async def notify_task_error(tg_bot: Bot, task: dict) -> None:
    """
    Отправляет уведомление об ошибке решения в чат или топик пользователя.

    Срабатывает при исчерпании лимита повторных попыток обработки задания.
    Информирует студента о необходимости перепроверить читаемость файла.

    Ничего не возвращает.
    """
    try:
        await tg_bot.send_message(
            chat_id=task.get("chat_id"),
            text="⚠️ <b>Не удалось решить ДЗ.</b>\nПроверьте читаемость файла или повторите позже.",
            reply_to_message_id=task.get("message_id"),
            message_thread_id=task.get("message_thread_id"),
        )
    except Exception as e:
        log.debug(f"Не удалось отправить уведомление об ошибке: {e}")
