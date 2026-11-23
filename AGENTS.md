# para — карта проекта

Telegram-бот и API группы 1-КПД-3: расписание, экзамены, посещаемость, решатель ДЗ (DeepSeek),
расшифровка голосовых (Whisper), геймификация (ачивки/XP), Mini App со Swagger.
Навигация по символам — плагин `pyright-lsp` (go-to-definition / references), его ставит `.Codex/settings.json`.

## Сервисы (compose.yml)

| Контейнер | Точка входа | Что делает |
|---|---|---|
| `api` | `api.py` → `api/__init__.py:create_app` | FastAPI :8000 + gRPC :50051, Mini App, Swagger, прокси Jaeger |
| `bot` | `bot.py` | aiogram-поллинг, ходит в данные через `core/api_client.py` (gRPC → HTTP fallback) |
| `worker` | `worker.py` | фоновые циклы: топики расписания/экзаменов/посещаемости, ДР, бэкапы, refresh |
| `solver` | `solver.py` → `services/solver/task_processor.py` | потребитель Redis-очереди ДЗ → DeepSeek → .docx в топик |
| `stt` | `stt.py` → `services/stt_queue.py`, `services/transcriber.py` | очередь голосовых → faster-whisper |
| `redis`, `jaeger` | — | кэш/очереди/сессии; трейсинг OTel |

Код монтируется в контейнеры read-only из рабочей копии (`./api:/app/api:ro` и т.д.), `./data` и `./logs` — rw.
`main.py` — устаревшая точка входа: `from bot import main` берёт пакет `bot/`, а не `bot.py`, и не работает.

## Слои

- `config.py` — все env-переменные и константы (ключи Redis, лимиты, Lua-скрипты). Импортируется всеми сервисами; без нужных env падает при импорте.
- `core/` — синглтоны: `bot.py` (Bot, parse_mode=HTML), `redis.py` (пул), `redis_cache.py` (кэш, очередь ДЗ, локи, rate-limit, снапшоты), `database.py` (SQLite/SQLAlchemy + ручные миграции), `api_client.py`, `circuit_breaker.py`, `telemetry.py`, `metrics.py`, `prompt_sanitizer.py`, `logger.py`.
- `api/` — `deps.py` (вся авторизация), `router/*` (группа эндпоинтов = файл), `schemas/*` (имена совпадают с роутерами), `grpc/` + `proto/` (сгенерированные `*_pb2*.py`, не править).
- `bot/` — `commands.py` (связующий роутер), `handlers/{admin,user}`, `templates/{admin,user}` (тексты/клавиатуры/стейты), `filters/auth.py`, `middlewares/` (throttling, retry, tracing, achievements).
- `services/` — бизнес-логика и воркеры. Группы: `schedule_*`/`topic_updater` (расписание), `exam_*`, `attendance_*`, `achievement_*`/`gamification*` (ачивки), `solver/`, `stt_queue`/`transcriber`, `birthday_manager`, `backup_manager`, `alerting`, `notifier`, `deploy_notifier`, `testers_manager`, `login_tokens`, `classmates_auth`.
- `integrations/` — внешние источники: `google_sheets.py` (журнал посещаемости через Google Sheets/Drive API), `docx_parser.py` (контакты преподавателей с Yandex Disk), `deepseek.py`.
- `db/` — `sqlite/models.py`, `sqlite/repositories.py`, `subscribers.py`.
- `utils/` — `miniapp_auth.py` (initData HMAC, сессии тестеров), `storage.py` (атомарная запись JSON), `doc_generator.py` (.docx решений), `mute_parser.py`.
- `data/` — `birthdays.json` = реестр одногруппников (ФИО, tg_id, ДР) — это и есть база авторизации студентов; `api/miniapp.html`, `api/pulse.js`.

## Авторизация (api/deps.py)

Идентичности: `master_admin` (X-API-Key = `API_SECRET_KEY`), `tester:<uid>` (персональный ключ с префиксом `API_TESTER_KEY_PREFIX` или сессия тестера), `classmate:<uid>` (сессия одногруппника).
`verify_api_or_tester` — любой из трёх; `verify_admin_access` — `master_admin` или `tester:` с uid старосты/зама.
Сессия: кука `para_session` = `uid:ts:hmac(SESSION_SECRET)`, выдаётся `/miniapp/auth` (initData или ключ) и `/miniapp/login?t=` (одноразовый токен из бота, `services/login_tokens.py`).
В боте: `AuthFilter` (только староста), `ClassmateAuthFilter` (tg_id в реестре), `AttendanceAuthFilter`.

## Ключевые потоки

- ДЗ: `bot/handlers/user/hw_solver.py` → `push_hw_task`/`schedule_hw_task` (Redis) → `solver` `pop_hw_task` (BLMOVE в processing) → `ack_hw_task`/`nack_hw_task` (LREM по JSON-строке, поэтому задачу нельзя мутировать до LREM).
- Расписание: `services/schedule_parser.py` (API колледжа + fallback, снапшот в Redis) → `topic_updater.py` редактирует закреп в топике.
- Посещаемость: `bot/handlers/admin/attendance.py` (опрос) → `services/attendance_manager.py` → `integrations/google_sheets.py` (запись в Google Таблицу) → `attendance_topic_updater.py`.
- Ачивки: события из хэндлеров/middleware → `services/achievement_events.py` → `achievement_service.award_achievement` → правила в `achievement_rules.py`, каталог в `gamification_registry.py`.

## Разработка и деплой

- `make test` / `make lint` (ruff + bandit) / `make type-check` (mypy) / `make docs` (генератор `scripts/generate_docs_suite.py` → `docs/**`, не править вручную).
- Push в `main` → CI (`.github/workflows/ci.yml`) → джоб deploy-gate двигает `ci-passed` → сервер `scripts/autodeploy.sh` (systemd-таймер, каждые 2 мин) деплоит.
- Прод: сервер `home` (Tailscale); публичный вход — Caddy на VPS (`scripts/vps/Caddyfile`) через reverse SSH-туннель.
- `docs/UML.md` — Mermaid-диаграмма, обновлять при изменении классов/модулей/API.
