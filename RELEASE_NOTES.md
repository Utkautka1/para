# Release Notes: Para v2.8.0

## 🚀 Overview

**Para v2.8.0** delivers a comprehensive enterprise-grade production hardening and resilience milestone, implementing all 21 points of the architectural engineering audit. This release establishes robust zero-trust security (non-root Dockerfiles, Trivy CVE scanning, pre-commit secret auditing), production observability (Prometheus `/metrics`, distributed `trace_id` correlation), modular solver decomposition, typed domain configuration models, multimodal prompt injection sanitization, stateful async Circuit Breaker protection, strict MyPy static typing, and an expanded suite of **629 passing tests** (up from 594).

---

## 📊 Summary of Changes vs v2.7.0

| Dimension | Release v2.7.0 | Release v2.8.0 | Impact |
| :--- | :--- | :--- | :--- |
| **Container Security** | `root:root` execution | **Unprivileged `appuser` (UID 1000)** | Eliminates host volume takeover & breakout |
| **CI Security Pipeline** | Basic lint & pytest | **Pre-commit (10 hooks) + Trivy + Pip-Audit** | Automated 4-tier security validation |
| **Observability** | Plain text log files | **Prometheus `/metrics` + ContextVar Tracing** | Real-time monitoring and log correlation |
| **AI LLM Protection** | Raw prompt passing | **Prompt Sanitizer + Circuit Breaker** | Protection against prompt injection & cascading outages |
| **Solver Architecture** | Monolithic (378 lines) | **Decomposed `services/solver/` (58 lines)** | Modular, maintainable homework pipeline |
| **Configuration** | Flat global constants | **Frozen Domain Dataclasses + Facade** | Type-safe configuration with 100% backward compatibility |
| **Static Typing** | Unchecked dynamic types | **Configured MyPy (`make type-check`)** | Strict compile-time type verification |
| **Automated Tests** | 594 / 594 passing | **629 / 629 passing (+35 tests)** | Full coverage of new resilience & domain components |
| **Legal Compliance** | High-level overview | **Detailed GDPR / 152-ФЗ Erasure & /dev/shm** | Legal compliance and data minimization guarantees |

---

## 🔍 Key Architectural Enhancements

### 1. Non-Root Container Security & Supply Chain Hardening
* Enforced unprivileged user `appuser` (UID 1000:GID 1000) across all service Dockerfiles (`api`, `bot`, `worker`, `solver`).
* Added pre-commit hooks (`.pre-commit-config.yaml`) with detect-secrets baseline (`.secrets.baseline`).
* Automated PyPA vulnerability scanning (`pip-audit`) and Trivy CRITICAL scanner in GitHub Actions.

### 2. Prometheus Observability & Distributed Tracing
* Exposed production metrics endpoint `GET /metrics` (`api/router/metrics.py`, `core/metrics.py`) tracking memory RSS, CPU times, HTTP duration histograms, and solver queue depth.
* Integrated `ContextVar` `trace_id` into all logs (`[trace_id: ...] [thread: ...]`) and automatic `X-Request-ID` generation / propagation in FastAPI middleware.

### 3. Solver Monolith Decomposition & Modularity
* Decomposed monolithic `solver.py` into `services/solver/`:
  - `payload_extractor.py`: Safe download and multimodal attachment parser.
  - `telegram_reporter.py`: Delivery of solutions and structured user alerts.
  - `task_processor.py`: Worker loop with semaphore throttling and atomic ACK/NACK.
* Shrunk the `solver.py` entrypoint from 378 lines to a clean 58-line orchestrator.

### 4. Multimodal AI Safety & Circuit Breaker
* `core/prompt_sanitizer.py`: Normalizes Unicode, removes control characters, escapes context tags (`</учебное_задание>`), and flags prompt injection / jailbreak attempts.
* `core/circuit_breaker.py`: Stateful Circuit Breaker (`CLOSED`, `OPEN`, `HALF_OPEN`) with `async_retry_with_backoff` and random jitter.

### 5. Domain Configuration Models & Developer Experience
* Created frozen dataclasses in `core/config_models.py` (`TelegramConfig`, `ScheduleConfig`, `CampusConfig`, `RedisConfig`, `YandexConfig`, `ApiConfig`, `AiSolverConfig`, `WhisperConfig`, `NotificationConfig`).
* Added `.github/CODEOWNERS`, PR templates, and developer setup script `scripts/dev_setup.sh`.

---

## 🛠️ Deployment & Verification

```bash
# 1. Update source code
git pull origin main

# 2. Rebuild and launch hardened containers
docker compose up -d --build

# 3. Verify health & metrics
curl -s http://localhost:8000/metrics | grep process_resident_memory_bytes
```
