# 🏛️ Para — Distributed Telegram Bot, College Schedule & AI Academic Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![aiogram 3](https://img.shields.io/badge/aiogram-3.x-2CA5E0.svg)](https://docs.aiogram.dev/)
[![Redis 7](https://img.shields.io/badge/Redis-7.x-DC382D.svg)](https://redis.io/)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)
[![Tests](https://img.shields.io/badge/Tests-445%20Passed-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/UML%20Docs-Verified-blueviolet.svg)](docs/UML.md)

A high-performance, fault-tolerant distributed system designed for college student groups. Combines sub-2ms timetable caching, automated Telegram topic administration, bell reminders with chat auto-cleanup, an At-Least-Once reliable queue AI homework solver generating GOST-standard Word documents, and an electronic attendance registry powered by the WOPI protocol and cloud office editors.

---

## 📑 Architecture & UML Specification

Comprehensive architectural specifications, class contracts, state registries, and execution flows are documented in **[docs/UML.md](docs/UML.md)**:

1. **[System Services Architecture](docs/UML.md#1-сквозная-архитектура-сервисов-и-системных-контрактов)** — Component topology and typed service contracts (`classDiagram`).
2. **[Domain Models & Interfaces](docs/UML.md#2-диаграмма-классов-моделей-и-сервисных-контрактов)** — Core Pydantic schemas, response types, and manager interfaces (`classDiagram`).
3. **[Schedule Caching Module](docs/UML.md#3-сквозной-процесс-запрос-и-кэширование-расписания)** — Multi-level caching (L1 memory, L2 Redis snapshot) with KTMU parser (`classDiagram`).
4. **[Topic & Bell Management](docs/UML.md#4-сквозной-процесс-уведомления-о-парах-и-очистка-топика)** — Idempotent notifications and ZSET auto-cleanup timers (`classDiagram`).
5. **[Reliable Homework Queue](docs/UML.md#5-сквозной-процесс-надежная-очередь-решения-домашних-заданий)** — At-Least-Once execution via atomic `BLMOVE` and GOST docx generator (`classDiagram`).
6. **[WOPI Attendance Engine](docs/UML.md#6-сквозной-процесс-электронная-ведомость-посещаемости-wopi)** — Cloud office document integration with Yandex Disk (`classDiagram`).
7. **[Data Models & Redis Registry](docs/UML.md#7-модели-сущностей-и-структура-хранилища-redis)** — Complete ERD and key storage lifecycle specification.

---

## ⚡ Key Capabilities

### 1. Timetable Engine & L2-Snapshot Caching
- **Sub-2ms Cold Starts**: Serializes parsed group schedules into a Redis snapshot (`sched:group:snapshot`) with a 4-hour TTL, completely shielding users from upstream latency.
- **Upstream KTMU Parser**: Parses 40 MB raw JSON payloads from KTMU college servers, resolves subgroups, streams, classroom addresses, and parity-dependent lesson times.
- **Remote Classroom Enrichment**: Automatically parses teacher consultation docx files from Yandex Disk to embed direct Zoom and Yandex Telemost conference credentials into lesson cards.
- **Fail-Safe HTTP Resilience**: Implements HTTP conditional requests (`ETag` / `If-None-Match`), fast 15-second timeouts, and automatic fallback to stale snapshots if upstream college servers degrade.

### 2. Automated Topic Manager & Bell Alerts
- **Minute-by-Minute Evaluation**: Background scheduler monitors time remaining until bell rings (10 minutes before start/end).
- **Strict Idempotency**: Employs Redis atomic flags (`rem:sent:{group}:{date}:{period}:{type}`) to prevent duplicate notifications across worker restarts.
- **Self-Cleaning Ephemeral Messages**: Temporary notifications are registered in a Redis Sorted Set (`topic:cleanup_messages`) with a score of `now + 900s` and automatically purged via `deleteMessage` to prevent chat bloat.

### 3. Reliable AI Homework Solver
- **Reliable Queue Pattern**: Uses Redis atomic `BLMOVE` between `hw:tasks:queue` and `hw:tasks:processing` to guarantee **At-Least-Once** processing even during hard worker terminations.
- **Stale Task Recovery**: On daemon startup, `recover_stale_hw_tasks` restores orphaned tasks via `RPOPLPUSH`.
- **DeepSeek Integration**: Step-by-step academic solutions with full mathematical formula derivation.
- **GOST Academic Word Compiling**: Translates Markdown and LaTeX formulas into `.docx` files formatted strictly according to Russian GOST standards (Times New Roman 14pt, 1.5 line spacing, 30-15-20-20 mm margins, page numbering).

### 4. Electronic Attendance Registry (WOPI Protocol)
- **Standardized Cloud Office**: Full WOPI implementation (`CheckFileInfo`, `GetFile`, `PutFile`) allowing group admins to edit attendance spreadsheets directly inside Yandex Documents web editor.
- **Temporary Cryptographic Sessions**: Ephemeral session tokens with 1-hour TTL in Redis.
- **Cloud Storage Synchronization**: Direct two-way sync with Yandex Disk `.xlsx` spreadsheets.

---

## 🏗️ Architecture & Service Topology

The system is engineered as 5 isolated containerized microservices:

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│          Students, Group Chat, Group Admin (Telegram)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Telegram Gateway (para-bot)                 │
│         aiogram 3 • Event Routers • Keyboard Handlers       │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
     HTTP GET  │                    LPUSH     │ Task
     /schedule │                              │
               ▼                              ▼
┌──────────────────────────────┐┌─────────────────────────────┐
│   Internal API (para-api)    ││     In-Memory Data Grid     │
│   FastAPI • Schedule Parser  ││        (para-redis)         │
│   WOPI Office Controller     ││  Redis 7 • Snapshots • ZSET │
└──────────────┬───────────────┘│  Reliable Queue • Sessions  │
               │                └─────────────┬───────────────┘
    L2 Cache   │                              │ BLMOVE
    Snapshot   │                              │
               ▼                              ▼
┌──────────────────────────────┐┌─────────────────────────────┐
│  Topic Worker (para-worker)  ││   AI Solver (para-solver)   │
│  APScheduler • 60s Monitor   ││   DeepSeek LLM • Docx GOST  │
│  Bell Reminders • Cleanup    ││   Consumer Loop • Delivery  │
└──────────────────────────────┘└─────────────────────────────┘
```

| Container | Base Image | Role | Memory Limit |
| :--- | :--- | :--- | :--- |
| `para-redis` | `redis:7-alpine` | Primary data grid: L2 snapshot cache, reliable queues, cleanup ZSET | 64 MB |
| `para-api` | Python 3.11-slim | Internal REST API for schedule parsing, teacher data, and WOPI server | 256 MB |
| `para-bot` | Python 3.11-slim | Interactive Telegram bot (aiogram 3), commands, inline menus | 384 MB |
| `para-worker` | Python 3.11-slim | Background daemon with APScheduler, 60s bell monitor, auto-cleanup | 384 MB |
| `para-solver` | Python 3.11-slim | Reliable queue consumer loop, AI reasoning, GOST docx generation | 512 MB |

---

## 📁 Repository Structure

```
para/
├── api.py                    # Entrypoint for FastAPI Internal API service
├── api.dockerfile            # Dockerfile for para-api container
├── bot.py                    # Entrypoint for Telegram Bot service
├── bot.dockerfile            # Dockerfile for para-bot container
├── worker.py                 # Entrypoint for Background Topic/Bell Worker
├── worker.dockerfile         # Dockerfile for para-worker container
├── solver.py                 # Entrypoint for AI Homework Solver Worker
├── solver.dockerfile         # Dockerfile for para-solver container
├── compose.yml               # Production multi-service Docker Compose configuration
├── config.py                 # Global typed environment settings & constants
├── requirements.txt          # Python runtime dependencies
│
├── api/
│   ├── deps.py               # Dependency injection & API Key security
│   ├── router/               # Route endpoints (schedule, wopi, attendance)
│   └── schemas/              # Pydantic request/response validation schemas
│
├── bot/
│   ├── filters/              # aiogram custom chat and role filters
│   ├── handlers/             # Telegram command & callback handlers (admin/user)
│   ├── keyboards/            # Dynamic inline keyboards & navigation
│   └── templates/            # Message formatting & HTML presentation
│
├── core/
│   ├── api_client.py         # Persistent keep-alive HTTP client to para-api
│   ├── bot.py                # Bot and Dispatcher global singletons
│   ├── logger.py             # Structured logging subsystem
│   └── redis.py              # Redis connection pool and async client
│
├── data/                     # Local data files, birthday configs, templates
├── docs/
│   ├── UML.md                # Full architectural specifications & Mermaid diagrams
│   └── puml/                 # Standalone PlantUML source files & SVG exports
├── services/
│   ├── docx_parser.py        # Word generator (GOST formatting) & Yandex Disk parser
│   ├── models.py             # Core domain models (Lesson, ExamItem, etc.)
│   ├── redis_cache.py        # High-level Redis cache & queue manager
│   ├── schedule_parser.py    # KTMU timetable parser & snapshot builder
│   └── topic_updater.py      # Topic synchronization & bell alert manager
└── tests/                    # Comprehensive test suite (445 automated tests)
```

---

## 🔧 Environment Configuration

Copy the example configuration file:

```bash
cp .env.example .env
```

Key configuration variables:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Telegram Bot API authentication token | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `API_SECRET_KEY` | Shared secret header (`X-API-Key`) between services | `your_internal_secret_key` |
| `API_BASE_URL` | Base URL of the internal API service | `http://api:8000` (Docker) or `http://127.0.0.1:8000` |
| `REDIS_URL` | Redis connection URI | `redis://redis:6379/0` or `redis://localhost:6379/0` |
| `DEEPSEEK_API_KEY` | DeepSeek LLM API key for homework generation | `sk-xxxxxxxxxxxxxxxxxxxxxxxx` |
| `YANDEX_DISK_TOKEN` | OAuth token for Yandex Disk attendance & teacher files | `y0_AgAAAA...` |
| `GROUP_ID` | College group identifier in KTMU API | `e6189916-2591-11ec-8178-000c2941df90` |
| `ALLOWED_USER_ID` | Telegram user ID of group administrator / headman | `987654321` |
| `SCHEDULE_API_URL` | Upstream KTMU timetable JSON endpoint | `https://timetable-ktmu.ru/...` |
| `TIMEZONE` | System scheduling timezone | `Europe/Moscow` |

---

## 🚀 Quick Start & Development Setup

### Option 1: Local Development with Virtual Environment

1. **Clone repository**:
   ```bash
   git clone https://github.com/Utkautka1/para.git
   cd para
   ```

2. **Configure virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Start local Redis instance**:
   ```bash
   docker run -d --name local-redis -p 6379:6379 redis:7-alpine
   ```

4. **Launch individual services**:
   ```bash
   # Terminal 1: Internal API
   python api.py

   # Terminal 2: Telegram Bot
   python bot.py

   # Terminal 3: Topic Worker
   python worker.py

   # Terminal 4: AI Homework Solver
   python solver.py
   ```

### Option 2: Production Deployment with Docker Compose

All microservices, healthchecks, CPU/memory quotas, and volume bindings are defined in `compose.yml`:

```bash
# Build and launch all 5 containers in the background
docker compose up -d --build

# Monitor live log streams
docker compose logs -f

# Verify container health status
docker compose ps
```

---

## 🧪 Testing & Quality Assurance

The codebase includes an extensive automated test suite covering API contracts, parser edge-cases, Redis queue resilience, and Telegram message formatting:

```bash
# Run all tests
PYTHONPATH=. ./venv/bin/pytest tests/

# Run with verbose output and duration profiling
PYTHONPATH=. ./venv/bin/pytest tests/ -v --durations=10

# Run specific performance & resilience suite
PYTHONPATH=. ./venv/bin/pytest tests/test_performance_and_resilience.py
```

### Architectural Quality Invariants
- **Function Line Limit**: Every function and method is strictly limited to **maximum 25 lines** of code with single responsibility.
- **Fail-Fast Error Handling**: Specific exceptions are captured before generic handlers; all transient errors log structured diagnostics.
- **Zero AI-Slop & Clean Code**: Clean, maintainable Python 3.11 idioms with complete type hinting (`Mapped`, `Annotated`, `Pydantic`).

---

## 📡 REST API & WOPI Endpoints

The internal API (`para-api`) exposes high-performance endpoints secured by `X-API-Key`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/schedule/day?target_date=YYYY-MM-DD` | Returns normalized schedule for the given date (`<2ms` with L2 cache) |
| `GET` | `/schedule/week?monday=YYYY-MM-DD` | Returns schedule for the entire 6-day academic week |
| `GET` | `/schedule/teachers` | Returns parsed teacher database with contact and Zoom links |
| `GET` | `/schedule/exams` | Returns upcoming exam and credit dates for the target group |
| `POST` | `/attendance/init` | Generates a secure temporary WOPI editing session for headman |
| `GET` | `/wopi/files/{file_id}` | WOPI `CheckFileInfo`: returns permissions, file size, and owner metadata |
| `GET` | `/wopi/files/{file_id}/contents` | WOPI `GetFile`: streams the binary `.xlsx` attendance spreadsheet |
| `POST` | `/wopi/files/{file_id}/contents` | WOPI `PutFile`: receives and updates `.xlsx` from the cloud office editor |

---

## 📄 License & Attribution

Designed and maintained for student group **1-КПД-3**. All rights reserved. Architectural and visual design details can be explored in the [Architecture Documentation](docs/UML.md).
