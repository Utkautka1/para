# syntax=docker/dockerfile:1
# Образ сервиса распознавания речи (para-stt): faster-whisper + CUDA-библиотеки.
# Единственный образ проекта с GPU — бот и остальные сервисы остаются лёгкими.
# Базовый образ закреплён по digest: тег 3.11-slim переписывается, а сборка должна быть воспроизводимой
FROM python:3.11-slim@sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.11/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH}"

WORKDIR /app

# ffmpeg берём из репозитория базового образа (закреплён по digest), отдельный пин версии не нужен
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

# Слой 1: все зависимости, включая CUDA-библиотеки, из requirements-stt.lock
# (requirements.txt + requirements-bot.txt). Кэш pip переживает пересборки.
# Только версии из lock с проверкой sha256 (--require-hashes): подменённый пакет на PyPI не установится
COPY requirements-stt.lock ./
# Кэш pip — это BuildKit cache mount, в слой образа он не попадает
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --require-hashes -r requirements-stt.lock

# Слой 2: Код приложения (собирается за 0.3s)
COPY . ./
RUN mkdir -p /app/data /app/logs /app/stt_audio && chown -R appuser:appuser /app

USER appuser

CMD ["python", "stt.py"]
