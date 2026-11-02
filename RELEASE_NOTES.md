# Release Notes: Para v3.0.0

**Hardened Security Boundary, Fair Achievements, Dedicated STT Service & Continuous Deployment**

---

## 🚀 Overview

**Para v3.0.0** collects 55 commits made since v2.9.0. It is a major release because
several contracts changed: API keys are no longer accepted in URLs, more endpoints
require authentication, speech recognition moved to its own container, and the
achievements system was reset with a new ranking.

For the group the visible changes are an honest leaderboard (guild points instead of
attendance percent, so past absences no longer lock anyone out of the podium), 80
achievements that can all actually be unlocked, and a schedule that follows KTMU
substitutions. For operators: every green `main` commit is deployed automatically,
and only signed commits from `main` can reach the server.

---

## ⚠️ Breaking Changes & Migration

| Change | What to do |
| :--- | :--- |
| `?key=` / `?api_key=` and `GET /miniapp/dev-login` removed | Send `X-API-Key` or `Authorization: Bearer`; open Swagger via the one-time link from the bot (`GET /miniapp/login?t=`) |
| `/gamification/leaderboard`, `/gamification/profile` require a session or key | Mini App obtains its session before loading the leaderboard; API clients add the header |
| `/metrics` is admin-only | Prometheus scraper sends the master key in `X-API-Key` |
| Cross-site unsafe requests with the session cookie return 403 | Nothing for the Mini App and Swagger (same origin); third-party pages must use header auth |
| Speech-to-text runs in `para-stt` | `docker compose up -d` brings up the new service; set `WHISPER_*` variables for it |
| Sessions signed with `SESSION_SECRET` | Set `SESSION_SECRET` in `.env`; users re-open the Mini App once |
| Achievements reset with a journal baseline | Run once via `python -m services.achievement_reset --confirm` in `para-worker` (SQLite is backed up first) |
| `main.py` removed | Start the bot with `python bot.py` (as the containers already do) |
| Git history rewritten on 2026-11-02 | Re-clone, or `git fetch && git reset --hard origin/main`; old tags were re-created on the new history |

---

## 📊 Comparison Matrix: Release v2.9.0 vs Release v3.0.0

| Feature / Subsystem | Para v2.9.0 | Para v3.0.0 | Impact & Rationale |
| :--- | :--- | :--- | :--- |
| **Leaderboard** | Sorted by attendance percent | **Guild points: achievement XP + 10 per pair − 10 per absence, after a reset baseline** | Students with past absences can reach the podium again |
| **Achievements** | ~60 rules were dead code, 17 ids ever granted | **All 80 reachable, description = condition, journal rules granted by `para-worker`** | Achievements reflect what students actually did |
| **Admin panel** | No manual control of rewards | **«🏆 Ачивки и очки»: bonus XP / guild points, grant & revoke achievements** | Headman fixes edge cases without touching the database |
| **Schedule** | Base grid only | **KTMU substitutions applied (shift, cancel, move, stream cancel)** | Bot matches the official site on changed days |
| **Speech-to-text** | Inside the bot process | **Dedicated `para-stt` GPU service with a Redis job queue** | Bot image without CUDA; one GPU queue for the whole group |
| **API authentication** | Keys accepted in URLs, gamification public | **Header/Bearer/session only, one-time login links, CSRF guard** | Keys no longer leak into logs, history and Referer |
| **Deployment** | Manual `git pull` on the server | **Autodeploy after green CI, signed commits from `main` only** | No manual steps; a forged branch cannot reach the server |
| **Containers** | Code baked in images, all secrets everywhere | **Read-only code mounts, hashed lock files, per-service secrets** | Smaller blast radius, reproducible images |
| **CI** | 42 jobs | **57 jobs** (+ shell/Docker/workflow linters, gitleaks, detect-secrets, dead code, complexity, standalone imports, coverage gate ≥ 65 %) | Problems are caught before deploy |
| **Automated tests** | 664 | **977** | Every algorithm and security fix is covered |

---

## 🔒 Security Fixes Highlights

- **CSRF guard** for cookie-authenticated unsafe requests (`api/deps.py:_reject_cookie_csrf`).
- **Headman Mini App session** now passes admin checks (`classmate:` identity accepted for the headman and deputy).
- **Jaeger proxy** no longer forwards `Cookie`, `Authorization` and `X-API-Key` to the internal service.
- **Atomic, fail-closed rate limits** (`SET NX EX` + `INCR` in one transaction).
- **Telegram ID binding** refuses an ID already bound to another student.
- **Keys only in private chats**, separate `SESSION_SECRET`, STT and `/miniapp/action` limited to the group, `/metrics` hardened.

## 🛠️ Reliability Fixes Highlights

- Homework tasks are re-queued atomically (`LUA_REQUEUE`), so a retry no longer duplicates the task.
- Background tasks keep references and are drained on shutdown (`core/background.py`).
- Autodeploy writes files with `umask 022`, so containers can always read updated code.
- Attestation rooms and slots come from the schedule grid.

---

Full list of changes: [CHANGELOG.md](CHANGELOG.md#v300---2026-11-02).
