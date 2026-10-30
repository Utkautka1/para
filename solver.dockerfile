# Базовый образ закреплён по digest: тег 3.11-slim переписывается, а сборка должна быть воспроизводимой
FROM python:3.11-slim@sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/sh -m appuser

# Только версии из lock с проверкой sha256 (--require-hashes): подменённый пакет на PyPI не установится
COPY requirements.lock .
RUN pip install --no-cache-dir --require-hashes -r requirements.lock && \
    rm -rf /root/.cache/pip

COPY . .
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app

USER appuser

CMD ["python", "solver.py"]
