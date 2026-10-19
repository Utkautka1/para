"""
Модульные тесты для сервиса и хэндлеров распознавания речи (Voice & Video note).

Проверяет фильтрацию чатов, извлечение метаданных, форматирование шаблонов,
деление длинных текстов на части, логику работы пайплайна и fallback транскрибера.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Chat, Message, User, VideoNote, Voice

from bot.handlers.user.voice_transcribe import (
    cleanup_temp_file,
    deliver_transcription,
    extract_audio_meta,
    handle_voice_or_video_note,
    is_allowed_chat,
    process_audio_pipeline,
    send_overflow_chunks,
)
from bot.templates.user.voice import (
    format_duration_str,
    format_transcription_empty,
    format_transcription_error,
    format_transcription_result,
    format_transcription_status,
)
from config import TOPIC_CHAT_ID
from services.transcriber import AudioTranscriber, split_text_to_chunks


def test_is_allowed_chat() -> None:
    """Проверяет допуск сообщений только из целевой группы или ЛС."""
    assert is_allowed_chat(TOPIC_CHAT_ID, "supergroup") is True
    assert is_allowed_chat(12345, "private") is True
    assert is_allowed_chat(-999, "group") is False
    assert is_allowed_chat(-10088888, "supergroup") is False


def test_format_duration_str() -> None:
    """Проверяет корректное форматирование длительности секунд."""
    assert format_duration_str(0) == ""
    assert format_duration_str(-5) == ""
    assert format_duration_str(15) == " (0:15)"
    assert format_duration_str(65) == " (1:05)"


def test_format_transcription_result() -> None:
    """Проверяет экранирование HTML и сборку готового сообщения."""
    res = format_transcription_result("<Иван & Co>", 15, "Привет <b>мир</b>")
    assert "&lt;Иван &amp; Co&gt;" in res
    assert "Привет &lt;b&gt;мир&lt;/b&gt;" in res
    assert "(0:15)" in res
    assert "«" in res and "»" in res


def test_format_templates_status_and_empty() -> None:
    """Проверяет шаблоны статуса, пустой записи и ошибки."""
    assert "Расшифровываю" in format_transcription_status()
    assert "не удалось разобрать" in format_transcription_empty("Иван", 10)
    assert "Не удалось расшифровать" in format_transcription_error()


def test_split_text_to_chunks_short() -> None:
    """Проверяет отсутствие разбивки для короткого текста."""
    text = "Короткое сообщение"
    chunks = split_text_to_chunks(text, max_chunk_len=100)
    assert chunks == [text]


def test_split_text_to_chunks_long() -> None:
    """Проверяет корректное разбиение длинного многострочного текста."""
    p1 = "А" * 60
    p2 = "Б" * 60
    text = f"{p1}\n{p2}"
    chunks = split_text_to_chunks(text, max_chunk_len=70)
    assert len(chunks) == 2
    assert chunks[0] == p1
    assert chunks[1] == p2


def test_extract_audio_meta_voice() -> None:
    """Проверяет извлечение метаданных из голосового сообщения."""
    msg = MagicMock(spec=Message)
    msg.from_user = User(id=1, is_bot=False, first_name="Тест")
    msg.voice = Voice(file_id="voice_123", file_unique_id="u1", duration=25)
    msg.video_note = None
    file_id, dur, sender = extract_audio_meta(msg)
    assert file_id == "voice_123"
    assert dur == 25
    assert sender == "Тест"


def test_extract_audio_meta_video_note() -> None:
    """Проверяет извлечение метаданных из видео-кружочка."""
    msg = MagicMock(spec=Message)
    msg.from_user = User(id=2, is_bot=False, first_name="Круг")
    msg.voice = None
    msg.video_note = VideoNote(file_id="vid_456", file_unique_id="u2", length=240, duration=18)
    file_id, dur, sender = extract_audio_meta(msg)
    assert file_id == "vid_456"
    assert dur == 18
    assert sender == "Круг"


def test_cleanup_temp_file(tmp_path) -> None:
    """Проверяет удаление временного файла и безопасность при отсутствии."""
    p = tmp_path / "test.ogg"
    p.write_text("audio")
    cleanup_temp_file(str(p))
    assert not os.path.exists(str(p))
    cleanup_temp_file(str(p))


@pytest.mark.asyncio
async def test_deliver_transcription_empty() -> None:
    """Проверяет отправку сообщения о неразборчивой речи."""
    msg = MagicMock(spec=Message)
    status_msg = MagicMock(spec=Message)
    status_msg.edit_text = AsyncMock()
    await deliver_transcription(msg, status_msg, "Анна", 10, "")
    status_msg.edit_text.assert_awaited_once()
    assert "не удалось разобрать" in status_msg.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_deliver_transcription_success() -> None:
    """Проверяет редактирование статусного сообщения на распознанный текст."""
    msg = MagicMock(spec=Message)
    msg.message_thread_id = 405
    status_msg = MagicMock(spec=Message)
    status_msg.edit_text = AsyncMock()
    await deliver_transcription(msg, status_msg, "Анна", 15, "Привет всем!")
    status_msg.edit_text.assert_awaited_once()
    assert "Привет всем!" in status_msg.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_send_overflow_chunks() -> None:
    """Проверяет отправку дополнительных частей текста в нужный топик."""
    msg = MagicMock(spec=Message)
    msg.message_thread_id = 777
    msg.reply = AsyncMock()
    await send_overflow_chunks(msg, ["кусок 1", "кусок 2"])
    assert msg.reply.await_count == 2
    msg.reply.assert_any_await("«кусок 1»")
    msg.reply.assert_any_await("«кусок 2»")


@pytest.mark.asyncio
async def test_process_audio_pipeline_success() -> None:
    """Проверяет успешный цикл скачивания, транскрибации и очистки."""
    msg = MagicMock(spec=Message)
    status_msg = MagicMock(spec=Message)
    status_msg.edit_text = AsyncMock()
    with (
        patch("bot.handlers.user.voice_transcribe.download_temp_audio", new=AsyncMock(return_value="/tmp/fake.ogg")),
        patch(
            "bot.handlers.user.voice_transcribe.transcriber_service.transcribe_file",
            new=AsyncMock(return_value="Текст"),
        ),
        patch("bot.handlers.user.voice_transcribe.cleanup_temp_file") as mock_clean,
    ):
        await process_audio_pipeline("f1", "Иван", 10, msg, status_msg)
        mock_clean.assert_called_once_with("/tmp/fake.ogg")
        status_msg.edit_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_audio_pipeline_error() -> None:
    """Проверяет вывод ошибки и обязательную очистку при сбое."""
    msg = MagicMock(spec=Message)
    status_msg = MagicMock(spec=Message)
    status_msg.edit_text = AsyncMock()
    with (
        patch(
            "bot.handlers.user.voice_transcribe.download_temp_audio",
            new=AsyncMock(side_effect=RuntimeError("Download err")),
        ),
        patch("bot.handlers.user.voice_transcribe.cleanup_temp_file") as mock_clean,
    ):
        await process_audio_pipeline("f2", "Иван", 10, msg, status_msg)
        mock_clean.assert_called_once_with("")
        status_msg.edit_text.assert_awaited_once()
        assert "Не удалось" in status_msg.edit_text.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_voice_or_video_note_wrong_chat() -> None:
    """Проверяет игнорирование сообщений из посторонних групп."""
    msg = MagicMock(spec=Message)
    msg.chat = Chat(id=-99999, type="group")
    with patch("bot.handlers.user.voice_transcribe.process_audio_pipeline") as mock_pipe:
        await handle_voice_or_video_note(msg)
        mock_pipe.assert_not_called()


@pytest.mark.asyncio
async def test_handle_voice_or_video_note_success() -> None:
    """Проверяет реакцию бота в целевом топике с отправкой статуса."""
    msg = MagicMock(spec=Message)
    msg.chat = Chat(id=TOPIC_CHAT_ID, type="supergroup")
    msg.message_thread_id = 555
    msg.from_user = User(id=10, is_bot=False, first_name="Петр")
    msg.voice = Voice(file_id="v_ok", file_unique_id="u_ok", duration=12)
    msg.video_note = None
    status_mock = MagicMock(spec=Message)
    msg.reply = AsyncMock(return_value=status_mock)

    with patch("bot.handlers.user.voice_transcribe.process_audio_pipeline") as mock_pipe:
        await handle_voice_or_video_note(msg)
        msg.reply.assert_awaited_once_with(format_transcription_status())
        mock_pipe.assert_awaited_once_with("v_ok", "Петр", 12, msg, status_mock, 10)


@pytest.mark.asyncio
async def test_handle_voice_too_long() -> None:
    """Проверяет отклонение слишком длинного аудиосообщения."""
    msg = MagicMock(spec=Message)
    msg.chat = Chat(id=TOPIC_CHAT_ID, type="supergroup")
    msg.from_user = User(id=11, is_bot=False, first_name="Долгий")
    msg.voice = Voice(file_id="v_long", file_unique_id="u_long", duration=301)
    msg.video_note = None
    msg.reply = AsyncMock()

    with patch("bot.handlers.user.voice_transcribe.process_audio_pipeline") as mock_pipe:
        await handle_voice_or_video_note(msg)
        mock_pipe.assert_not_called()
        msg.reply.assert_awaited_once()
        assert "слишком длинное" in msg.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_voice_rate_limit() -> None:
    """Проверяет срабатывание троттлинга при флуде аудио от одного пользователя."""
    from bot.handlers.user.voice_transcribe import _USER_IN_FLIGHT

    _USER_IN_FLIGHT[99] = 2  # лимит исчерпан
    msg = MagicMock(spec=Message)
    msg.chat = Chat(id=TOPIC_CHAT_ID, type="supergroup")
    msg.from_user = User(id=99, is_bot=False, first_name="Флудер")
    msg.voice = Voice(file_id="v_spam", file_unique_id="u_spam", duration=5)
    msg.video_note = None
    msg.reply = AsyncMock()

    with patch("bot.handlers.user.voice_transcribe.process_audio_pipeline") as mock_pipe:
        await handle_voice_or_video_note(msg)
        mock_pipe.assert_not_called()
        assert "предыдущее аудиосообщение" in msg.reply.call_args[0][0]
    _USER_IN_FLIGHT.pop(99, None)


@pytest.mark.asyncio
async def test_send_overflow_chunks_html_escaping() -> None:
    """Проверяет обязательное экранирование HTML-тегов в оверфлоу чанках."""
    msg = MagicMock(spec=Message)
    msg.reply = AsyncMock()
    await send_overflow_chunks(msg, ["<script>alert(1)</script> & Co"])
    msg.reply.assert_awaited_once_with("«&lt;script&gt;alert(1)&lt;/script&gt; &amp; Co»")


@pytest.mark.asyncio
async def test_multi_user_concurrent_transcriptions() -> None:
    """Проверяет параллельную обработку 5 пользователей без блокировок и утечек."""
    import asyncio

    tr = AudioTranscriber()
    mock_engine = MagicMock()
    mock_engine.transcribe.return_value = ([MagicMock(text="Привет")], None)
    tr._model = mock_engine

    tasks = [tr.transcribe_file(f"/tmp/user_{i}.ogg") for i in range(5)]
    results = await asyncio.gather(*tasks)
    assert len(results) == 5
    assert all(r == "Привет" for r in results)
    assert tr.queue_size == 0


def test_transcriber_cpu_fallback() -> None:
    """Проверяет переключение на CPU при ошибке инициализации CUDA."""
    tr = AudioTranscriber(device="cuda_fake")
    mock_model = MagicMock()
    mock_module = MagicMock()
    mock_module.WhisperModel = MagicMock(side_effect=[Exception("CUDA error"), mock_model])
    with patch.dict(sys.modules, {"faster_whisper": mock_module}):
        engine = tr._init_whisper_engine()
        assert engine == mock_model


@pytest.mark.asyncio
async def test_transcriber_service_transcribe_file() -> None:
    """Проверяет корректное склеивание распознанных сегментов речи."""
    tr = AudioTranscriber()
    mock_seg1 = MagicMock(text=" Привет ")
    mock_seg2 = MagicMock(text=" мир! ")
    mock_engine = MagicMock()
    mock_engine.transcribe.return_value = ([mock_seg1, mock_seg2], None)
    tr._model = mock_engine

    res = await tr.transcribe_file("/tmp/fake_test.ogg")
    assert res == "Привет мир!"


@pytest.mark.asyncio
async def test_transcriber_runtime_fallback_to_cpu() -> None:
    """Проверяет переключение на CPU модель при runtime ошибке GPU инференса."""
    tr = AudioTranscriber()
    gpu_engine = MagicMock()
    gpu_engine.transcribe.side_effect = RuntimeError("CUDA out of memory")
    cpu_engine = MagicMock()
    cpu_seg = MagicMock(text="Спасенный текст")
    cpu_engine.transcribe.return_value = ([cpu_seg], None)
    tr._model = gpu_engine
    tr._get_cpu_model = AsyncMock(return_value=cpu_engine)

    res = await tr.transcribe_file("/tmp/audio.ogg")
    assert res == "Спасенный текст"
    tr._get_cpu_model.assert_awaited_once()


def test_transcriber_anti_hallucination_params() -> None:
    """Проверяет передачу параметров против галлюцинаций в transcribe."""
    tr = AudioTranscriber(language="ru", beam_size=1)
    mock_engine = MagicMock()
    mock_engine.transcribe.return_value = ([], None)
    tr._sync_transcribe(mock_engine, "/tmp/scream.ogg")
    call_kwargs = mock_engine.transcribe.call_args[1]
    assert call_kwargs["language"] == "ru"
    assert call_kwargs["beam_size"] == 1
    assert call_kwargs["condition_on_previous_text"] is False
    assert call_kwargs["no_speech_threshold"] == 0.6


def test_transcriber_clean_hallucinations() -> None:
    """Проверяет фильтрацию типовых галлюцинаций Whisper на тишине."""
    assert AudioTranscriber._clean_hallucinations("Спасибо за просмотр!") == ""
    assert AudioTranscriber._clean_hallucinations("Продолжение следует...") == ""
    assert AudioTranscriber._clean_hallucinations("Привет, это пара!") == "Привет, это пара!"
