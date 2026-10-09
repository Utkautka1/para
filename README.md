# 🎓 Para — Enterprise-Grade Academic Ops & Distributed Telegram Ecosystem

[![CI/CD Pipeline](https://github.com/Utkautka1/para/actions/workflows/ci.yml/badge.svg)](https://github.com/Utkautka1/para/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/pytest-546%20passed%20(100%25)-brightgreen.svg?logo=pytest&logoColor=white)](https://pytest.org)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Architecture](https://img.shields.io/badge/architecture-Microservices%20%7C%20Dual--Protocol-orange.svg?logo=fastapi&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-uvloop%20%2B%20httptools-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![gRPC](https://img.shields.io/badge/gRPC-HTTP%2F2%20Protobuf-244c5a.svg?logo=grpc&logoColor=white)](https://grpc.io)
[![aiogram](https://img.shields.io/badge/aiogram-3.4%20(AsyncIO)-2CA5E0.svg?logo=telegram&logoColor=white)](https://docs.aiogram.dev)
[![Redis](https://img.shields.io/badge/Redis-7.x%20(LRU%20%2B%20AOF)-DC382D.svg?logo=redis&logoColor=white)](https://redis.io)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose%20v2-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)
[![Security Audit](https://img.shields.io/badge/security-Bandit%20Passing-success.svg?logo=shield&logoColor=white)](https://github.com/PyCQA/bandit)
[![Code Style](https://img.shields.io/badge/code%20style-Ruff%20Strict-black.svg?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Para** is an enterprise-grade, high-throughput distributed microservices platform engineered for real-time academic schedule orchestration, collaborative WOPI attendance registries, AI-assisted homework synthesis, and Telegram Supergroup operations. Built with modern asynchronous Python, dual-protocol RPC networking (REST + gRPC), and multi-tier caching hierarchies.

---

## 🏛️ System Architecture

Para follows a decoupled, containerized microservices architecture with isolated failure domains, strict boundary enforcement, and horizontal scalability:

```
                                  ┌────────────────────────────────────────┐
                                  │      Telegram Supergroup & DMs         │
                                  └───────────────────┬────────────────────┘
                                                      │
                                           HTTPS / Long-Polling
                                                      ▼
┌───────────────────────────┐             ┌────────────────────────────────┐
│    Telegram Mini App      │  HMAC Auth  │            para-bot            │
│   (Embedded Swagger UI)   │◄───────────►│       aiogram 3.4 Engine       │
└─────────────┬─────────────┘             └───────┬───────────────┬────────┘
              │                                   │               │
         HTTP REST                           gRPC / REST     LPUSH / Tasks
              ▼                                   ▼               ▼
┌───────────────────────────────────────────┐     │     ┌──────────────────┐
│                 para-api                  │◄────┘     │    para-redis    │
│  FastAPI (uvloop) + gRPC Binary Server    │           │  L2 Cache & AOF  │
│  WOPI Host + KTMU Upstream Ingress Engine │           │  Distributed FSM │
└─────────────────────┬─────────────────────┘           └────────┬─────────┘
                      │                                          │
                  Snapshots                                  RPOPLPUSH
                      ▼                                          ▼
┌───────────────────────────────────────────┐     ┌────────────────────────┐
│                para-worker                │     │      para-solver       │
│  APScheduler + Telemetry Bell Dispatcher  │     │ DeepSeek AI Engine     │
│  Topic Auto-Updater + Garbage Collection  │     │ GOST Word Synthesizer  │
└───────────────────────────────────────────┘     └────────────────────────┘
```

### Microservice Topology

| Service Container | Base Runtime | Primary Responsibilities | Network Protocols |
| :--- | :--- | :--- | :--- |
| `para-bot` | `python:3.11-slim` | Ingress gateway, user command FSM, inline keyboards, scoped menus | HTTPS, Telegram Bot API |
| `para-api` | `python:3.11-slim` | Upstream scraping, schedule cache, WOPI server, Swagger UI | Dual: HTTP REST + gRPC |
| `para-worker` | `python:3.11-slim` | Bell alarms, topic synchronization, birthday alerts, Yandex keep-alive | APScheduler, Redis Pub/Sub |
| `para-solver` | `python:3.11-slim` | Asynchronous homework solving queue, DeepSeek LLM, GOST `.docx` generator | Async Redis `BLMOVE` |
| `para-redis` | `redis:7-alpine` | Distributed FSM storage, L2 cache snapshots, distributed locks, ZSET TTL | RESP3 (TCP :6379) |

---

## ⚡ Key Engineering Highlights

### 1. High-Speed Dual-Protocol RPC Mesh (REST + gRPC)
* **Multiplexed Protocols**: `para-api` simultaneously runs a **gRPC HTTP/2 server** (`Protobuf`) on port `50051` for high-throughput internal RPCs and a **FastAPI REST server** driven by the `uvloop` and `httptools` C-extensions on port `8000`.
* **Zero Cold-Start Latency**: Pre-warmed TCP keepalive connections, HTTP/2 frame pooling, and persistent gRPC channels cut inter-service communication latency down to `< 0.3 ms`.

### 2. Multi-Tier Cache Hierarchy (L1 RAM + L2 Redis)
* **Sub-Millisecond Queries**:
  * **L1 In-Memory Cache**: Zero-overhead in-process dictionary cache for today's resolved schedule (`< 10 µs`).
  * **L2 Redis Snapshot**: Serialized binary JSON snapshots with configurable TTL and atomic fallback.
* **Upstream Protection**: Singleflight request collapsing prevents thundering herd problems when fetching upstream schedules from college servers.

### 3. Electronic Attendance Registry & WOPI Cloud Sync
* **WOPI Protocol Compliant**: Native implementation of `CheckFileInfo`, `GetFile`, and `PutFile` for direct browser-based spreadsheet editing in Yandex Documents / OnlyOffice.
* **Optimistic UI with Background Settling**: Headman marks attendance with immediate UI feedback (< 10 ms), followed by a delayed settling pass that reconciles OnlyOffice's co-authoring autosave buffer.
* **Mutual Headman & Deputy Telemetry**: When either the Headman or Deputy Headman records attendance or cancels a session, a comprehensive analytical breakdown (present, late, excused, unexcused counts and absent student names) is dispatched asynchronously to the peer administrator's direct messages.

### 4. Resilient AI Homework Synthesis Queue
* **Reliable Queue Lifecycle**: Utilizes Redis `BLMOVE` between `hw:tasks:queue` and `hw:tasks:processing` to guarantee **at-least-once delivery** with zero task loss during container crashes.
* **Multimodal DeepSeek Integration**: Ingests prompts, images, PDFs, and DOCX assignments, applying prompt-injection sanitization and token-budget limits.
* **GOST 7.32-2017 Document Synthesizer**: Programmatically produces formatted Word documents (`.docx`) compliant with Russian academic standards (margins, typography, numbered headers, tables, formulas).

### 5. Telegram Mini App & Cryptographic Gateway
* **HMAC-SHA256 WebApp Handshake**: The embedded Swagger UI (`/miniapp`) verifies `initData` signatures using the bot token secret key with anti-replay timestamp verification.
* **Dynamic Tester Whitelist**: Authorized testers are tracked in Redis, allowing real-time permission toggling via Telegram bot commands (`/add_tester`, `/del_tester`).

---

## 🚀 Performance Benchmarks

| Operation / Path | Execution Engine | Typical Latency | Throughput / Limits |
| :--- | :--- | :--- | :--- |
| **Schedule Query (L1 RAM Hit)** | In-Process Memory Cache | **< 0.05 ms** | ~50,000 req/s |
| **Schedule Query (L2 Redis Hit)** | Redis 7 Connection Pool | **1.8 – 3.2 ms** | ~12,000 req/s |
| **gRPC Protobuf Day Schedule** | HTTP/2 Binary Serialization | **0.3 – 0.6 ms** | Frame size: ~1.3 KB |
| **Optimistic Attendance Mark** | Redis In-Memory Marks Cache | **~ 8 – 12 ms** | Instant UI feedback |
| **WOPI Sheet Commit** | Async Thread-Offloaded OpenPyXL | **1.2 – 2.4 s** | 12-sheet Excel parsing |
| **DeepSeek Homework Solver** | Multimodal Vision + LLM Pipeline | **4 – 15 s** | Semaphore bounded (3 concurrent) |

---

## 📂 Project Structure

Para follows a clean, canonical architecture ensuring single responsibility and high cohesion across all modules:

```
para/
├── api.py                    # Entry point: Dual-Protocol FastAPI REST + gRPC server
├── api.dockerfile            # Production container definition for API service
├── bot.py                    # Entry point: Telegram Bot long-polling gateway
├── bot.dockerfile            # Production container definition for Bot service
├── worker.py                 # Entry point: APScheduler background task worker
├── worker.dockerfile         # Production container definition for Worker service
├── solver.py                 # Entry point: DeepSeek async homework queue consumer
├── solver.dockerfile         # Production container definition for Solver service
├── compose.yml               # Multi-container Docker Compose cluster specification
├── config.py                 # Centralized type-safe environment configuration
├── requirements.txt          # Production runtime dependencies
├── requirements-dev.txt      # Development, testing, and linting dependencies
├── pyproject.toml            # Tooling configuration (Ruff, Pytest, Bandit)
│
├── api/                      # REST & gRPC Presentation Tier
│   ├── deps.py               # Dependency injection & HMAC/API-Key security guards
│   ├── handlers.py           # Custom HTTP exception and validation handlers
│   ├── grpc/                 # gRPC implementation tier:
│   │   ├── converters.py     # Pydantic to Protobuf message serializers
│   │   ├── server.py         # Async gRPC server lifecycle (HTTP/2 persistent socket)
│   │   └── servicers.py      # Schedule, Exams, and Teachers gRPC RPC implementations
│   ├── proto/                # Protocol Buffers definitions & generated stubs:
│   │   ├── exams.proto       # Exams RPC service contract
│   │   ├── schedule.proto    # Day & Week schedule binary RPC contract
│   │   └── teachers.proto    # Teacher contacts & directory RPC contract
│   ├── router/               # FastAPI route controllers:
│   │   ├── attendance.py     # WOPI electronic attendance registry endpoints
│   │   ├── birthdays.py      # Student birthday management endpoints
│   │   ├── classmates.py     # Group member authentication & registry routes
│   │   ├── exams.py          # Examination timetable endpoints
│   │   ├── health.py         # Kubernetes/Docker readiness & liveness probes
│   │   ├── miniapp.py        # Telegram Mini App HMAC-SHA256 handshake & auth
│   │   ├── schedule.py       # Day/Week schedule REST queries with L1/L2 cache
│   │   ├── solver.py         # Homework solving task ingress & queue status
│   │   ├── subscribers.py    # Notification subscriber registry endpoints
│   │   ├── system.py         # Safe cache flushing & Redis diagnostic routes
│   │   └── teachers.py       # Instructor directory & custom remote link routes
│   └── schemas/              # Pydantic v2 validation and transfer schemas (DTO)
│
├── bot/                      # Telegram Ingress & Interaction Tier
│   ├── commands.py           # Interactive command menu registration (bot.set_my_commands)
│   ├── filters/              # Custom aiogram authorization and context filters:
│   │   └── auth.py           # Classmates, Headman, and Deputy access control filters
│   ├── handlers/             # Modular event routers:
│   │   ├── admin/            # Administrative handlers (attendance, mute, panel, ping_all, testers)
│   │   ├── user/             # Student handlers (schedule, attendance, hw_solver, public_copy)
│   │   └── errors.py         # Global exception trapper & user-facing alert fallback
│   ├── middlewares/          # Event interceptors:
│   │   ├── retry.py          # Telegram FloodControl 429 backoff middleware
│   │   └── throttling.py     # Callback query and command rate limiter
│   └── templates/            # Semantic message formatting & inline keyboard builders:
│       ├── admin/            # Admin poll keyboards, student cards, and tester menus
│       └── user/             # Timetable grids, day navigation, and action buttons
│
├── core/                     # Distributed Foundation Tier
│   ├── api_client.py         # Resilient HTTP/gRPC internal client with circuit breaking
│   ├── bot.py                # Bot and Dispatcher singletons with RedisStorage FSM
│   ├── logger.py             # Structured rotating file & console logger
│   ├── redis.py              # Low-level connection pool manager
│   └── redis_cache.py        # Distributed locks, atomic snapshots, and task queues
│
├── data/                     # Local file data storage (birthdays, wish registry, miniapp.html)
├── db/                       # Local database adapters:
│   └── subscribers.py        # Atomic JSON subscriber persistence with fsync
│
├── integrations/             # External Upstream Integrations
│   ├── deepseek.py           # Multimodal DeepSeek LLM vision API client
│   ├── docx_parser.py        # Remote instructor contact parser from Yandex Disk
│   ├── yandex_docs.py        # WOPI protocol implementation for Yandex Documents
│   └── yandex_keepalive.py   # Autonomous session keep-alive loop
│
├── scripts/                  # DevOps & Utility Scripts
│   └── tunnel_sync.py        # Automated Cloudflare/SSH tunnel synchronization
│
├── services/                 # Business Logic & Orchestration Tier
│   ├── attendance_manager.py # State machine for electronic attendance sessions
│   ├── attendance_stats.py   # Statistical aggregator & attendance league calculator
│   ├── attendance_topic_updater.py # Adaptive polling & pinned registry updater
│   ├── birthday_manager.py   # Automated celebratory greeting dispatcher
│   ├── classmates_auth.py    # Identity registry & cryptographic Telegram binding
│   ├── custom_teachers.py    # Custom instructor contact persistence
│   ├── exam_parser.py        # Upstream examination timetable parser
│   ├── exam_topic_updater.py # Pinned examination topic updater
│   ├── models.py             # Core dataclass domain models (Lesson, ExamItem, Session)
│   ├── notifier.py           # APScheduler bell notifications (10-min pre-class alarms)
│   ├── schedule_parser.py    # Resilient KTMU college timetable parser & parser engine
│   ├── testers_manager.py    # Mini App Swagger UI tester whitelist manager
│   ├── topic_updater.py      # Pinned schedule message updater & ZSET message cleaner
│   └── user_cache.py         # Fast JSON-backed Telegram user identity cache
│
├── utils/                    # Shared Utility Libraries
│   ├── doc_generator.py      # GOST 7.32-2017 compliant Word document builder
│   ├── miniapp_auth.py       # HMAC-SHA256 cryptographic initData validator
│   ├── mute_parser.py        # Natural language duration parser for moderation (/mute)
│   └── storage.py            # Atomic JSON serialization with temp file & fsync guarantees
│
├── docs/                     # Architectural Documentation
│   ├── UML.md                # Comprehensive Mermaid UML architectural specification
│   ├── PRIVACY.md            # Data privacy & user telemetry policy
│   └── puml/                 # Visual PlantUML diagrams and SVG architecture artifacts
│
└── tests/                    # Comprehensive Test Suite (546 tests, 100% passing)
    ├── conftest.py           # Pytest fixtures and mock objects
    ├── test_admin_panel.py   # RBAC & administrative control tests
    ├── test_attendance.py    # WOPI, mark calculation, and mutual notification tests
    ├── test_hw_solver_logic.py # DeepSeek queue and document generation tests
    ├── test_grpc_services.py # Binary Protobuf RPC contract validation
    └── test_security_and_chaos.py # Injection, flood, and chaos resilience tests
```

---

## 🛠️ Quickstart & Deployment

### Production Deployment (Docker Compose)

Para is fully containerized and orchestrates via Docker Compose.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Utkautka1/para.git
   cd para
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (BOT_TOKEN, API_SECRET_KEY, etc.)
   ```

3. **Launch the cluster**:
   ```bash
   docker compose up -d --build
   ```

4. **Monitor service status**:
   ```bash
   docker compose ps
   ```

5. **Tail granular service logs**:
   ```bash
   docker compose logs -f bot       # Telegram ingress logs
   docker compose logs -f api       # REST & gRPC API logs
   docker compose logs -f worker    # Background scheduler & topic logs
   docker compose logs -f solver    # AI homework queue consumer logs
   ```

---

### Local Development Setup

Para supports native local development outside containers:

1. **Initialize virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. **Spin up local Redis instance**:
   ```bash
   docker run -d --name para-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes
   ```

3. **Configure local environment**:
   ```bash
   cp .env.ci .env  # Pre-populated with safe local mock defaults
   ```

4. **Execute services in parallel terminals**:
   ```bash
   # Terminal 1: REST & gRPC Gateway
   python api.py

   # Terminal 2: Telegram Bot
   python bot.py

   # Terminal 3: Background Worker
   python worker.py

   # Terminal 4: AI Homework Solver
   python solver.py
   ```

---

## 🧪 Quality Assurance & CI/CD Pipeline

The project enforces strict quality standards through an automated 3-tier GitHub Actions workflow (`.github/workflows/ci.yml`):

```mermaid
flowchart LR
    Push([Push / PR]) --> Lint["Stage 1: Ruff & Bandit"]
    Push --> TestMatrix["Stage 2: Pytest Matrix\n(Python 3.11 & 3.12)"]
    Lint --> DockerBuild["Stage 3: Docker Build\n(--parallel)"]
    TestMatrix --> DockerBuild
    DockerBuild --> Verified([✅ Production Ready])
```

### Running Checks Locally

* **Execute full test suite (546 tests)**:
  ```bash
  PYTHONPATH=. pytest tests/ -v
  ```

* **Run strict code style and linter checks**:
  ```bash
  ruff check .
  ```

* **Run automated AST security audit**:
  ```bash
  bandit -r services/ bot/ core/ api/ -c pyproject.toml
  ```

---

## 🔐 Security & Hardening Architecture

* **Least-Privilege Role-Based Access Control (RBAC)**: Strict separation between standard students, deputy headmen, and the headmaster. Unauthorized ingress attempts are trapped with audit log entries.
* **Zero Host Port Exposure**: Only necessary gateway ports are bound to loopback interfaces (`127.0.0.1`), keeping Redis and internal services strictly inside isolated Docker bridge networks.
* **Defensive AST Parsing**: XML spreadsheets are sanitized using `defusedxml` to prevent XXE (XML External Entity) expansion attacks.
* **Distributed Rate Limiting**: Callback and message throttling prevents flood attacks, and LLM input token ceilings prevent API resource exhaustion.

---

## 📄 License & Attribution

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for detailed terms.

For data privacy guidelines, audit protocols, and student record handling policies, review [`PRIVACY.md`](PRIVACY.md). For complete architectural diagrams, inspect [`docs/UML.md`](docs/UML.md).
