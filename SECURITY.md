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

