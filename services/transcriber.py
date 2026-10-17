"""
Сервис транскрибации речи на базе faster-whisper.

Использует модель large-v3-turbo на локальном GPU (NVIDIA Turing GTX 1660 Ti)
с автоматическим переходом на CPU при отсутствии CUDA.
Тяжёлые вычисления вынесены в отдельный поток через asyncio.to_thread,
чтобы не блокировать event loop бота.
"""

import asyncio
import os
from typing import Optional

from config import (
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_DOWNLOAD_ROOT,
    WHISPER_MODEL_NAME,
)
from core.logger import get_logger

log = get_logger("voice_transcriber")


class AudioTranscriber:
    """Сервис распознавания аудиофайлов с использованием faster-whisper."""

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
        download_root: str | None = None,
    ):
        # model_name — идентификатор модели (large-v3-turbo / base)
        # device — целевое устройство (cuda / cpu)
        # compute_type — точность вычислений (float16 / int8)
        # download_root — путь к директории хранения весов моделей
        self.model_name = model_name or WHISPER_MODEL_NAME
        self.device = device or WHISPER_DEVICE
        self.compute_type = compute_type or WHISPER_COMPUTE_TYPE
        self.download_root = download_root or WHISPER_DOWNLOAD_ROOT
        self._model = None
        self._lock = asyncio.Lock()



    def _init_whisper_engine(self):
        """Создает экземпляр WhisperModel с обработкой CUDA fallback."""
        from faster_whisper import WhisperModel
        os.makedirs(self.download_root, exist_ok=True)
        try:
            log.info(f"Загрузка модели STT: {self.model_name} на {self.device} ({self.compute_type})")
            return WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root=self.download_root,
            )
        except Exception as e:
            log.warning(f"⚠️ Сбой загрузки на {self.device}: {e}. Переключение на CPU (int8)")
            return WhisperModel(
                self.model_name,
                device="cpu",
                compute_type="int8",
                download_root=self.download_root,
            )

    async def get_model(self):
        """Ленивая асинхронно-безопасная инициализация модели Whisper."""
        if self._model is not None:
            return self._model
        async with self._lock:
            if self._model is None:
                self._model = await asyncio.to_thread(self._init_whisper_engine)
        return self._model

    def _sync_transcribe(self, model, audio_path: str, language: Optional[str] = None) -> str:
        """Синхронный прогон инференса faster-whisper в фоновом потоке."""
        segments, _ = model.transcribe(
            audio_path,
            language=language,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            beam_size=5,
        )
        return " ".join(seg.text.strip() for seg in segments if seg.text).strip()

    async def transcribe_file(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Асинхронно транскрибирует аудиофайл с помощью модели Whisper.

        :param audio_path: Путь к локальному аудиофайлу (.ogg, .mp4, .mp3, .wav)
        :param language: Языковой код (например, 'ru'), либо None для автоопределения
        :return: Распознанный текст или пустая строка
        """
        model = await self.get_model()
        return await asyncio.to_thread(self._sync_transcribe, model, audio_path, language)


def split_text_to_chunks(text: str, max_chunk_len: int = 4000) -> list[str]:
    """Разбивает длинный текст на части с учетом границ предложений."""
    if len(text) <= max_chunk_len:
        return [text]
    chunks, curr = [], ""
    for paragraph in text.split("\n"):
        if len(curr) + len(paragraph) + 1 <= max_chunk_len:
            curr = f"{curr}\n{paragraph}".strip()
        else:
            if curr:
                chunks.append(curr)
            curr = paragraph[:max_chunk_len]
    if curr:
        chunks.append(curr)
    return chunks


# Глобальный синглтон сервиса транскрибации
transcriber_service = AudioTranscriber()
