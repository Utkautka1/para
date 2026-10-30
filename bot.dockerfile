# syntax=docker/dockerfile:1
# Образ Telegram-бота (para-bot). Распознавание речи вынесено в сервис stt,
# поэтому здесь нет CUDA, faster-whisper и ffmpeg — образ ~0.5 ГБ вместо ~5.4 ГБ.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . ./
RUN mkdir -p /app/data /app/logs /app/stt_audio && chown -R appuser:appuser /app

USER appuser

CMD ["python", "bot.py"]
