"""
Шаблоны сообщений для расшифровки голосовых и видеосообщений в Telegram.

Формирует аккуратные HTML-сообщения со статусом распознавания,
экранированием имени автора и цитатой расшифрованного текста,
а также сообщениями об ошибках и пустых аудиозаписях.
"""

import html


def format_transcription_status() -> str:
    """Возвращает текст временного статуса распознавания речи."""
    return "🎙 <i>Расшифровываю аудиосообщение...</i>"


def format_duration_str(duration_seconds: int) -> str:
    """
    Форматирует длительность в формат М:СС.

    :param duration_seconds: Длительность в секундах
    :return: Строка вида (0:15) или пустая строка если 0
    """
    if duration_seconds <= 0:
        return ""
    mins = duration_seconds // 60
    secs = duration_seconds % 60
    return f" ({mins}:{secs:02d})"


def format_transcription_result(
    sender_name: str,
    duration_sec: int,
    transcription_text: str
) -> str:
    """
    Формирует итоговое сообщение с расшифровкой аудиосообщения.

    :param sender_name: Имя автора аудиосообщения
    :param duration_sec: Длительность аудиозаписи в секундах
    :param transcription_text: Распознанный текст
    :return: Отформатированное HTML-сообщение
    """
    safe_name = html.escape(sender_name)
    safe_text = html.escape(transcription_text.strip())
    dur_str = format_duration_str(duration_sec)
    return (
        f"🗣 <b>{safe_name}</b>{dur_str}:\n\n"
        f"«{safe_text}»"
    )


def format_transcription_empty(sender_name: str, duration_sec: int) -> str:
    """Возвращает уведомление о неразборчивой или пустой записи."""
    safe_name = html.escape(sender_name)
    dur_str = format_duration_str(duration_sec)
    return (
        f"🗣 <b>{safe_name}</b>{dur_str}:\n\n"
        f"<i>(В аудиозаписи не удалось разобрать речь)</i>"
    )


def format_transcription_error() -> str:
    """Возвращает сообщение о техническом сбое при обработке аудио."""
    return "⚠️ <i>Не удалось расшифровать аудиосообщение. Попробуйте позже.</i>"


def format_too_long_error(max_seconds: int = 300) -> str:
    """Возвращает предупреждение о превышении максимальной длительности аудио."""
    mins = max_seconds // 60
    return f"⚠️ <i>Аудиосообщение слишком длинное (максимум {mins} мин).</i>"


def format_too_big_error(max_mb: int = 20) -> str:
    """Возвращает предупреждение о превышении максимального размера файла."""
    return f"⚠️ <i>Аудиофайл слишком большой (максимум {max_mb} МБ).</i>"


def format_rate_limit_error() -> str:
    """Возвращает уведомление о защите от частого флуда аудиосообщениями."""
    return "⏳ <i>Подождите, ваше предыдущее аудиосообщение ещё обрабатывается.</i>"


def format_queue_status(queue_pos: int) -> str:
    """Возвращает текст статуса нахождения аудиосообщения в очереди GPU."""
    return f"🎙 <i>В очереди на расшифровку (позиция: {queue_pos})...</i>"
