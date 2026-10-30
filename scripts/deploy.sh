#!/usr/bin/env bash
# ==============================================================================
# Деплой para на сервер одной командой: scripts/deploy.sh
#
# 1. Проверяет, что локальный main запушен (деплоится только origin/main)
# 2. Выполняет scripts/deploy_remote.sh на сервере (через stdin, с таймаутом)
# 3. Снаружи проверяет публичный /health через шлюз claude
#
# DEPLOY_HOST — ssh-хост сервера. По умолчанию home-tunnel: он работает через
# обратный туннель на claude и не зависит от Tailscale, NAT и смены IP дома.
# ==============================================================================
set -euo pipefail

DEPLOY_HOST="${DEPLOY_HOST:-home-tunnel}"
PUBLIC_HEALTH_URL="${PUBLIC_HEALTH_URL:-https://185-121-12-109.sslip.io/health}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { printf '[deploy] %s\n' "$*"; }
fail() { printf '[deploy] ❌ %s\n' "$*" >&2; exit 1; }

check_pushed() {
  # Сервер берёт код из origin/main: незапушенные коммиты на него не попадут
  timeout 30 git fetch -q origin main || fail "git fetch не уложился в 30 сек"
  [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] \
    || fail "локальный HEAD не совпадает с origin/main — сначала git push"
}

run_remote() {
  log "деплой на $DEPLOY_HOST ($(git rev-parse --short HEAD))"
  # ServerAliveInterval — обрыв туннеля даёт ошибку через ~45 сек, а не вечное ожидание
  timeout 1200 ssh -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=15 \
    "$DEPLOY_HOST" bash -s < "$SCRIPT_DIR/deploy_remote.sh"
}

check_public() {
  curl -fsS -m 15 "$PUBLIC_HEALTH_URL" >/dev/null || fail "публичный $PUBLIC_HEALTH_URL не отвечает"
  log "✅ публичный /health OK"
}

main() {
  cd "$SCRIPT_DIR/.."
  check_pushed
  run_remote
  check_public
}

main "$@"
