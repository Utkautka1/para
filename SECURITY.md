# Security Policy

## 1. Supported Versions

Security patches and dependency updates are applied exclusively to the `main` branch.

| Version | Supported | Release Date | Status |
| :--- | :--- | :--- | :--- |
| `v2.4.x` | :white_check_mark: | October 2026 | Active Production (Dual-Protocol Mesh) |
| `v2.3.x` | :x: | September 2026 | Deprecated |
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

- **Cryptographic Authentication**: Telegram Mini App endpoints require HMAC-SHA256 signature verification matching the Bot token with replay mitigation (`auth_date` validation within `SESSION_MAX_AGE_SECONDS`).
- **AST Security Scanning**: Automated Bandit security scans execute on every pull request to detect socket leaks, weak cryptography, and unsafe serialization.
- **Network Isolation**: Docker containers communicate solely over internal bridge networks with zero host port exposure on `0.0.0.0`.
- **Secret Isolation**: All credentials, tokens, and keys are strictly injected via `.env` with type-safe validation in `config.py`. Zero secrets are stored in Git.
