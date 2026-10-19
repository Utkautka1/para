# 🏛️ Enterprise Engineering Portal: API & Subsystems Reference

> Comprehensive, unabridged API and architectural specification for all 625+ system symbols.

## Subsystem Catalogs & Architectural Boundaries

| Subsystem | Source Module | Specification Reference | Architectural Layer |
| :--- | :--- | :--- | :--- |
| `AI Homework Flow` | [`bot/handlers/user/hw_solver.py`](../bot/handlers/user/hw_solver.py) | [📖 View Specification](bot/handlers_user_hw_solver.md) | Enterprise Service Component |
| `AI Prompt Sanitization` | [`core/prompt_sanitizer.py`](../core/prompt_sanitizer.py) | [📖 View Specification](core/prompt_sanitizer.md) | Enterprise Service Component |
| `AI Queue Consumer` | [`solver.py`](../solver.py) | [📖 View Specification](entrypoints/solver.md) | Enterprise Service Component |
| `Admin Control Panel` | [`bot/handlers/admin/panel.py`](../bot/handlers/admin/panel.py) | [📖 View Specification](bot/handlers_admin_panel.md) | Enterprise Service Component |
| `Admin Panel Keyboards` | [`bot/templates/admin/keyboards.py`](../bot/templates/admin/keyboards.py) | [📖 View Specification](bot/templates_admin_keyboards.md) | Enterprise Service Component |
| `Atomic Storage Engine` | [`utils/storage.py`](../utils/storage.py) | [📖 View Specification](utils/storage.md) | Enterprise Service Component |
| `Attendance API` | [`api/router/attendance.py`](../api/router/attendance.py) | [📖 View Specification](api/router_attendance.md) | Enterprise Service Component |
| `Attendance Keyboards` | [`bot/templates/admin/attendance.py`](../bot/templates/admin/attendance.py) | [📖 View Specification](bot/templates_admin_attendance.md) | Enterprise Service Component |
| `Attendance Operations` | [`services/attendance_manager.py`](../services/attendance_manager.py) | [📖 View Specification](services/attendance_manager.md) | Enterprise Service Component |
| `Automated Backup Engine` | [`services/backup_manager.py`](../services/backup_manager.py) | [📖 View Specification](services/backup_manager.md) | Enterprise Service Component |
| `Background Daemon` | [`worker.py`](../worker.py) | [📖 View Specification](entrypoints/worker.md) | Enterprise Service Component |
| `Ban Duration Parser` | [`utils/mute_parser.py`](../utils/mute_parser.py) | [📖 View Specification](utils/mute_parser.md) | Enterprise Service Component |
| `Birthdays API` | [`api/router/birthdays.py`](../api/router/birthdays.py) | [📖 View Specification](api/router_birthdays.md) | Enterprise Service Component |
| `Bot Auth Filters` | [`bot/filters/auth.py`](../bot/filters/auth.py) | [📖 View Specification](bot/filters_auth.md) | Enterprise Service Component |
| `Bot Instance Singleton` | [`core/bot.py`](../core/bot.py) | [📖 View Specification](core/bot.md) | Enterprise Service Component |
| `Bot Menu Registry` | [`bot/commands.py`](../bot/commands.py) | [📖 View Specification](bot/commands.md) | Enterprise Service Component |
| `Classmates API` | [`api/router/classmates.py`](../api/router/classmates.py) | [📖 View Specification](api/router_classmates.md) | Enterprise Service Component |
| `Cloud DOCX Parser` | [`integrations/docx_parser.py`](../integrations/docx_parser.py) | [📖 View Specification](integrations/docx_parser.md) | Enterprise Service Component |
| `Cloudflare Tunnel Syncer` | [`scripts/tunnel_sync.py`](../scripts/tunnel_sync.py) | [📖 View Specification](scripts/tunnel_sync.md) | Enterprise Service Component |
| `DeepSeek LLM Integration` | [`integrations/deepseek.py`](../integrations/deepseek.py) | [📖 View Specification](integrations/deepseek.md) | Enterprise Service Component |
| `Distributed L2 Cache` | [`core/redis_cache.py`](../core/redis_cache.py) | [📖 View Specification](core/redis_cache.md) | Enterprise Service Component |
| `Domain Configuration Models` | [`core/config_models.py`](../core/config_models.py) | [📖 View Specification](core/config_models.md) | Enterprise Service Component |
| `Domain Models` | [`services/models.py`](../services/models.py) | [📖 View Specification](services/models.md) | Enterprise Service Component |
| `Examination Parser` | [`services/exam_parser.py`](../services/exam_parser.py) | [📖 View Specification](services/exam_parser.md) | Enterprise Service Component |
| `Examination Topic` | [`services/exam_topic_updater.py`](../services/exam_topic_updater.py) | [📖 View Specification](services/exam_topic_updater.md) | Enterprise Service Component |
| `Exams API` | [`api/router/exams.py`](../api/router/exams.py) | [📖 View Specification](api/router_exams.md) | Enterprise Service Component |
| `Faculty Registry` | [`services/custom_teachers.py`](../services/custom_teachers.py) | [📖 View Specification](services/custom_teachers.md) | Enterprise Service Component |
| `Fallback Auth Flow` | [`bot/handlers/user/auth_fallback.py`](../bot/handlers/user/auth_fallback.py) | [📖 View Specification](bot/handlers_user_auth_fallback.md) | Enterprise Service Component |
| `GOST Document Generator` | [`utils/doc_generator.py`](../utils/doc_generator.py) | [📖 View Specification](utils/doc_generator.md) | Enterprise Service Component |
| `Global Error Trapper` | [`bot/handlers/errors.py`](../bot/handlers/errors.py) | [📖 View Specification](bot/handlers_errors.md) | Enterprise Service Component |
| `HMAC-SHA256 Auth` | [`utils/miniapp_auth.py`](../utils/miniapp_auth.py) | [📖 View Specification](utils/miniapp_auth.md) | Enterprise Service Component |
| `HW Solver API` | [`api/router/solver.py`](../api/router/solver.py) | [📖 View Specification](api/router_solver.md) | Enterprise Service Component |
| `Headman Attendance Polling` | [`bot/handlers/admin/attendance.py`](../bot/handlers/admin/attendance.py) | [📖 View Specification](bot/handlers_admin_attendance.md) | Enterprise Service Component |
| `Healthcheck API` | [`api/router/health.py`](../api/router/health.py) | [📖 View Specification](api/router_health.md) | Enterprise Service Component |
| `Incident Alerting` | [`services/alerting.py`](../services/alerting.py) | [📖 View Specification](services/alerting.md) | Enterprise Service Component |
| `Ingress Gateway` | [`api.py`](../api.py) | [📖 View Specification](entrypoints/api.md) | Enterprise Service Component |
| `Internal RPC Client` | [`core/api_client.py`](../core/api_client.py) | [📖 View Specification](core/api_client.md) | Enterprise Service Component |
| `KTMU Timetable Engine` | [`services/schedule_parser.py`](../services/schedule_parser.py) | [📖 View Specification](services/schedule_parser.md) | Enterprise Service Component |
| `Live Schedule Topic` | [`services/topic_updater.py`](../services/topic_updater.py) | [📖 View Specification](services/topic_updater.md) | Enterprise Service Component |
| `MiniApp API` | [`api/router/miniapp.py`](../api/router/miniapp.py) | [📖 View Specification](api/router_miniapp.md) | Enterprise Service Component |
| `Moderation Ban Engine` | [`bot/handlers/admin/mute.py`](../bot/handlers/admin/mute.py) | [📖 View Specification](bot/handlers_admin_mute.md) | Enterprise Service Component |
| `Network Retry Middleware` | [`bot/middlewares/retry.py`](../bot/middlewares/retry.py) | [📖 View Specification](bot/middlewares_retry.md) | Enterprise Service Component |
| `Notification Dispatcher` | [`services/notifier.py`](../services/notifier.py) | [📖 View Specification](services/notifier.md) | Enterprise Service Component |
| `Prometheus Metrics API` | [`api/router/metrics.py`](../api/router/metrics.py) | [📖 View Specification](api/router_metrics.md) | Enterprise Service Component |
| `Prometheus Metrics Engine` | [`core/metrics.py`](../core/metrics.py) | [📖 View Specification](core/metrics.md) | Enterprise Service Component |
| `Protobuf Converters` | [`api/grpc/converters.py`](../api/grpc/converters.py) | [📖 View Specification](api/grpc_converters.md) | Enterprise Service Component |
| `Public Sharing Flow` | [`bot/handlers/user/public_copy.py`](../bot/handlers/user/public_copy.py) | [📖 View Specification](bot/handlers_user_public_copy.md) | Enterprise Service Component |
| `RBAC Security` | [`services/classmates_auth.py`](../services/classmates_auth.py) | [📖 View Specification](services/classmates_auth.md) | Enterprise Service Component |
| `REST Request Handlers` | [`api/handlers.py`](../api/handlers.py) | [📖 View Specification](api/handlers.md) | Enterprise Service Component |
| `Redis Engine` | [`core/redis.py`](../core/redis.py) | [📖 View Specification](core/redis.md) | Enterprise Service Component |
| `Relational SQLite Engine` | [`core/database.py`](../core/database.py) | [📖 View Specification](core/database.md) | Enterprise Service Component |
| `Resilience & Circuit Breaker` | [`core/circuit_breaker.py`](../core/circuit_breaker.py) | [📖 View Specification](core/circuit_breaker.md) | Enterprise Service Component |
| `SQLite Domain Models` | [`db/sqlite/models.py`](../db/sqlite/models.py) | [📖 View Specification](db/sqlite_models.md) | Enterprise Service Component |
| `SQLite Repositories` | [`db/sqlite/repositories.py`](../db/sqlite/repositories.py) | [📖 View Specification](db/sqlite_repositories.md) | Enterprise Service Component |
| `Schedule API` | [`api/router/schedule.py`](../api/router/schedule.py) | [📖 View Specification](api/router_schedule.md) | Enterprise Service Component |
| `Security Dependencies` | [`api/deps.py`](../api/deps.py) | [📖 View Specification](api/deps.md) | Enterprise Service Component |
| `Session Keepalive` | [`integrations/yandex_keepalive.py`](../integrations/yandex_keepalive.py) | [📖 View Specification](integrations/yandex_keepalive.md) | Enterprise Service Component |
| `Solver Delivery & Reporting` | [`services/solver/telegram_reporter.py`](../services/solver/telegram_reporter.py) | [📖 View Specification](services/solver_telegram_reporter.md) | Enterprise Service Component |
| `Solver Payload Ingestion` | [`services/solver/payload_extractor.py`](../services/solver/payload_extractor.py) | [📖 View Specification](services/solver_payload_extractor.md) | Enterprise Service Component |
| `Solver Queue Processing` | [`services/solver/task_processor.py`](../services/solver/task_processor.py) | [📖 View Specification](services/solver_task_processor.md) | Enterprise Service Component |
| `Solver Security Facade` | [`services/solver/prompt_sanitizer.py`](../services/solver/prompt_sanitizer.py) | [📖 View Specification](services/solver_prompt_sanitizer.md) | Enterprise Service Component |
| `Speech-to-Text Whisper Engine` | [`services/transcriber.py`](../services/transcriber.py) | [📖 View Specification](services/transcriber.md) | Enterprise Service Component |
| `Spreadsheet Analytics` | [`services/attendance_stats.py`](../services/attendance_stats.py) | [📖 View Specification](services/attendance_stats.md) | Enterprise Service Component |
| `Student Identity Cache` | [`services/user_cache.py`](../services/user_cache.py) | [📖 View Specification](services/user_cache.md) | Enterprise Service Component |
| `Student Lifecycle` | [`services/birthday_manager.py`](../services/birthday_manager.py) | [📖 View Specification](services/birthday_manager.md) | Enterprise Service Component |
| `Subscriber Store` | [`db/subscribers.py`](../db/subscribers.py) | [📖 View Specification](db/subscribers.md) | Enterprise Service Component |
| `Subscribers API` | [`api/router/subscribers.py`](../api/router/subscribers.py) | [📖 View Specification](api/router_subscribers.md) | Enterprise Service Component |
| `Supergroup Alert Dispatch` | [`bot/handlers/admin/ping_all.py`](../bot/handlers/admin/ping_all.py) | [📖 View Specification](bot/handlers_admin_ping_all.md) | Enterprise Service Component |
| `System Admin API` | [`api/router/system.py`](../api/router/system.py) | [📖 View Specification](api/router_system.md) | Enterprise Service Component |
| `System Configuration` | [`config.py`](../config.py) | [📖 View Specification](entrypoints/config.md) | Enterprise Service Component |
| `Teachers API` | [`api/router/teachers.py`](../api/router/teachers.py) | [📖 View Specification](api/router_teachers.md) | Enterprise Service Component |
| `Telegram Gateway` | [`bot.py`](../bot.py) | [📖 View Specification](entrypoints/bot.md) | Enterprise Service Component |
| `Telemetry Logging` | [`core/logger.py`](../core/logger.py) | [📖 View Specification](core/logger.md) | Enterprise Service Component |
| `Telemetry Topic` | [`services/attendance_topic_updater.py`](../services/attendance_topic_updater.py) | [📖 View Specification](services/attendance_topic_updater.md) | Enterprise Service Component |
| `Tester Keyboards & States` | [`bot/templates/admin/testers.py`](../bot/templates/admin/testers.py) | [📖 View Specification](bot/templates_admin_testers.md) | Enterprise Service Component |
| `Tester Management Flow` | [`bot/handlers/admin/testers.py`](../bot/handlers/admin/testers.py) | [📖 View Specification](bot/handlers_admin_testers.md) | Enterprise Service Component |
| `Testing Whitelist` | [`services/testers_manager.py`](../services/testers_manager.py) | [📖 View Specification](services/testers_manager.md) | Enterprise Service Component |
| `Throttling Middleware` | [`bot/middlewares/throttling.py`](../bot/middlewares/throttling.py) | [📖 View Specification](bot/middlewares_throttling.md) | Enterprise Service Component |
| `User Attendance Flow` | [`bot/handlers/user/attendance.py`](../bot/handlers/user/attendance.py) | [📖 View Specification](bot/handlers_user_attendance.md) | Enterprise Service Component |
| `User Inline Keyboards` | [`bot/templates/user/keyboards.py`](../bot/templates/user/keyboards.py) | [📖 View Specification](bot/templates_user_keyboards.md) | Enterprise Service Component |
| `User Message Formatter` | [`bot/templates/user/messages.py`](../bot/templates/user/messages.py) | [📖 View Specification](bot/templates_user_messages.md) | Enterprise Service Component |
| `User Schedule Flow` | [`bot/handlers/user/schedule.py`](../bot/handlers/user/schedule.py) | [📖 View Specification](bot/handlers_user_schedule.md) | Enterprise Service Component |
| `Voice Message Templates` | [`bot/templates/user/voice.py`](../bot/templates/user/voice.py) | [📖 View Specification](bot/templates_user_voice.md) | Enterprise Service Component |
| `Voice Transcription Handler` | [`bot/handlers/user/voice_transcribe.py`](../bot/handlers/user/voice_transcribe.py) | [📖 View Specification](bot/handlers_user_voice_transcribe.md) | Enterprise Service Component |
| `WOPI Cloud Service` | [`integrations/yandex_docs.py`](../integrations/yandex_docs.py) | [📖 View Specification](integrations/yandex_docs.md) | Enterprise Service Component |
| `gRPC HTTP/2 Server` | [`api/grpc/server.py`](../api/grpc/server.py) | [📖 View Specification](api/grpc_server.md) | Enterprise Service Component |
| `gRPC RPC Servicers` | [`api/grpc/servicers.py`](../api/grpc/servicers.py) | [📖 View Specification](api/grpc_servicers.md) | Enterprise Service Component |

---
*Authored under Google Developer Documentation Style Guide standards. 100% Technical English.*
