"""
Сервис транскрибации речи на базе faster-whisper.

Использует модель large-v3-turbo на локальном GPU (NVIDIA Turing GTX 1660 Ti)
с автоматическим переходом на CPU при отсутствии CUDA.
Тяжёлые вычисления вынесены в отдельный поток через asyncio.to_thread,
чтобы не блокировать event loop бота.
"""

import asyncio
import os
import time

from config import (
    WHISPER_BEAM_SIZE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_DOWNLOAD_ROOT,
    WHISPER_LANGUAGE,
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
        language: str | None = None,
        beam_size: int | None = None,
    ):
        # model_name — идентификатор модели (large-v3-turbo / base)
        # device — целевое устройство (cuda / cpu)
        # compute_type — точность вычислений (float16 / int8)
        # download_root — путь к директории хранения весов моделей
        self.model_name = model_name or WHISPER_MODEL_NAME
        self.device = device or WHISPER_DEVICE
        self.compute_type = compute_type or WHISPER_COMPUTE_TYPE
        self.download_root = download_root or WHISPER_DOWNLOAD_ROOT
        self.language = language or WHISPER_LANGUAGE
        self.beam_size = beam_size or WHISPER_BEAM_SIZE
        self._model = None
        self._cpu_model = None
        self._lock = asyncio.Lock()
        self._gpu_semaphore = asyncio.Semaphore(1)
        self._queue_count = 0

    @property
    def queue_size(self) -> int:
        """Возвращает число задач в очереди ожидания GPU."""
        return max(0, self._queue_count - 1)

    def _init_whisper_engine(self, device: str | None = None, compute_type: str | None = None):
        """Создает экземпляр WhisperModel с обработкой CUDA fallback."""
        from faster_whisper import WhisperModel  # type: ignore
        os.makedirs(self.download_root, exist_ok=True)
        dev = device or self.device
        comp = compute_type or self.compute_type
        try:
            log.info(f"Загрузка модели STT: {self.model_name} на {dev} ({comp})")
            return WhisperModel(
                self.model_name,
                device=dev,
                compute_type=comp,
                download_root=self.download_root,
            )
        except Exception as e:
            log.warning(f"⚠️ Сбой загрузки на {dev}: {e}. Переключение на CPU (int8)")
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

    async def _get_cpu_model(self):
        """Возвращает кэшированный экземпляр резервной CPU-модели Whisper."""
        if self._cpu_model is None:
            self._cpu_model = await asyncio.to_thread(self._init_whisper_engine, "cpu", "int8")
        return self._cpu_model

    async def warmup(self) -> None:
        """Прогревает модель Whisper в фоне, загружая веса в память GPU."""
        await self.get_model()

    @staticmethod
    def _clean_hallucinations(text: str) -> str:
        """Очищает стандартные артефакты Whisper на тишине или шуме."""
        raw = text.strip()
        lower = raw.lower().rstrip(".!?,")
        hallucinations = (
            "спасибо за просмотр",
            "продолжение следует",
            "субтитры сделал",
            "редактор субтитров",
            "до скорой встречи",
        )
        return "" if lower in hallucinations else raw

    def _sync_transcribe(self, model, audio_path: str, language: str | None = None) -> str:
        """Синхронный прогон инференса faster-whisper с подавлением галлюцинаций."""
        target_lang = language or self.language
        segments, _ = model.transcribe(
            audio_path,
            language=target_lang,
            beam_size=self.beam_size,
            condition_on_previous_text=False,
            no_speech_threshold=0.6,
        )
        raw_text = " ".join(seg.text.strip() for seg in segments if seg.text).strip()
        return self._clean_hallucinations(raw_text)

    async def _infer_with_fallback(self, audio_path: str, language: str | None) -> str:
        """Запускает инференс на GPU с автоматическим переходом на CPU при сбое."""
        fname = os.path.basename(audio_path)
        try:
            model = await self.get_model()
            return await asyncio.to_thread(self._sync_transcribe, model, audio_path, language)
        except Exception as e:
            log.warning(f"⚠️ Ошибка GPU инференса ({e}). Переход на CPU fallback: {fname}")
            cpu_model = await self._get_cpu_model()
            return await asyncio.to_thread(self._sync_transcribe, cpu_model, audio_path, language)

    async def transcribe_file(self, audio_path: str, language: str | None = None) -> str:
        """Асинхронно транскрибирует аудиофайл через семафор с замером времени и очереди."""
        self._queue_count += 1
        start_time = time.monotonic()
        fname = os.path.basename(audio_path)
        log.debug(f"Файл {fname} встал в очередь STT (ожидают в очереди: {self.queue_size})")
        try:
            async with self._gpu_semaphore:
                infer_start = time.monotonic()
                log.info(f"▶️ Начало STT инференса ({self.device}): {fname} (beam={self.beam_size})")
                text = await self._infer_with_fallback(audio_path, language)
                infer_time = time.monotonic() - infer_start
                total_time = time.monotonic() - start_time
                log.info(f"✅ STT инференс {fname} завершен: время={infer_time:.2f}с (всего={total_time:.2f}с, {len(text)} симв.)")
                return text
        finally:
            self._queue_count -= 1


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
