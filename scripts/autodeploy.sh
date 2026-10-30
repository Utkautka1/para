#!/usr/bin/env bash
# ==============================================================================
# Автодеплой para после зелёного CI. Запускается на сервере systemd-таймером
# para-autodeploy.timer (scripts/systemd/) раз в 2 минуты.
#
# CI на GitHub после прохождения ВСЕХ джобов двигает ветку ci-passed на коммит
# (джоб deploy-gate). Этот скрипт только читает её через git ls-remote — GitHub
# не нужен доступ к серверу. Если ci-passed ушла вперёд, деплоит её через
# deploy_remote.sh и сообщает результат администратору в Telegram.
# ==============================================================================
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/para}"
DEPLOY_LOG="$PROJECT_DIR/logs/deploy.log"

log() { printf '[%s] [autodeploy] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$DEPLOY_LOG"; }

remote_ci_passed() {
  timeout 30 git ls-remote origin refs/heads/ci-passed | cut -f1
}

notify() {
  # Уведомление идёт через бота в контейнере worker; его сбой не должен ронять автодеплой
  docker exec para-worker python -m services.deploy_notifier "$@" >/dev/null 2>&1 \
    || log "⚠️  не удалось отправить уведомление в Telegram"
}

deploy() {
  local rev="$1" output
  log "ci-passed -> ${rev:0:7}, начинаем деплой"
  if output=$(DEPLOY_BRANCH=ci-passed bash scripts/deploy_remote.sh 2>&1); then
    printf '%s\n' "$output" >>"$DEPLOY_LOG"
    log "✅ ${rev:0:7} задеплоен"
    notify success "${rev:0:7}" "$(git log -1 --format=%s "$rev")"
  else
    printf '%s\n' "$output" >>"$DEPLOY_LOG"
    log "❌ деплой ${rev:0:7} упал"
    notify failure "${rev:0:7}" "$(tail -n 5 <<<"$output")"
    return 1
  fi
}

main() {
  cd "$PROJECT_DIR"
  local rev
  rev=$(remote_ci_passed) || { log "⚠️  GitHub недоступен (ls-remote)"; exit 0; }
  [[ -n "$rev" ]] || exit 0
  # Коммит уже в HEAD — тихо выходим, чтобы таймер не засорял лог каждые 2 минуты
  if git cat-file -e "$rev^{commit}" 2>/dev/null && git merge-base --is-ancestor "$rev" HEAD; then
    exit 0
  fi
  deploy "$rev"
}

main "$@"
