#!/usr/bin/env bash
# ==============================================================================
# Серверная часть деплоя para. Не запускается вручную: scripts/deploy.sh передаёт
# этот файл на сервер через stdin (`ssh HOST bash -s`), чтобы удалённый shell
# не разбирал команды из аргументов.
#
# Также вызывается scripts/autodeploy.sh по таймеру с DEPLOY_BRANCH=ci-passed.
#
# Шаги:
#   1. fetch + ff-only merge origin/$DEPLOY_BRANCH с таймаутами (сегодняшний зависший pull);
#      перед merge — коммит есть в main и все новые коммиты подписаны доверенным ключом
#   2. по списку изменённых файлов выбирает сервисы, чей код смонтирован
#      (из `docker compose config`, а не из ручного списка)
#   3. пересобирает образы только при смене requirements/Dockerfile,
#      пересоздаёт всё при смене compose.yml, иначе — restart затронутых
#   4. ждёт healthcheck, проверяет /health, перезапуски и новые ERROR в логах
# ==============================================================================
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/para}"
# Ветка, из которой деплоим: main — ручной деплой, ci-passed — автодеплой после зелёного CI
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
# Общая блокировка: ручной деплой и таймер не должны перезапускать сервисы одновременно
LOCK_FILE="${LOCK_FILE:-/run/lock/para-deploy.lock}"
# Сколько секунд после старта наблюдать за перезапусками и ошибками
OBSERVE_SECONDS="${OBSERVE_SECONDS:-30}"
# Ключи, чьей подписи коммитов доверяем (формат git allowed_signers). Лежит вне рабочей копии,
# владелец root: иначе подменённый коммит мог бы сам добавить свой ключ
ALLOWED_SIGNERS="${ALLOWED_SIGNERS:-/etc/para/allowed_signers}"

log() { printf '[deploy] %s\n' "$*"; }
fail() { printf '[deploy] ❌ %s\n' "$*" >&2; exit 1; }

verify_trusted_range() {
  # Защита от подмены ветки ci-passed: деплоим только коммиты из main, подписанные доверенным ключом.
  # Проверяем весь диапазон, а не верхний коммит — иначе чужой коммит прячется под подписанным
  local rev
  [[ -r "$ALLOWED_SIGNERS" ]] || fail "нет $ALLOWED_SIGNERS — без списка доверенных ключей не деплоим"
  timeout 60 git fetch -q origin main || fail "git fetch main не уложился в 60 сек"
  git merge-base --is-ancestor "$NEW_REV" origin/main || fail "${NEW_REV:0:7} нет в main — ветку подменили?"
  for rev in $(git rev-list "$OLD_REV..$NEW_REV"); do
    git -c gpg.ssh.allowedSignersFile="$ALLOWED_SIGNERS" verify-commit "$rev" >/dev/null 2>&1 \
      || fail "коммит ${rev:0:7} не подписан доверенным ключом"
  done
  log "подписи и принадлежность main проверены: $(git rev-list --count "$OLD_REV..$NEW_REV") коммит(ов)"
}

update_code() {
  # Не трогаем рабочую копию с ручными правками — иначе merge молча их смешает
  [[ -z "$(git status --porcelain --untracked-files=no)" ]] || fail "на сервере есть незакоммиченные правки"
  OLD_REV=$(git rev-parse HEAD)
  timeout 60 git fetch -q origin "$DEPLOY_BRANCH" || fail "git fetch не уложился в 60 сек"
  NEW_REV=$(git rev-parse "origin/$DEPLOY_BRANCH")
  # Целевой коммит уже есть в HEAD (например, main задеплоили вручную раньше, чем прошёл CI) —
  # откатываться назад не нужно
  if git merge-base --is-ancestor "$NEW_REV" "$OLD_REV"; then
    log "уже на ${OLD_REV:0:7} (содержит ${NEW_REV:0:7}), обновлять нечего"
    exit 0
  fi
  verify_trusted_range
  git merge -q --ff-only "$NEW_REV" || fail "fast-forward невозможен: история на сервере разошлась с origin/$DEPLOY_BRANCH"
  log "код: ${OLD_REV:0:7} -> ${NEW_REV:0:7}"
}

changed_files() {
  git diff --name-only "$OLD_REV" "$NEW_REV"
}

affected_services() {
  # Сервис затронут, если изменённый файл лежит в одном из его bind-монтирований кода.
  # data/ и logs/ — не код: шаблон Mini App читается на каждый запрос, рестарт не нужен.
  docker compose config --format json | python3 -c '
import json, sys
changed = [l.strip() for l in open(sys.argv[1]) if l.strip()]
root = sys.argv[2].rstrip("/") + "/"
for name, svc in json.load(sys.stdin)["services"].items():
    mounts = [v["source"].replace(root, "") for v in svc.get("volumes", []) if v.get("type") == "bind"]
    code = [m for m in mounts if m.split("/")[0] not in {"data", "logs"}]
    if any(f == m or f.startswith(m + "/") for f in changed for m in code):
        print(name)
' <(changed_files) "$PROJECT_DIR"
}

apply_changes() {
  local files services
  files=$(changed_files)
  services=$(affected_services | xargs)
  if grep -qE '^(requirements[^/]*\.(txt|lock)|[^/]+\.dockerfile|\.dockerignore)$' <<<"$files"; then
    log "изменились зависимости/Dockerfile — пересборка образов"
    timeout 900 docker compose up -d --build --wait || fail "пересборка не прошла"
  elif grep -qx 'compose.yml' <<<"$files"; then
    log "изменился compose.yml — пересоздание изменённых контейнеров"
    timeout 300 docker compose up -d --wait || fail "docker compose up не прошёл"
    [[ -z "$services" ]] || timeout 300 docker compose restart $services
  elif [[ -n "$services" ]]; then
    log "перезапуск: $services"
    timeout 300 docker compose restart $services || fail "restart не прошёл"
  else
    log "изменения не затрагивают код сервисов — перезапуск не нужен"
  fi
}

restart_counts() {
  docker compose ps -q | xargs docker inspect -f '{{.Name}}={{.RestartCount}}' | sort
}

verify_health() {
  local before since errors
  # С точностью до секунды: с минутной меткой в окно попадали ошибки старых контейнеров,
  # случившиеся при пересоздании за секунды до проверки (ложный DEPLOY_FAILED 9993bbb)
  since=$(date '+[%Y-%m-%d %H:%M:%S')
  before=$(restart_counts)
  timeout 120 docker compose up -d --wait >/dev/null 2>&1 || fail "сервисы не стали healthy за 120 сек"
  sleep "$OBSERVE_SECONDS"
  [[ "$(restart_counts)" == "$before" ]] || fail "контейнер перезапускался: $(diff <(echo "$before") <(restart_counts) | grep '^>' | xargs)"
  curl -fsS -m 10 http://127.0.0.1:8080/health >/dev/null || fail "/health не отвечает"
  errors=$(cat logs/*.log 2>/dev/null | awk -v s="$since" '$0 >= s' | grep -cE '\[ERROR\]|Traceback' || true)
  [[ "$errors" -eq 0 ]] || fail "в логах $errors новых ERROR — смотрите logs/*.log"
  log "✅ сервисы healthy, перезапусков нет, /health OK, новых ошибок нет"
}

main() {
  cd "$PROJECT_DIR"
  exec 9>"$LOCK_FILE"
  flock -w 600 9 || fail "другой деплой идёт дольше 10 минут"
  update_code
  apply_changes
  verify_health
}

main "$@"
