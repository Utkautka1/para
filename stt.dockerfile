# syntax=docker/dockerfile:1
# Образ сервиса распознавания речи (para-stt): faster-whisper + CUDA-библиотеки.
# Единственный образ проекта с GPU — бот и остальные сервисы остаются лёгкими.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.11/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

# Слой 1: Тяжелые CUDA-библиотеки (кэшируются намертво, 0.0s при правках кода)
COPY requirements-bot.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements-bot.txt

# Слой 2: Легкие Python-зависимости бота
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Слой 3: Код приложения (собирается за 0.3s)
COPY . ./
RUN mkdir -p /app/data /app/logs /app/stt_audio && chown -R appuser:appuser /app

USER appuser

CMD ["python", "stt.py"]
