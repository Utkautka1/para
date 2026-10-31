# Contributing to Para

Thank you for your interest in contributing to **Para**. This repository enforces rigorous engineering practices designed for distributed systems, high availability, and sub-millisecond academic operations.

---

## 1. Code of Conduct & Architectural Invariants

All contributors must adhere to the core architectural principles established in this repository:

1. **Strict Method Length Bound (≤ 25 Lines)**:
   - Every function and method must not exceed **25 lines of code**.
   - Functions must strictly adhere to the **Single Responsibility Principle (SRP)**. Decompose complex orchestration into small, pure helper functions.
2. **Dual-Protocol Microservices Topology**:
   - Inter-service communication between `para-bot`, `para-worker`, and `para-api` must utilize **gRPC (HTTP/2 binary Protobuf)** with fallback to REST.
   - External APIs are exposed via FastAPI with Pydantic V2 data validation and strict type safety.
3. **Zero Host Port Exposure**:
   - Containerized services must communicate within the private internal Docker bridge network (`para-network`). Never bind services to `0.0.0.0` on host ports without reverse proxy isolation.
4. **Resilience & Storage Invariants**:
   - Transient operations must acquire distributed locks via Redis (`redis_lock`) with explicit TTL bounds.
   - At-least-once queue processing must utilize atomic Redis operations (`BLMOVE` / `LPUSH`).
5. **Dual-Endpoint Fallback & Resilient Ingress**:
   - External HTTP dependencies (such as upstream timetable APIs) must provide fallback mirrors with independent timeout bounds (<= 10s) and automatic failover.
6. **Configuration Centralization Invariant**:
   - All runtime variables, timeouts, rate limits, and external service URLs must be centralized in `config.py` and mirrored in `.env.example` and `.env.ci`. Hardcoding magic numbers or URLs across application modules is prohibited.
7. **gRPC Interceptor Security Invariant**:
   - All inter-service gRPC invocations must include authenticated metadata (`x-api-key`), validated at the server gateway via `ApiKeyAuthInterceptor` using constant-time cryptographic comparisons.

---

## 2. Local Development Setup

### Prerequisites
- **Python 3.11+** (Python 3.12 recommended)
- **Docker & Docker Compose** (v2+)
- **Redis 7.x** (standalone or containerized)

### Step-by-Step Installation
```bash
# 1. Clone the private repository
git clone https://github.com/Utkautka1/para.git
cd para

# 2. Initialize and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade package installer and install dependencies
pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt

# 4. Prepare local environment configuration
#    WARNING: overwrites an existing .env — never run this in a checkout with production secrets
cp .env.ci .env

# 5. Start background Redis store (if not running natively)
docker run -d --name para-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes
```

Alternatively, use the provided `Makefile`:
```bash
make install
make dev-redis
```

---

## 3. Code Style & Quality Gates

Before submitting any code changes, ensure all automated quality gates pass:

```bash
# Run Ruff linter in strict mode
ruff check .

# Automatically apply Ruff safe fixes
ruff check . --fix

# Run Bandit AST security scan
bandit -r services/ bot/ core/ api/ -c pyproject.toml

# Run the complete test suite (931 tests)
PYTHONPATH=. pytest tests/ -v
```

Shortcut via `Makefile`:
```bash
make lint
make test
```

---

## 4. Documentation Policy

Documentation is treated as a first-class production artifact:
- When modifying or creating functions, regenerate the engineering documentation suite:
  ```bash
  python3 scripts/generate_docs_suite.py
  ```
- Verify zero documentation drift via Git:
  ```bash
  git diff --exit-code docs/
  ```
- All documentation files in `docs/` must be written in **100% Technical English** conforming to the **Google Developer Documentation Style Guide**.

---

## 5. Git Commit & Pull Request Workflow

1. **Branch Naming**:
   - `feature/<issue-id>-short-description`
   - `fix/<issue-id>-bug-name`
   - `docs/<topic>-update`
2. **Commit Message Format (Conventional Commits)**:
   - `feat(schedule): add dual-endpoint fallback mechanism for timetable API`
   - `feat(yandex): add zen browser cookie sync utility and update UML diagram`
   - `fix(bot): resolve race condition in attendance session ownership`
   - `docs(api): update gRPC servicer parameter specifications`
   - `test(solver): add chaos test for DeepSeek DLQ retry backoff`
3. **Pull Request Checklist**:
   - [ ] All 931+ automated unit and integration tests pass.
   - [ ] `ruff check .` produces zero linting warnings.
   - [ ] Every new or modified method is ≤ 25 lines.
   - [ ] Documentation regenerated via `scripts/generate_docs_suite.py`.
   - [ ] No hardcoded tokens, API keys, or secrets introduced.
