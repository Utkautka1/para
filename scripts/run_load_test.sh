#!/usr/bin/env bash
# ==============================================================================
# Скрипт автоматического запуска стресс-тестирования 500+ RPS (Locust)
# ==============================================================================
set -euo pipefail

HOST="${1:-http://127.0.0.1:8000}"
USERS="${2:-80}"
SPAWN_RATE="${3:-20}"
DURATION="${4:-25s}"
REPORT_DIR="docs/reports/load_test"

mkdir -p "${REPORT_DIR}"

echo "=================================================================="
echo "🚀 Запуск стресс-тестирования Para API & gRPC (Цель: 500 RPS)"
echo "   Хост:          ${HOST}"
echo "   Пользователи:  ${USERS}"
echo "   Скорость спавна: ${SPAWN_RATE}/сек"
echo "   Длительность:  ${DURATION}"
echo "   Отчеты:        ${REPORT_DIR}"
echo "=================================================================="

PYTHON_BIN="./venv/bin/python3"
if [ ! -f "${PYTHON_BIN}" ]; then
    PYTHON_BIN="python3"
fi

${PYTHON_BIN} -m locust \
    -f tests/load/locustfile.py \
    --headless \
    --host="${HOST}" \
    --users="${USERS}" \
    --spawn-rate="${SPAWN_RATE}" \
    --run-time="${DURATION}" \
    --csv="${REPORT_DIR}/benchmark" \
    --html="${REPORT_DIR}/benchmark.html"

echo "=================================================================="
echo "✅ Нагрузочный стресс-тест успешно завершен!"
echo "   HTML отчет: ${REPORT_DIR}/benchmark.html"
echo "   CSV данные: ${REPORT_DIR}/benchmark_stats.csv"
echo "=================================================================="
