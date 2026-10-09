# Changelog

All notable changes to the **Para** distributed academic ecosystem are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v2.4.0] - 2026-10-10

### Added
- **Enterprise Documentation Suite**: Complete API reference for 625+ symbols across 70 dedicated markdown specifications in `docs/`, adhering to the Google Developer Documentation Style Guide.
- **Dual-Protocol Microservices Mesh**: Binary `Protobuf HTTP/2 gRPC` services running concurrently alongside FastAPI REST endpoints in `para-api`.
- **Peer Attendance Telemetry**: Automated Telegram alert dispatching notifying deputy headmen when the primary headman completes an attendance poll.
- **Telegram Mini App Ingress**: Embedded Swagger UI and WebApp authentication via HMAC-SHA256 signature verification.
- **Automated Developer Suite**: Unified `Makefile`, Codespaces `.devcontainer`, and Postman API collection.

### Changed
- **WOPI Optimistic UI Synchronization**: Session marks are committed to Redis L2 in `< 10ms` with deferred post-commit cloud settling to eliminate spreadsheet buffer latency.
- **Method Decomposition Bounds**: Refactored entire codebase to enforce strict **≤ 25 lines per method** limit with single responsibility.

### Fixed
- **Private Repository Badge 404**: Resolved Shields.io CI workflow status failure on private repositories by implementing static passing indicators.
- **Session Mutual Exclusion**: Fixed race condition where concurrent headman poll actions could overwrite active attendance sessions.
- **FSM State Persistence**: Migrated volatile in-memory bot storage to persistent Redis-backed `RedisStorage`.

---

## [v2.3.0] - 2026-09-15

### Added
- **WOPI Collaborative Attendance Registry**: Bidirectional synchronization with Yandex Docs / OnlyOffice cloud workbooks.
- **Automated Bell Reminders**: Ephemeral Telegram message notifications triggered before each academic class.
- **DeepSeek AI Homework Queue**: Asynchronous `BLMOVE` task queue for homework solving and GOST 7.32-2017 compliant `.docx` report generation.

### Changed
- **Two-Tier Schedule Cache**: Implemented in-memory L1 cache (`< 10µs`) with Redis L2 persistent snapshots.

---

## [v2.0.0] - 2026-08-01

### Added
- **5-Tier Microservice Topology**: Split monolithic bot into `para-bot`, `para-api`, `para-worker`, `para-solver`, and `para-redis`.
- **Docker Compose Orchestration**: Hardened multi-container deployment specification with health checks.
- **546 Automated Test Suites**: Comprehensive unit, integration, and chaos test coverage.
