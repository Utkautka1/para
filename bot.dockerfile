# syntax=docker/dockerfile:1
# Образ Telegram-бота (para-bot). Распознавание речи вынесено в сервис stt,
# поэтому здесь нет CUDA, faster-whisper и ffmpeg — образ ~0.5 ГБ вместо ~5.4 ГБ.
# Базовый образ закреплён по digest: тег 3.11-slim переписывается, а сборка должна быть воспроизводимой
FROM python:3.11-slim@sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

# Только версии из lock с проверкой sha256 (--require-hashes): подменённый пакет на PyPI не установится
COPY requirements.lock ./
# Кэш pip — это BuildKit cache mount, в слой образа он не попадает
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --require-hashes -r requirements.lock

COPY . ./
RUN mkdir -p /app/data /app/logs /app/stt_audio && chown -R appuser:appuser /app

USER appuser

CMD ["python", "bot.py"]
