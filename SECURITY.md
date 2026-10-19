# Security Policy

## 1. Supported Versions

Security patches and dependency updates are applied exclusively to the `main` branch.

| Version | Supported | Release Date | Status |
| :--- | :--- | :--- | :--- |
| `v2.6.x` | :white_check_mark: | October 2026 | Active Production (Hardened Containers & gRPC Auth Interceptor) |
| `v2.5.x` | :white_check_mark: | October 2026 | Maintenance Mode (GPU STT Transcription Engine) |
| `v2.4.x` | :x: | October 2026 | Deprecated |
| `< v2.0` | :x: | Earlier | End of Life |

---

## 2. Vulnerability Reporting Protocol

Because this repository is private, security issues must be reported through direct internal channels:

1. **Do not create public Git issues or forum discussions** detailing sensitive vulnerabilities.
2. Contact the core engineering maintainers directly via Telegram or encrypted communication.
3. Include the following details in your security report:
   - Vulnerability category (e.g., Auth Bypass, Replay Attack, Injection, Race Condition).
   - Affected service and endpoint/method (e.g., `api/router/miniapp.py` -> `/miniapp/auth`).
   - Proof of Concept (PoC) or reproducible curl/gRPC request.
   - Potential impact on student privacy or telemetry integrity.

The maintainers will acknowledge receipt within 24 hours and issue a triage report with an estimated fix timeline.

---

## 3. Defense-in-Depth Architecture

This repository enforces defense-in-depth principles across all subsystems:

- **gRPC Constant-Time Authentication**: All binary microservice endpoints enforce constant-time `secrets.compare_digest` validation against `API_SECRET_KEY` via `ApiKeyAuthInterceptor`, preventing unauthorized inter-service RPC invocations.
- **Cryptographic Authentication**: Telegram Mini App endpoints require HMAC-SHA256 signature verification matching the Bot token with replay mitigation (`auth_date` validation within `SESSION_MAX_AGE_SECONDS`).
- **Container Hardening & Least Privilege**: Services enforce restricted Linux capabilities (`cap_drop: [ALL]` with surgical `SETUID`/`SETGID`/`DAC_OVERRIDE` on Redis for bind-mount volume persistence), CLI password masking via environment variables (`REDISCLI_AUTH`), and `no-new-privileges:true`.
- **Payload Bound Enforcement**: Public and worker endpoints strictly validate payload sizes (solver text <= 4000 chars, image <= 15MB) to neutralize memory exhaustion vectors.
- **AST Security Scanning**: Automated Bandit security scans execute on every pull request to detect socket leaks, weak cryptography, and unsafe serialization.
- **Network Isolation**: Docker containers communicate solely over internal bridge networks with zero host port exposure on `0.0.0.0`.
- **Secret Isolation & Config Centralization**: All credentials, tokens, and sync constants are strictly injected via `.env` with type-safe validation in `config.py`. Zero secrets are stored in Git, and `.env.example` templates are strictly sanitized to prevent sensitive network topology leakage.
- **Zero-Trust Upstream API Failover**: Upstream schedule endpoints (primary and fallback mirrors) are treated as untrusted boundaries with strict 10-second per-endpoint timeout budgets and structured exception containment to prevent denial-of-service cascading failures.
- **Ephemeral Session Token Hygiene**: Session cookies (`yandexuid`, `Session_id`) extracted via automated sync utilities are strictly injected into Redis memory caches with dynamic TTL expiry. Session tokens are never committed to version control.
- **Unauthenticated Ingress Trapping**: Unauthorized bot interactions (`bot/handlers/user/auth_fallback.py`) are strictly intercepted and logged as structured security events, blocking unauthorized access to headman workflows and private group operations.
- **Ephemeral RAM-Disk Media Isolation (`/dev/shm`)**: Audio and video notes ingested for STT transcription are strictly buffered into `/dev/shm` in-memory tmpfs with atomic unlinking in `finally` blocks, preventing persistent physical SSD wear and ensuring zero-trace media destruction.
- **Audio Concurrency & Rate Limiting Guard**: Voice processing enforces per-user concurrency constraints (`MAX_CONCURRENT_PER_USER=2`) and strict duration (`MAX_AUDIO_DURATION=300s`) and file size (`MAX_AUDIO_SIZE=20MB`) ceilings to neutralize denial-of-service and memory exhaustion attacks.

---

## 4. Key Rotation & Revocation Protocol

To minimize attack surface and credential exposure windows, all production secrets follow strict rotation lifecycles:

| Secret / Credential | Rotation Cadence | Rotation Procedure | Immediate Revocation Action |
| :--- | :--- | :--- | :--- |
| **Yandex Cookies (`Session_id`, `sessar`)** | Automated (12-24h) | Executed via `scripts/sync_yandex_cookie.py` with direct Redis cache update. | Invalidate via Yandex Passport active sessions console; re-run `sync_yandex_cookie.py`. |
| **DeepSeek API Key** | Quarterly (90 days) | Generate new key in DeepSeek Console -> update `.env` on host -> `docker compose restart solver`. | Revoke key in DeepSeek dashboard; replace with emergency backup key. |
| **Telegram Bot Token** | Semi-annually (180 days) | Request new token from `@BotFather` -> update `.env` -> `docker compose restart bot api`. | Revoke immediately in `@BotFather` `/revoke` command. |
| **Internal `API_SECRET_KEY`** | Annual (365 days) | Generate 32-byte cryptographically secure random token (`openssl rand -hex 32`) -> update `.env` across all services. | Replace `.env` and execute zero-downtime rolling restart of `api`, `bot`, `worker`, `solver`. |

---

## 5. Token Lifecycles & TTL Policies

All transient authorization tokens enforce deterministic expiration bounds:

- **Telegram Mini App Session Tokens**: Enforce cryptographic validation with a maximum age of `SESSION_MAX_AGE_SECONDS=86400` (24 hours). Expired session payloads are immediately rejected with `401 Unauthorized`.
- **Redis Operational Cache Keys**:
  - Timetable data: `SCHEDULE_CACHE_TTL_SECONDS=60` (dynamic invalidation on upstream update).
  - Student and mark cache: `STUDENTS_CACHE_TTL_SECONDS=86400` (24h), `MARKS_CACHE_TTL_SECONDS=2592000` (30 days).
  - Distributed Lock keys: `REDIS_CACHE_TTL_SECONDS=600` with automated Lua unlinking.
- **Tester Personal API Keys**: Prefixed with `API_TESTER_KEY_PREFIX=para_test_`, audited in Redis whitelist sets (`REDIS_TESTERS_KEY`), and revocable instantly via administrative command without server restart.

---

## 6. PII Protection & Data Retention Policy

In compliance with student data privacy requirements and educational data regulations:

- **Zero-Storage for Raw Media**: Voice messages and video circles submitted for transcription are processed strictly in RAM (`/dev/shm`) and immediately purged via `cleanup_temp_file()` upon inference completion. No audio samples are persisted to disk or sent to third-party providers.
- **Student Attendance Records**: Attendance logs are synchronized directly with institutional spreadsheet mirrors. Local cached JSON snapshots enforce an automatic retention cutoff of 90 days.
- **Audit Logging Hygiene**: Structured application logs (`logs/*.log`) mask user tokens, full passport sessions, and raw homework prompt attachments. Logs are rotated with a maximum file size of 10MB and retained for at most 3 cycles (`max-file: 3`).
- **Data Subject Rights & Deletion**: Telegram user IDs and associated cache records can be permanently expunged upon user command `/forget_me` or direct request to maintainers.
