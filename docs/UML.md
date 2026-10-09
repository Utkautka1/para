# Architecture Specification for «para»

Technical specification of the distributed system architecture, end-to-end data flows, object models, and execution lifecycles for the Telegram group bot, timetable API service, and background workers.

---

## Table of Contents

1. [System Services Architecture & Core Contracts](#1-system-services-architecture--core-contracts)
2. [Domain Models & Service Contracts Diagram](#2-domain-models--service-contracts-diagram)
3. [End-to-End Flow: Schedule Query & L2 Caching](#3-end-to-end-flow-schedule-query--l2-caching)
4. [End-to-End Flow: Bell Notifications & Topic Auto-Cleanup](#4-end-to-end-flow-bell-notifications--topic-auto-cleanup)
5. [End-to-End Flow: Reliable AI Homework Solver Queue](#5-end-to-end-flow-reliable-ai-homework-solver-queue)
6. [End-to-End Flow: Electronic Attendance Registry (WOPI)](#6-end-to-end-flow-electronic-attendance-registry-wopi)
7. [Data Models & Redis Storage Structure](#7-data-models--redis-storage-structure)
8. [User Interaction Flows & Per-Button Architecture Diagrams](#8-user-interaction-flows--per-button-architecture-diagrams)
   - 8.1. [Command /start & Classmate Onboarding Flow](#81-command-start--classmate-onboarding-flow)
   - 8.2. [Button «📅 Сегодня» (sched:today) Ingress Flow](#82-button-сегодня-schedtoday-ingress-flow)
   - 8.3. [Button «📆 Завтра» (sched:tomorrow) Ingress Flow](#83-button-завтра-schedtomorrow-ingress-flow)
   - 8.4. [Buttons «⏭ Неделя (След.)» & «⏮ Неделя (Тек.)» Flow](#84-buttons-неделя-след--неделя-тек-schedweek--schedweek_next)
   - 8.5. [Button «🔄 Обновить» (sched:refresh) Force Sync Flow](#85-button-обновить-schedrefresh-force-sync-flow)
   - 8.6. [Button «🔔/🔕 Напоминания» (sched:toggle_notify) Subscription Flow](#86-button-bell-напоминания-schedtoggle_notify-subscription-flow)
   - 8.7. [Command /my_attendance & Button «🔄 Обновить мои данные» Flow](#87-command-my_attendance--button-обновить-мои-данные-attmy_refresh)
   - 8.8. [Headman Attendance Flow: Command /attendance & Mark Buttons](#88-headman-attendance-flow-command-attendance--mark-buttons)
   - 8.9. [Remote Lesson Direct Join Button «🔗 N-я пара» Flow](#89-remote-lesson-direct-join-button-n-я-пара-flow)
   - 8.10. [AI Homework Solver Workflow in Topic 405 (DeepSeek & GOST .docx)](#810-ai-homework-solver-workflow-in-topic-405-deepseek--gost-docx)
   - 8.11. [Headman & Admin Control Panel /admin Flow](#811-headman--admin-control-panel-admin-flow)
   - 8.12. [Unauthenticated Ingress & Fallback Flow (auth_fallback.py)](#812-unauthenticated-ingress--fallback-flow-auth_fallbackpy)
   - 8.13. [Global Exception Trapping & User-Facing Error Fallback (errors.py)](#813-global-exception-trapping--user-facing-error-fallback-errorspy)
   - 8.14. [Scoped Interactive Telegram Command Menus (commands.py)](#814-scoped-interactive-telegram-command-menus-commandspy)
   - 8.15. [Distributed Redis FSM Storage & Resilient Fallback (core/bot.py)](#815-distributed-redis-fsm-storage--resilient-fallback-corebotpy)
9. [Dual-Protocol gRPC & Telegram Mini App Swagger UI Architecture](#9-dual-protocol-grpc--telegram-mini-app-swagger-ui-architecture)
   - 9.1. [gRPC Microservices Ingress & Protobuf Multiplexing Flow](#91-grpc-microservices-ingress--protobuf-multiplexing-flow)
   - 9.2. [Telegram Mini App Cryptographic Auth & Embedded Swagger UI Flow](#92-telegram-mini-app-cryptographic-auth--embedded-swagger-ui-flow)
   - 9.3. [Tester Whitelist Management Flow](#93-tester-whitelist-management-flow)
10. [Performance Hardening & Security Audit Architecture](#10-performance-hardening--security-audit-architecture)
   - 10.1. [API Security Boundary & Privilege Escalation Prevention](#101-api-security-boundary--privilege-escalation-prevention)
   - 10.2. [High-Performance Attendance Caching & Thread-Offloading Flow](#102-high-performance-attendance-caching--thread-offloading-flow)
   - 10.3. [Concurrent AI Solver Worker Pipeline with Semaphore Control](#103-concurrent-ai-solver-worker-pipeline-with-semaphore-control)
   - 10.4. [Multi-Tier High-Performance Architecture: L1 In-Memory, uvloop & gRPC Keepalive](#104-multi-tier-high-performance-architecture-l1-in-memory-uvloop--grpc-keepalive)
11. [Automated CI/CD Pipeline & Delivery Verification](#11-automated-cicd-pipeline--delivery-verification)
---

## 1. System Services Architecture & Core Contracts

The architecture diagram outlines the interaction between distributed system components: ingress gateways, dispatchers, business logic microservices, in-memory state stores, and external upstream integrations.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +session AiohttpSession (pool_limit=50)
        +handle_schedule(chat_id, date) void
        +handle_hw_task(student_id, file) void
        +handle_attendance(admin_id) void
        +send_document(chat_id, docx) void
        +send_alert(chat_id, text) int
        +delete_msg(chat_id, msg_id) bool
    }

    class RetryAfterMiddleware {
        +__call__(handler, event, data) Any
        +retry_on_flood_control(attempt, delay) Any
    }

    class CallbackThrottleMiddleware {
        -_last_clicks dict
        +__call__(handler, event, data) Any
        -_determine_cooldown(cb_data) float
        -_handle_callback_throttle(event, now) bool
    }

    class DocxParserService {
        -_DOCX_LOCK Lock
        -_CACHE tuple
        +get_teacher_links(force_refresh) dict
        -_fetch_and_cache_teachers(now) dict
        -_is_cache_fresh(now, force) bool
        +parse_docx_xml(docx_bytes) dict
    }

    class ScheduleApiService {
        +get_day_schedule(group, date) DayScheduleResponse
        +get_week_schedule(group, week) WeekScheduleResponse
        +get_exams(group) ExamsResponse
        +refresh_schedule_in_background(force) void
    }

    class TopicWorkerService {
        +run_check_cycle() void
        +topic_sync_loop() void
        +sync_topic_main_message(force_refresh, target_date) bool
        +resolve_target_date(now_dt, ignore_restriction) date
        +get_next_working_day(target_date) date
        +is_too_early_to_publish(lessons, now_dt, today, ignore_restriction) bool
        +send_bell_reminder() void
        +cleanup_old_messages() void
    }

    class NotifierService {
        +schedule_lesson_reminder(today, lesson, now_dt) void
        +schedule_attendance_poll(today, lesson, now_dt) void
        +send_attendance_prompt(lesson) void
        +auto_close_attendance_session(lesson_num) void
        +send_daily_schedule_job() void
    }

    class HomeworkSolverService {
        +run_consumer_loop() void
        +recover_stale_tasks() int
        +solve_task(task_data) void
    }

    class WopiAttendanceService {
        +init_session(admin_id) str
        +check_file_info(file_id, token) dict
        +get_file(file_id, token) bytes
        +put_file(file_id, content, token) bool
        +check_session_ownership(session, user_id) bool
    }

    class BirthdayService {
        +check_and_send_birthday_congratulations(bot) void
        +is_morning_congrats_time(now_dt) bool
        +format_birthday_registry_text() str
    }

    class ClassmatesAuthService {
        +is_authorized_user(user) bool
        +find_classmate_by_tg_id(user_id) dict
        +find_unregistered_by_username(username) dict
        +update_classmate_tg_id(username, tg_id) dict
        +process_user_auth(user) tuple
    }

    class ExamTopicUpdater {
        +sync_exam_topic_message(force_refresh) bool
        +get_effective_semester_start() date
        +get_default_semester_start() date
        +format_exams_schedule_message(exams, sem_start) str
    }

    class DeepSeekIntegrationModule {
        +solve_homework(image_bytes, prompt) str
        +build_deepseek_messages(prompt, b64_img) list
        +sanitize_prompt_input(text) str
        +get_deepseek_client() AsyncOpenAI
        +close_deepseek_client() void
    }

    class RedisStateManager {
        +get_snapshot(key) dict
        +set_snapshot(key, data, ttl) void
        +push_task(queue, item) void
        +pop_hw_task(timeout) dict
        +ack_hw_task(task_data) void
        +nack_hw_task(task_data, max_retries) bool
        +recover_stale_hw_tasks() int
        +redis_lock(key, ttl) AsyncGenerator
        +zadd_cleanup(set, score, item) void
        +zpop_expired(set, max_score) list
    }

    class KTMUProvider {
        +fetch_all_schedule() json
    }

    class DeepSeekProvider {
        +generate_solution(prompt) str
    }

    class YandexOfficeProvider {
        +open_web_editor(token) html
        +read_disk_xlsx(path) bytes
        +write_disk_xlsx(path, data) bool
    }

    CallbackThrottleMiddleware --> TelegramGateway : debounces rapid inline-clicks & prevents handler flooding
    RetryAfterMiddleware --> TelegramGateway : wraps ingress updates & transparent 429 backoff
    TelegramGateway --> ScheduleApiService : HTTP GET schedule
    TelegramGateway --> RedisStateManager : LPUSH HW queue
    TelegramGateway --> WopiAttendanceService : POST init session
    TopicWorkerService --> ScheduleApiService : query today schedule
    TopicWorkerService --> RedisStateManager : verify flags and ZSET
    TopicWorkerService --> TelegramGateway : publish bell reminders
    NotifierService --> TelegramGateway : send personal reminders and polls
    NotifierService --> ScheduleApiService : fetch daily schedule for broadcasts
    ScheduleApiService --> RedisStateManager : L2 snapshot cache
    ScheduleApiService --> DocxParserService : singleflight contact sync (30s cooldown)
    DocxParserService --> YandexOfficeProvider : public disk download
    ScheduleApiService ..> KTMUProvider : parse upstream on cache miss
    HomeworkSolverService --> RedisStateManager : BLMOVE HW queue
    HomeworkSolverService --> DeepSeekProvider : generate step solution
    HomeworkSolverService --> TelegramGateway : send docx to student
    WopiAttendanceService --> RedisStateManager : token validation
    WopiAttendanceService --> YandexOfficeProvider : spreadsheet sync
```

### Architectural Principles

1. **Decoupled Ingress & Asynchronous Queuing**: The Telegram Gateway never blocks on compute-heavy tasks or document rendering. Inbound student homework is atomically placed onto Redis queues (`LPUSH`) and acknowledged instantly. Attendance commit to Yandex Documents runs asynchronously via background worker tasks (`_async_commit_and_update`), immediately returning interactive feedback to group admins.
2. **Network Resilience & Connection Pooling**: Telegram API outbound calls operate over a persistent `AiohttpSession` pool (concurrency limit 50, keepalive), protected by `RetryAfterMiddleware` to transparently handle flood control (HTTP 429 / TelegramRetryAfter).
3. **Thundering Herd & Click Debounce Protection**: `CallbackThrottleMiddleware` intercepts rapid clicks on inline-buttons (cooldown 1.0–4.0s). `DocxParserService` applies `asyncio.Lock` singleflight synchronization and a 30s forced-refresh guard, completely eliminating parallel cache stampedes to Yandex Disk.
4. **Multi-Tier L2 Snapshot Caching**: The Schedule API isolates upstream college infrastructure by serving pre-computed, group-filtered timetable snapshots directly from Redis memory in `<2ms`.
5. **Autonomous Worker Daemons**: Background daemons (`Topic Worker` and `Homework Solver`) operate independently, relying on atomic primitives (`BLMOVE`, `ZRANGEBYSCORE`) to guarantee high availability and fault isolation.

---

## 2. Domain Models & Service Contracts Diagram

This diagram specifies domain model typing, response payloads, service contracts, and inter-module dependencies across the application.

```mermaid
classDiagram
    direction TB

    class Lesson {
        +int period
        +str time_str
        +str subject
        +str lesson_type
        +str teacher
        +bool is_remote
        +str room
        +str address
        +int subgroup
        +bool is_stream
        +str remote_link
        +str remote_passcode
        +str remote_meeting_id
        +number() int
    }

    class ExamItem {
        +str subject
        +str exam_type
        +str teacher
        +str room
        +str address
        +List~int~ weeks
        +int subgroup
        +str format_str
    }

    class DayScheduleResponse {
        +str date
        +str weekday
        +List~Lesson~ lessons
    }

    class WeekScheduleResponse {
        +int week_number
        +List~DayScheduleResponse~ days
    }

    class TeachersResponse {
        +List~str~ teachers
        +int total_count
    }

    class ExamsResponse {
        +str group_name
        +List~ExamItem~ exams
    }

    class RedisPool {
        -ConnectionPool _pool$
        +get_pool()$ ConnectionPool
        +get_client()$ Redis
    }

    class ApiClient {
        -AsyncClient _http_client
        -str base_url
        -Limits limits
        +get_day_schedule(group, date) DayScheduleResponse
        +get_week_schedule(group, week) WeekScheduleResponse
        +get_teachers() TeachersResponse
        +get_exams(group) ExamsResponse
        +close() void
    }

    class ScheduleParser {
        -dict _in_memory_cache
        -float _cache_timestamp
        -float _cooldown_until
        -Timeout _http_timeout
        +fetch_schedule(group) dict
        +refresh_schedule_in_background(force) void
        +_parse_and_clean_payload(content) tuple
        +get_day(group, target_date) List~Lesson~
        +get_week(group, week_num) dict
        +load_schedule_snapshot(group) dict
        +save_schedule_snapshot(group, data) void
    }

    class RedisCacheManager {
        +save_snapshot(group, data) bool
        +load_snapshot(group) dict
        +pop_hw_task(timeout) str
        +ack_hw_task(raw_task) bool
        +recover_stale_hw_tasks() int
        +is_reminder_sent(key) bool
        +mark_reminder_sent(key, ttl) void
        +register_message_for_cleanup(chat_id, msg_id, delay) void
        +get_expired_messages_for_cleanup() list
    }

    class TopicUpdater {
        -int chat_id
        -int topic_id
        +sync_topic_schedule() void
        +send_call_reminder(lesson, call_type) void
        +cleanup_expired_messages() void
        -calculate_current_call(now) dict
    }

    DayScheduleResponse "1" *-- "many" Lesson : contains
    WeekScheduleResponse "1" *-- "many" DayScheduleResponse : contains
    ExamsResponse "1" *-- "many" ExamItem : contains

    ApiClient ..> DayScheduleResponse : returns
    ApiClient ..> WeekScheduleResponse : returns
    ApiClient ..> TeachersResponse : returns
    ApiClient ..> ExamsResponse : returns

    ScheduleParser ..> Lesson : parses
    ScheduleParser ..> RedisPool : L2 cache pool
    ScheduleParser ..> RedisCacheManager : persists snapshot

    TopicUpdater --> ApiClient : requests schedule
    TopicUpdater --> RedisCacheManager : flags and cleanup queue
    TopicUpdater ..> Lesson : renders to topic

    RedisCacheManager --> RedisPool : connection pool
```

---

## 3. End-to-End Flow: Schedule Query & L2 Caching

Pipeline describing data movement when students or background services request group schedules, guaranteeing cold starts under `<2ms`.

```mermaid
classDiagram
    direction TB

    class DayScheduleResponse {
        +str date
        +str weekday
        +List~Lesson~ lessons
    }

    class Lesson {
        +int period
        +str time_str
        +str subject
        +str lesson_type
        +str teacher
        +str room
        +str address
        +int subgroup
    }

    class ScheduleParser {
        -dict _memory_cache
        +get_day(group, date) List~Lesson~
        +get_week(group, week_num) dict
        +load_schedule_snapshot(group) dict
        +save_schedule_snapshot(group, data) void
        +fetch_schedule(group) dict
    }

    class RedisCacheManager {
        +save_snapshot(group, data) bool
        +load_snapshot(group) dict
    }

    class ApiClient {
        -AsyncClient _http
        +get_day_schedule(group, date) DayScheduleResponse
        +get_week_schedule(group, week) WeekScheduleResponse
    }

    class KTMUProvider {
        +fetch_raw_payload() dict
    }

    DayScheduleResponse "1" *-- "many" Lesson : contains
    ApiClient ..> DayScheduleResponse : returns
    ScheduleParser ..> Lesson : parses
    ScheduleParser --> RedisCacheManager : reads and writes snapshot
    ScheduleParser ..> KTMUProvider : downloads on cache miss
```

### Execution Flow & Data Lifecycle

1. **L2 Snapshot Verification**: When `get_day_schedule` is invoked, the parser immediately queries Redis key `sched:group:snapshot`. If the snapshot exists and is valid, structured timetable data is returned in `<2ms` without outbound networking.
2. **Cold Start & Upstream Ingestion**: On cache misses or stale intervals, the parser requests the raw ~50 MB timetable payload from KTMU servers with a 60-second read timeout. Deserialization and group filtering are offloaded to `asyncio.to_thread` to prevent freezing the FastAPI event loop.
3. **Resilience & Cooldown**: In case of network timeouts or upstream outages (including HTTP 5xx/4xx responses like 503), a 5-minute cooldown (`_COOLDOWN_UNTIL`) prevents hammering the upstream server, seamlessly falling back to cached Redis snapshots.
4. **Atomic Persistence & Multi-Level L1/L2 Caching**:
   - The normalized JSON payload is persisted to Redis L2 with a TTL of 14,400 seconds (4 hours).
   - Ingress Telegram bot layer maintains an **L1 Redis Day Cache** (`sched:day_pack:{date}`) for 180 seconds, serving "Today" and "Tomorrow" button transitions instantly (`<2ms`) without internal API HTTP overhead.
   - User authorization filter `ClassmateAuthFilter` utilizes an **In-Memory MTime Cache** of `birthdays.json`, eliminating synchronous disk reads from the event loop during update polling.
   - Outbound personal reminders in `services/notifier.py` execute concurrently via `asyncio.gather` bounded by a 10-slot semaphore.

---

## 4. End-to-End Flow: Bell Notifications & Topic Auto-Cleanup

Execution cycle governing bell reminders, deduplication guards, and message lifecycles inside Telegram forum topics.

```mermaid
classDiagram
    direction TB

    class TopicUpdater {
        -int chat_id
        -int topic_id
        +sync_topic_schedule() void
        +send_call_reminder(lesson, call_type) void
        +cleanup_expired_messages() void
        -calculate_current_call(now) dict
    }

    class RedisCacheManager {
        +is_reminder_sent(key) bool
        +mark_reminder_sent(key, ttl) void
        +register_message_for_cleanup(chat, msg, delay) void
        +get_expired_messages_for_cleanup() list
    }

    class CallNotification {
        +int period
        +str call_type
        +str subject
        +str time_str
        +str room
    }

    class TelegramChat {
        +send_message(chat_id, text) int
        +delete_message(chat_id, msg_id) bool
    }

    TopicUpdater --> RedisCacheManager : delivery flags and ZSET queue
    TopicUpdater --> TelegramChat : sends and deletes bell alerts
    TopicUpdater ..> CallNotification : builds notification
```

### Notification & Auto-Cleanup Logic

1. **Idempotent Bell Alerts**: Every 60 seconds, the worker inspects lesson intervals for the current day. If exactly 10 minutes remain before lesson start/end, it checks `rem:sent:{group}:{date}:{period}:{type}`. If unset, it sets the flag with a 2-hour TTL and posts the alert to the chat.
2. **Expiration Scheduling**: Immediately after sending, the Telegram `message_id` is registered in Redis Sorted Set `topic:cleanup_messages` with a score equal to `timestamp + 900` (15 minutes).
3. **Automated Message Purging**: Each minute, the daemon calls `ZRANGEBYSCORE topic:cleanup_messages -inf {now}`, removes expired messages via Telegram `deleteMessage`, and deletes the entries via `ZREM`.

---

## 5. End-to-End Flow: Reliable AI Homework Solver Queue

Implementation of the **Reliable Queue** pattern guaranteeing **At-Least-Once** task execution via atomic list transitions.

```mermaid
classDiagram
    direction TB

    class HomeworkTask {
        +str task_id
        +int user_id
        +str user_name
        +str task_text
        +str photo_path
        +str created_at
    }

    class RedisCacheManager {
        +push_hw_task(task_json) void
        +pop_hw_task(timeout) dict
        +ack_hw_task(raw_task) void
        +nack_hw_task(task_data, max_retries) bool
        +recover_stale_hw_tasks() int
    }

    class SolverWorker {
        +run() void
        +solve_single(task) void
        +send_result(user_id, docx) void
    }

    class DocxParser {
        +create_docx_from_solution(solution_md) bytes
        -apply_gost_formatting(doc) void
        -add_formatted_formulas(doc, text) void
    }

    class DeepSeekClient {
        +solve_task_prompt(task_text, image_b64) str
    }

    SolverWorker --> RedisCacheManager : BLMOVE and LREM queue operations
    SolverWorker ..> HomeworkTask : deserializes JSON
    SolverWorker --> DeepSeekClient : requests step reasoning
    SolverWorker --> DocxParser : compiles GOST Word document
```

### Reliable Task Processing

1. **Atomic Ingestion (`BLMOVE`)**: The consumer extracts tasks from `hw:tasks:queue` and simultaneously moves them to `hw:tasks:processing`. If the container crashes mid-computation, the task remains preserved in `processing`.
2. **Daemon Crash Recovery**: On startup, `recover_stale_hw_tasks` safely relocates any orphaned tasks from `processing` back to `queue` via atomic `RPOPLPUSH`.
3. **Fault-Tolerant Retries & DLQ**: When a task encounters unrecoverable errors or parsing timeouts, `nack_hw_task` retries up to 3 times before shunting the poisoned task into Dead Letter Queue `hw:tasks:dlq`, alerting admins and keeping the main queue unblocked.
4. **GOST Academic Formatting**: Solved Markdown formulas are translated into Microsoft Word `.docx` documents adhering strictly to Russian academic GOST formatting (Times New Roman 14pt, 1.5 line spacing, 30-15-20-20 mm margins). The task is acknowledged via `LREM` only after document delivery.

---

## 6. End-to-End Flow: Electronic Attendance Registry (WOPI)

Data flow bridging the group administrator, Telegram Bot, FastAPI backend, and Yandex Documents cloud office via the WOPI standard.

```mermaid
classDiagram
    direction TB

    class AttendanceSession {
        +str session_id
        +str group_name
        +date target_date
        +int period
        +int initiator_id
        +str initiator_name
        +int current_idx
        +dict marks
        +check_session_ownership(user_id) bool
    }

    class WopiController {
        +init_attendance(group, date, period) str
        +check_file_info(file_id, access_token) dict
        +get_file(file_id, access_token) bytes
        +put_file(file_id, access_token, body) dict
    }

    class RedisCacheManager {
        +save_attendance_session(id, data, ttl) void
        +get_attendance_session(id) dict
        +mark_attendance_committed(group, date, period) void
    }

    class YandexDiskClient {
        +download_file(remote_path) bytes
        +upload_file(remote_path, content) bool
    }

    class YandexDocsEditor {
        +CheckFileInfo(access_token) dict
        +GetFile(access_token) bytes
        +PutFile(access_token, content) bool
    }

    class AttendanceStatsService {
        +fetch_all_time_attendance(force_refresh) dict
        +parse_workbook_attendance(workbook) dict
        +find_student_attendance(stats, target_name) dict
        +apply_session_optimistic_update(session) dict
        +invalidate_attendance_stats_cache() void
    }

    class AttendanceTopicUpdater {
        +sync_attendance_topic_message(force_refresh) bool
        +recreate_attendance_topic_message() bool
        +format_attendance_topic_message(stats) str
        +attendance_topic_sync_loop() void
    }

    WopiController --> RedisCacheManager : session token validation
    WopiController --> YandexDiskClient : reads and writes xlsx
    WopiController ..> AttendanceSession : parses session context
    YandexDocsEditor --> WopiController : WOPI REST protocol
    AttendanceTopicUpdater --> AttendanceStatsService : requests aggregated metrics
    AttendanceTopicUpdater --> RedisCacheManager : caches snapshot and acquires redis_lock
    AttendanceStatsService --> YandexDiskClient : downloads workbook sheets
```

### WOPI Session Lifecycle & All-Time Registry

1. **Session Provisioning**: When the admin clicks "Mark Attendance", the bot issues a secure access token and creates a session in Redis `att:session:{id}` with a 1-hour TTL.
2. **Cloud Office Interaction**: Yandex Documents connects to the backend:
   - `CheckFileInfo`: verifies write permissions, user identity, and spreadsheet metadata;
   - `GetFile`: streams the binary `.xlsx` spreadsheet loaded from Yandex Disk;
   - `PutFile`: receives and updates the modified spreadsheet directly back to Yandex Disk storage.
3. **Instant Optimistic UI & Non-Blocking Commit**: Upon completing attendance input in the Telegram UI, `apply_session_optimistic_update` immediately adjusts student metrics in Redis and updates the Telegram Topic message within ~1s. An asynchronous task (`_async_commit_and_update`) persists records to the Yandex Table, followed by a delayed 15s settling pass.
4. **All-Time Multi-Month Tally**: `AttendanceStatsService` scans all historical monthly sheets (`СЕНТ`, `ОКТ`, `НОЯБ`, `ДЕК`...), aggregates cumulative counts (`П`, `О`, `У`, `Н`) for each student, and stores the structured result in Redis (`att:stats:all_time`) with a 1-hour TTL. Excused absences (`У`) are considered legitimate and do not lower the academic percentage.
5. **Academic Leagues Dashboard (Thread ID 7025)**: `AttendanceTopicUpdater` maintains an idempotent pinned message in the dedicated Telegram Topic containing the full group ranking divided into 3 Academic Leagues (Gold 90-100%, Silver 60-89%, Risk Zone <60%), clean single-line rows without line-wrapping, and progress bars. Late arrivals are formatted as `N оп` to eliminate optical confusion with the number 10. Background sync adapts between 3 min (daytime 08-19) and 15 min (night).
6. **Student Self-Service (`/my_attendance`)**: Students can check their private cumulative record and percentage of attendance in PM without group disclosure.
7. **Headman Concurrency Isolation**: `create_attendance_session` checks the active session in `att:active_session`. If an uncommitted survey is held by another administrator, creation is rejected (`PermissionError`). All interactive inline callbacks enforce `check_session_ownership(session, cb.from_user.id)` to prevent dual-headman split-brain marking.
8. **Morning Birthday Dispatch & Dynamic Semester Alignment**: Birthday congratulations are restricted to daylight hours (`is_morning_congrats_time`, >= 07:00 MSK). `ExamTopicUpdater` automatically resolves `semesterStart` from the live KTMU timetable payload, supporting dynamic academic calendars without hardcoded date limits.

---

## 7. Data Models & Redis Storage Structure

### Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    DAY_SCHEDULE ||--|{ LESSON : "contains day lessons"
    DAY_SCHEDULE ||--o{ ATTENDANCE_RECORD : "contains records"

    DAY_SCHEDULE {
        date date PK "Lesson date"
        string weekday "Day of week"
        string group_name "Group identifier"
    }

    LESSON {
        int period PK "Slot number (0-5)"
        string time_str "Time interval"
        string subject "Discipline title"
        string lesson_type "Type (Lecture / Lab / Practice)"
        string teacher "Teacher full name"
        boolean is_remote "Remote format flag"
        string room "Classroom number"
        string address "Campus address"
        int subgroup "Subgroup (0 - whole group)"
    }

    ATTENDANCE_RECORD {
        int id PK "Record identifier"
        string student_name "Student full name"
        date date "Lesson date"
        int period "Period number"
        string status "Attendance status"
    }

    EXAM_ITEM {
        int id PK "Exam identifier"
        string subject "Subject name"
        string exam_type "Assessment type"
        string teacher "Instructor name"
        string room "Exam room"
        string weeks "Academic weeks"
    }

    BIRTHDAY_RECORD {
        string student_name PK "Student full name"
        string birthdate "Birthdate (DD.MM)"
        bigint tg_id "Telegram user ID"
    }
```

---

### Redis Key Registry & Storage Lifecycle

Comprehensive registry of all Redis keys, data structures, expiration policies, and lifecycle producers/consumers:

| Key / Key Pattern | Data Structure | TTL | Source / Producer | Consumer / Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `sched:group:snapshot` | String (JSON) | 4 hours | KTMU Server (post-normalization) | Schedule API: serves group schedule in `<2ms` without raw file parsing |
| `hw:tasks:queue` | List (FIFO) | Indefinite | Telegram Bot (students) | Homework Solver: inbound queue of homework tasks |
| `hw:tasks:processing` | List | Indefinite | `hw:tasks:queue` (via `BLMOVE`) | Homework Solver: in-flight task isolation. Purged via `LREM` upon delivery |
| `topic:cleanup_messages` | Sorted Set (ZSET) | Dynamic | Topic Service on alert dispatch | Topic Service: scheduled message collector purged every 60s past 15 min |
| `rem:sent:{group}:{date}:{period}:{type}` | String (flag) | 2 hours | Topic Service before alert dispatch | Bell alert deduplication guard preventing repeats across worker restarts |
| `att:session:{session_id}` | String (JSON) | 1 hour | Backend on headman action | Yandex Documents: ephemeral token validation following WOPI standard |
| `att:committed:{group}:{date}:{period}` | String (flag) | 24 hours | WOPI controller on save | Bot & Worker: confirmation flag that attendance was marked for the lesson |
| `topic:schedule_msg_id:{group}` | String (int) | Indefinite | Bot on initial timetable post | Topic Service: pinned main schedule message ID updated in-place |
| `api:testers:whitelist` | Set (Strings) | Indefinite | Bot / Admin (`/add_tester`) | MiniApp Auth Router: O(1) membership check for authorized Swagger UI testers |

---

## 8. User Interaction Flows & Per-Button Architecture Diagrams

This section specifies the component architecture, data flow contracts, and execution mechanics for every Telegram user action (commands, inline button clicks, background queues, and administrative tools). All diagrams strictly follow the UML Class/Component structure established in Sections 1–3 (`direction TB`), detailing ingress controllers, middleware guards, Redis storage structures, domain DTOs, and upstream integrations. All interface text and technical descriptors are standardized in English, preserving exact Russian button labels (`Button Сегодня`, `Button Завтра`, etc.) for direct mapping to the Telegram user interface.

---

### 8.1 Command /start & Classmate Onboarding Flow

Architecture governing student onboarding, identity verification via group records, session registration, and initial timetable hydration.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_start_command(chat_id, user_id, username) void
        +send_message(chat_id, text, reply_markup) int
        +send_access_denied(chat_id) void
    }

    class ClassmateAuthFilter {
        -_birthdays_cache dict
        -_last_mtime float
        +check(event, user_id) bool
        -_is_admin(user_id) bool
        -_match_student(user_id) dict
    }

    class UserStartHandler {
        +on_start(message) void
        +register_student_session(user_id, username) void
        +dispatch_initial_schedule(chat_id, user_id) void
    }

    class UserCacheManager {
        +register_user(user_id, username, full_name) void
        +is_registered(user_id) bool
        +get_registered_count() int
    }

    class ScheduleApiService {
        +get_day_schedule(group, date) DayScheduleResponse
        +load_snapshot(group) dict
    }

    class RedisCacheManager {
        +sadd(key, member) int
        +get_snapshot(key) dict
        +set_snapshot(key, data, ttl) void
    }

    class ScheduleKeyboardBuilder {
        +get_main_schedule_keyboard(is_subscribed) InlineKeyboardMarkup
    }

    class DayScheduleResponse {
        +str date
        +str weekday
        +List~Lesson~ lessons
    }

    TelegramGateway --> ClassmateAuthFilter : incoming start command update
    ClassmateAuthFilter --> UserStartHandler : authorizes student via birthdays or admin ID
    ClassmateAuthFilter --> TelegramGateway : unauthorized user sends access denied
    UserStartHandler --> UserCacheManager : records active session
    UserCacheManager --> RedisCacheManager : persists to registered users set
    UserStartHandler --> ScheduleApiService : requests today schedule
    ScheduleApiService --> RedisCacheManager : checks L1 today schedule cache
    ScheduleApiService ..> DayScheduleResponse : returns timetable DTO
    UserStartHandler --> ScheduleKeyboardBuilder : attaches buttons Сегодня, Завтра, Неделя След, Обновить, Напоминания
    UserStartHandler --> TelegramGateway : dispatches greeting card and controls
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Authentication Guard**: Ingress updates for `/start` pass through `ClassmateAuthFilter`. The filter cross-checks `user_id` against `data/birthdays.json` using an in-memory mtime cache and validates against `ADMIN_IDS`. Unregistered users receive an immediate polite denial message (`⛔ Access Denied: 1-КПД-3 only`).
2. **Activity Registration**: Verified users are added to the Redis Set `bot:registered_users` via `UserCacheManager`, updating profile metadata without blocking disk writes.
3. **L1 Timetable Hydration**: `ScheduleApiService` queries Redis for `sched:day_pack:{today}`. If present, the payload is retrieved in `<2ms`. If absent, the normalized snapshot is parsed and cached with a 7200s TTL.
4. **Interactive UI Assembly**: `ScheduleKeyboardBuilder` constructs the default inline markup containing buttons `Сегодня`, `Завтра`, `Неделя (След.)`, `Обновить`, and `Напоминания`, delivering a frictionless greeting interface.

---

### 8.2 Button «📅 Сегодня» (sched:today) Ingress Flow

Component architecture handling user requests for the current day's timetable with anti-flood debouncing and in-place DOM updates.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_callback_query(query_id, user_id, data) void
        +edit_message_text(chat_id, msg_id, text, reply_markup) bool
        +answer_callback_query(query_id, toast_text) bool
    }

    class CallbackThrottleMiddleware {
        -_last_clicks dict
        +__call__(handler, event, data) Any
        -_determine_cooldown(cb_data) float
    }

    class TodayCallbackHandler {
        +handle_today(query) void
        -resolve_current_date() date
    }

    class ScheduleApiService {
        +get_day_schedule(group, date) DayScheduleResponse
    }

    class RedisCacheManager {
        +get_day_pack(date) dict
        +set_day_pack(date, pack, ttl) void
    }

    class ScheduleFormatter {
        +format_day_message(day_dto) str
        -render_lesson_badge(lesson) str
        -format_teacher_room(teacher, room) str
    }

    class ScheduleKeyboardBuilder {
        +get_main_schedule_keyboard(is_subscribed) InlineKeyboardMarkup
    }

    class DayScheduleResponse {
        +str date
        +str weekday
        +List~Lesson~ lessons
    }

    TelegramGateway --> CallbackThrottleMiddleware : clicks button Сегодня
    CallbackThrottleMiddleware --> TodayCallbackHandler : throttles rapid clicks with cooldown
    TodayCallbackHandler --> ScheduleApiService : queries schedule for current date
    ScheduleApiService --> RedisCacheManager : reads L1 today schedule cache
    ScheduleApiService ..> DayScheduleResponse : returns day schedule DTO
    TodayCallbackHandler --> ScheduleFormatter : formats lessons, types, and classrooms
    TodayCallbackHandler --> ScheduleKeyboardBuilder : attaches navigation buttons
    TodayCallbackHandler --> TelegramGateway : updates message in place via editMessageText
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Click Debounce & Throttling**: `CallbackThrottleMiddleware` intercepts rapid clicks on Button `📅 Сегодня`. Rapid successive taps (`<0.5s`) trigger an ephemeral alert toast (`⏳ Please wait a moment...`) to protect Telegram rate limits.
2. **Sub-millisecond L1 Retrieval**: `TodayCallbackHandler` reads the pre-computed JSON structure from Redis key `sched:day_pack:{today}`. No outbound HTTP or disk parsing occurs on cache hits.
3. **Visual Formatting**: `ScheduleFormatter` builds the Markdown representation, calculating period badges (e.g., lecture, practice, lab), instructor names, and room numbers.
4. **Zero-Flicker In-Place Edit**: Telegram `editMessageText` replaces the message text without sending a new chat notification, preserving message scroll position.

---

### 8.3 Button «📆 Завтра» (sched:tomorrow) Ingress Flow

Architecture for resolving next-day schedule queries, handling weekend shifts, and injecting remote video conference links.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_callback_query(query_id, user_id, data) void
        +edit_message_text(chat_id, msg_id, text, reply_markup) bool
        +answer_callback_query(query_id, toast_text) bool
    }

    class TomorrowCallbackHandler {
        +handle_tomorrow(query) void
    }

    class AcademicDateResolver {
        +get_tomorrow_date(tz) date
        +is_day_off(target_date) bool
        +get_timezone() timezone
    }

    class ScheduleApiService {
        +get_day_schedule(group, target_date) DayScheduleResponse
    }

    class RedisCacheManager {
        +get_day_pack(date) dict
        +set_day_pack(date, pack, ttl) void
    }

    class ScheduleFormatter {
        +format_day_message(day_dto) str
        +format_weekend_placeholder(target_date) str
    }

    class ScheduleKeyboardBuilder {
        +get_main_schedule_keyboard(is_subscribed) InlineKeyboardMarkup
        +attach_vcs_links(lessons) void
    }

    TelegramGateway --> TomorrowCallbackHandler : clicks button Завтра
    TomorrowCallbackHandler --> AcademicDateResolver : computes target date in Moscow timezone
    AcademicDateResolver --> TomorrowCallbackHandler : evaluates weekend and holiday flag
    TomorrowCallbackHandler --> ScheduleApiService : queries timetable for tomorrow
    ScheduleApiService --> RedisCacheManager : reads L1 tomorrow schedule cache
    TomorrowCallbackHandler --> ScheduleFormatter : renders timetable or weekend resting view
    TomorrowCallbackHandler --> ScheduleKeyboardBuilder : attaches conference links if remote
    TomorrowCallbackHandler --> TelegramGateway : updates message via editMessageText
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Timezone Normalization**: `AcademicDateResolver` computes tomorrow's date anchored to `Europe/Moscow`, regardless of host server timezone.
2. **Weekend & Holiday Detection**: If tomorrow is Sunday or a scheduled holiday, `format_weekend_placeholder` renders an aesthetic rest card without invoking college parsers.
3. **L1 Cache Retrieval**: Timetable data is resolved via `sched:day_pack:{tomorrow}` (TTL 2 hours).
4. **Dynamic VCS Linking**: If any lessons are flagged `is_remote=True`, `ScheduleKeyboardBuilder` dynamically includes direct conference join buttons.

---

### 8.4 Buttons «⏭ Неделя (След.)» & «⏮ Неделя (Тек.)» Flow

Architecture governing multi-day schedule compilation, academic week parity resolution, and bidirectional navigation toggling.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_callback_query(query_id, user_id, data) void
        +edit_message_text(chat_id, msg_id, text, reply_markup) bool
        +answer_callback_query(query_id, toast_text) bool
    }

    class WeekNavigationHandler {
        +handle_week(query, offset_weeks) void
    }

    class AcademicCalendarService {
        +get_monday(offset_weeks) date
        +calculate_week_parity(monday_date) str
        +get_academic_week_number(monday_date) int
    }

    class ScheduleApiService {
        +get_week_schedule(group, monday_date) WeekScheduleResponse
    }

    class RedisCacheManager {
        +get_week_pack(monday_date) dict
        +set_week_pack(monday_date, data, ttl) void
    }

    class WeekScheduleFormatter {
        +format_full_week(week_dto, parity, week_num) str
        -format_day_section(day_dto) str
    }

    class ScheduleKeyboardBuilder {
        +get_week_toggle_keyboard(current_offset) InlineKeyboardMarkup
    }

    class WeekScheduleResponse {
        +int week_number
        +List~DayScheduleResponse~ days
    }

    TelegramGateway --> WeekNavigationHandler : clicks button Неделя След or Неделя Тек
    WeekNavigationHandler --> AcademicCalendarService : computes target Monday and parity
    WeekNavigationHandler --> ScheduleApiService : requests 6 day academic timetable
    ScheduleApiService --> RedisCacheManager : reads L2 week schedule cache
    ScheduleApiService ..> WeekScheduleResponse : returns full week payload
    WeekNavigationHandler --> WeekScheduleFormatter : formats weekly report with dividers
    WeekNavigationHandler --> ScheduleKeyboardBuilder : toggles button between Неделя След and Неделя Тек
    WeekNavigationHandler --> TelegramGateway : updates view via editMessageText
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Calendar Parity Calculation**: `AcademicCalendarService` calculates the Monday date for offset `+0` (current) or `+1` (next) and resolves academic week parity (Numerator/Denominator).
2. **L2 Snapshot Query**: `ScheduleApiService` checks Redis key `sched:week:{monday}` (TTL 14,400s). On hit, all 6 academic days are returned immediately.
3. **Aggregated Rendering**: `WeekScheduleFormatter` compiles all daily schedules into a compact, structured Markdown view separated by clean day headers.
4. **Smart Button Toggling**: The keyboard dynamically adjusts its callback action: when viewing the next week, the button switches to `⏮ Неделя (Тек.)` to allow seamless return.

---

### 8.5 Button «🔄 Обновить» (sched:refresh) Force Sync Flow

Architecture orchestrating cache eviction, upstream college synchronization, singleflight protection, and fallback resilience.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_callback_query(query_id, user_id, data) void
        +answer_callback_query(query_id, toast_text) bool
        +edit_message_text(chat_id, msg_id, text, reply_markup) bool
    }

    class RefreshScheduleHandler {
        +handle_refresh(query) void
    }

    class ScheduleCacheInvalidator {
        +evict_day_cache(date) void
        +evict_week_cache(monday) void
        +evict_group_snapshot(group) void
    }

    class KTMUUpstreamClient {
        +fetch_all_schedule_force() dict
        +parse_and_validate(raw_payload) dict
    }

    class RedisCacheManager {
        +del_keys(key_list) int
        +save_snapshot(group, data) bool
    }

    class ScheduleFormatter {
        +format_day_message(day_dto) str
    }

    class ScheduleKeyboardBuilder {
        +get_main_schedule_keyboard(is_subscribed) InlineKeyboardMarkup
    }

    TelegramGateway --> RefreshScheduleHandler : clicks button Обновить
    RefreshScheduleHandler --> TelegramGateway : displays progress toast checking updates
    RefreshScheduleHandler --> ScheduleCacheInvalidator : triggers force cache eviction
    ScheduleCacheInvalidator --> RedisCacheManager : executes DEL for cached schedule keys
    RefreshScheduleHandler --> KTMUUpstreamClient : fetches raw payload with timeout 60s
    KTMUUpstreamClient --> RedisCacheManager : stores fresh snapshot in Redis
    RefreshScheduleHandler --> ScheduleFormatter : compiles refreshed timetable with timestamp
    RefreshScheduleHandler --> TelegramGateway : updates message via editMessageText
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **User Toast Feedback**: An immediate Telegram `answerCallbackQuery` toast confirms that a live sync is underway (`🔄 Checking KTMU server updates...`).
2. **Targeted Cache Invalidation**: `ScheduleCacheInvalidator` evicts keys matching `sched:day_pack:*` and `sched:week:*` from Redis.
3. **Upstream Ingestion**: `KTMUUpstreamClient` issues an asynchronous HTTP request with a 60-second read timeout. Parsing is executed off-thread (`asyncio.to_thread`).
4. **Fallback Resilience**: If upstream is unreachable (HTTP 5xx/4xx), the handler falls back gracefully to the previous Redis snapshot and alerts the user with a non-blocking toast warning.

---

### 8.6 Button «🔔/🔕 Напоминания» (sched:toggle_notify) Subscription Flow

Architecture handling bell notification toggling with dual persistence across volatile Redis sets and durable disk storage.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_callback_query(query_id, user_id, data) void
        +answer_callback_query(query_id, toast_text) bool
        +edit_message_reply_markup(chat_id, msg_id, reply_markup) bool
    }

    class NotificationToggleHandler {
        +handle_toggle(query) void
        +handle_notice_command(message) void
    }

    class SubscriptionService {
        +toggle_subscription(user_id) bool
        +is_subscribed(user_id) bool
        +get_all_subscribers() list
    }

    class FileStorageManager {
        +read_subscribers_file() list
        +write_subscribers_file(subscribers) void
    }

    class RedisCacheManager {
        +sadd(key, member) int
        +srem(key, member) int
        +sismember(key, member) bool
    }

    class ScheduleKeyboardBuilder {
        +get_main_schedule_keyboard(is_subscribed) InlineKeyboardMarkup
    }

    TelegramGateway --> NotificationToggleHandler : clicks button Напоминания
    NotificationToggleHandler --> SubscriptionService : requests subscription state toggle
    SubscriptionService --> FileStorageManager : persists to disk file subscribers json
    SubscriptionService --> RedisCacheManager : updates volatile subscribers set
    NotificationToggleHandler --> TelegramGateway : alerts user via confirmation toast
    NotificationToggleHandler --> ScheduleKeyboardBuilder : updates button label icon
    NotificationToggleHandler --> TelegramGateway : updates markup without redrawing message text
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Dual Persistence Model**: Subscriptions are toggled in `data/subscribers.json` (durable between container rebuilds) and mirrored to Redis Set `bot:subscribers` (for O(1) checks during automated alerts).
2. **Ephemeral Toast Response**: Telegram `answerCallbackQuery` confirms the new status (`🔔 Reminders enabled: alerts 15 min before class` or `🔕 Reminders disabled`).
3. **Isolated Markup Patching**: By invoking `editMessageReplyMarkup` instead of `editMessageText`, the button icon toggles seamlessly (`🔔` ↔ `🔕`) without message reflow.

---

### 8.7 Command /my_attendance & Button «🔄 Обновить мои данные» Flow

Architecture for student self-service attendance metrics, ensuring private messaging protection, multi-month data aggregation, and excused absence handling.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_my_attendance_command(chat_id, user_id) void
        +handle_refresh_callback(query_id, user_id) void
        +send_message(chat_id, text, reply_markup) int
        +edit_message_text(chat_id, msg_id, text, reply_markup) bool
    }

    class PrivacyGuardFilter {
        +is_private_chat(chat_type) bool
        +redirect_to_private(chat_id, user_id) void
    }

    class MyAttendanceHandler {
        +show_personal_attendance(user_id, chat_id) void
        +refresh_personal_card(query) void
    }

    class ClassmatesDirectory {
        +find_student_by_tg_id(user_id) str
    }

    class AttendanceStatsService {
        +fetch_all_time_attendance(force) dict
        +find_student_attendance(stats, student_name) dict
    }

    class ExcusedAbsencePolicy {
        +is_excused_absence(code) bool
        +calculate_academic_pulse(attended, late, unexcused) float
        +resolve_league(pulse_rate) str
    }

    class PersonalAttendanceFormatter {
        +format_personal_card(student_stats) str
        -render_progress_bar(pulse_rate) str
        -format_monthly_breakdown(months_dict) str
    }

    class AttendanceKeyboardBuilder {
        +get_my_attendance_keyboard() InlineKeyboardMarkup
    }

    TelegramGateway --> PrivacyGuardFilter : enters command my_attendance or clicks button Обновить мои данные
    PrivacyGuardFilter --> MyAttendanceHandler : routes payload to private chat PM
    MyAttendanceHandler --> ClassmatesDirectory : maps user id to student name via birthdays
    MyAttendanceHandler --> AttendanceStatsService : retrieves cumulative all time stats from Redis
    AttendanceStatsService --> ExcusedAbsencePolicy : excused absence excluded from risk zone
    MyAttendanceHandler --> PersonalAttendanceFormatter : compiles league badge and monthly counts
    MyAttendanceHandler --> AttendanceKeyboardBuilder : attaches button Обновить мои данные
    MyAttendanceHandler --> TelegramGateway : delivers private card to student
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Privacy Shield**: If triggered in the public group or topic, `PrivacyGuardFilter` sends a redirect alert in chat and dispatches the actual attendance statistics to the student's Private Messages (PM).
2. **Multi-Month Registry Aggregation**: `AttendanceStatsService` aggregates counts across all workbook sheets (`СЕНТ`, `ОКТ`, `НОЯБ`, `ДЕК`...) from Redis key `att:stats:all_time`.
3. **Excused Absences Business Rule**: Absences marked as `У` (Excused) are legitimate and do not lower the academic percentage or place the student into the Risk Zone.
4. **Personal Card Delivery**: The message renders the student's League (Gold, Silver, Risk), progress bar, total hours, and per-month breakdown, with a refresh button: `Button "🔄 Обновить мои данные"`.

---

### 8.8 Headman Attendance Flow: Command /attendance & Mark Buttons

Architecture governing the headman attendance marking survey, Redis session tracking, undo support, optimistic UI publishing, and cloud synchronization.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_attendance_command(chat_id, user_id) void
        +handle_mark_callback(query_id, user_id, code) void
        +handle_submit_callback(query_id, user_id) void
        +edit_message_text(chat_id, msg_id, text, reply_markup) bool
    }

    class AttendanceAuthFilter {
        +is_headman_or_admin(user_id) bool
    }

    class AttendanceWorkflowHandler {
        +start_survey(user_id, chat_id) void
        +record_student_mark(user_id, status_code) void
        +step_back(user_id) void
        +submit_and_commit(user_id) void
    }

    class AttendanceSessionManager {
        +create_session(headman_id) str
        +record_mark(headman_id, student_name, code) void
        +pop_last_mark(headman_id) void
        +get_session_summary(headman_id) dict
        +close_session(headman_id) void
    }

    class RedisCacheManager {
        +setex(key, ttl, value) void
        +hset(key, field, value) int
        +del_key(key) int
    }

    class AttendanceStepKeyboard {
        +render_step_keyboard(student_idx, total) InlineKeyboardMarkup
    }

    class OptimisticTopicUpdater {
        +apply_session_optimistic_update(session) dict
        +trigger_instant_topic_update(session) void
    }

    class WopiCloudOfficeClient {
        +commit_marks_to_excel_async(session) void
    }

    class PartnerNotificationDispatcher {
        +get_partner_admin_id(current_user_id) int
        +notify_partner_about_attendance(session, stats, user_name) void
        +notify_partner_about_cancellation(lesson_num, user_id, user_name) void
    }

    TelegramGateway --> AttendanceAuthFilter : enters attendance command
    AttendanceAuthFilter --> AttendanceWorkflowHandler : validates headman role
    AttendanceWorkflowHandler --> AttendanceSessionManager : creates session in Redis
    AttendanceSessionManager --> RedisCacheManager : stores state in Redis session key
    AttendanceWorkflowHandler --> AttendanceStepKeyboard : displays controls buttons П, О, У, Н, Назад, Завершить
    TelegramGateway --> AttendanceWorkflowHandler : clicks mark button П or О or У or Н
    AttendanceWorkflowHandler --> AttendanceSessionManager : updates student record and advances index
    TelegramGateway --> AttendanceWorkflowHandler : clicks button Завершить
    AttendanceWorkflowHandler --> OptimisticTopicUpdater : immediately updates attendance topic in 1s
    AttendanceWorkflowHandler --> WopiCloudOfficeClient : triggers background async WOPI PUT commit
    AttendanceWorkflowHandler --> PartnerNotificationDispatcher : asynchronously notifies peer administrator
    PartnerNotificationDispatcher --> TelegramGateway : sends direct DM with detailed stats or cancellation
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Role Verification & Concurrency Control**: `AttendanceAuthFilter` validates headman status. Active survey sessions check `att:active_session` in Redis to prevent multiple headmen from conflicting.
2. **Interactive Survey State Machine**: Each student is presented sequentially with status buttons: `🟢 П` (Present), `🟡 О` (Late), `🔵 У` (Excused), `🔴 Н` (Unexcused), plus `⬅️ Назад` (Undo) and `💾 Завершить` (Submit).
3. **1-Second Optimistic Topic Update**: When the headman submits, `apply_session_optimistic_update` adjusts student statistics in Redis memory and refreshes the pinned Topic message within ~1 second.
4. **Asynchronous Cloud Commit**: `_async_commit_and_update` executes a background task to write records into the remote Excel workbook on Yandex Disk via WOPI without blocking the Telegram bot.
5. **Mutual Headman & Deputy Statistics Notification**: Upon completing the survey or cancelling a lesson, `notify_partner_about_attendance` asynchronously dispatches a comprehensive breakdown (present, late, excused, unexcused counts and names of absent students) directly to the peer administrator's direct messages.

---

### 8.9 Remote Lesson Direct Join Button «🔗 N-я пара» Flow

Component architecture for detecting online classes, mapping instructor credentials, and rendering direct conference launch buttons.

```mermaid
classDiagram
    direction TB

    class ScheduleKeyboardBuilder {
        +attach_remote_call_buttons(lessons) InlineKeyboardMarkup
        -create_url_button(label, url) InlineKeyboardButton
    }

    class RemoteLinkInspector {
        +is_remote_lesson(lesson) bool
        +resolve_platform_name(remote_link) str
        +get_clean_launch_url(lesson) str
    }

    class TeacherContactsDirectory {
        +find_teacher_vcs_link(teacher_name) str
        +match_fallback_platform(subject) str
    }

    class TelegramClientUI {
        +on_url_button_click(url) void
        +open_external_app_or_browser(url) void
    }

    class VideoConferenceSystem {
        +join_session_room(meeting_id) void
    }

    ScheduleKeyboardBuilder --> RemoteLinkInspector : inspects lesson remote attribute
    RemoteLinkInspector --> TeacherContactsDirectory : matches teacher with official conference URL
    RemoteLinkInspector --> ScheduleKeyboardBuilder : builds native URL button Сферум or Телемост
    TelegramClientUI --> VideoConferenceSystem : clicks button Сферум for direct browser launch
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Remote Attribute Parsing**: During timetable formatting, `RemoteLinkInspector` inspects `lesson.is_remote` and checks `lesson.remote_link`.
2. **Directory Matching**: If a link is missing from the raw timetable, `TeacherContactsDirectory` supplies the verified conference link (Sferum, VK Teams, Yandex Telemost, Kontur Talk).
3. **Native Inline URL Buttons**: Buttons are constructed as native Telegram `InlineKeyboardButton(text=..., url=...)`. Clicks execute directly on the student's device without incurring bot webhook latency.

---

### 8.10 AI Homework Solver Workflow in Topic 405 (DeepSeek & GOST .docx)

Component architecture for student homework submissions in dedicated Topic 405, reliable Redis queuing, multimodal reasoning, and academic formatting.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_topic_message(message, topic_id=405) void
        +send_document(chat_id, topic_id, file_bytes, caption) int
        +send_ack_message(chat_id, topic_id, text) int
    }

    class HomeworkTopicHandler {
        +on_homework_submission(message) void
        -validate_input_media(message) bool
    }

    class HomeworkQueueManager {
        +enqueue_task(task_payload) str
        +recover_stale_tasks() int
    }

    class RedisCacheManager {
        +lpush(queue_key, item_json) int
        +blmove(src_queue, dst_queue, timeout) str
        +lrem(queue_key, count, value) int
    }

    class HomeworkSolverWorker {
        +run_consumer_loop() void
        +process_task(task_dict) void
    }

    class DeepSeekVisionClient {
        +solve_task(task_text, image_b64) str
        -format_cot_prompt(task_text) list
    }

    class GostDocxCompiler {
        +create_docx_from_solution(solution_md, subject) bytes
        -apply_gost_formatting(doc) void
        -render_math_formulas(doc, text) void
    }

    TelegramGateway --> HomeworkTopicHandler : student submits task photo or text to Topic 405
    HomeworkTopicHandler --> HomeworkQueueManager : wraps task into DTO
    HomeworkQueueManager --> RedisCacheManager : enqueues task via LPUSH
    HomeworkSolverWorker --> RedisCacheManager : dequeues task via BLMOVE into processing
    HomeworkSolverWorker --> DeepSeekVisionClient : performs OCR and step reasoning
    HomeworkSolverWorker --> GostDocxCompiler : compiles formatted academic docx
    HomeworkSolverWorker --> TelegramGateway : delivers solution document back into Topic 405
    HomeworkSolverWorker --> RedisCacheManager : acknowledges task completion via LREM
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Topic Ingress & Immediate ACK**: Tasks posted in Topic 405 are enqueued in Redis via `LPUSH hw:tasks:queue`. The bot immediately responds with an acknowledgement message.
2. **Atomic Ingestion (`BLMOVE`)**: The worker daemon safely transfers the task into `hw:tasks:processing`. If the container restarts mid-solve, orphaned tasks are automatically recovered.
3. **Multimodal LLM Reasoning**: `DeepSeekVisionClient` extracts handwritten and printed problem statements, generates step-by-step reasoning, and calculates final solutions.
4. **Academic Document Compilation**: `GostDocxCompiler` structures the solution into a Microsoft Word `.docx` file following Russian academic standards (Times New Roman 14pt, 1.5 line spacing, 30-15-20-20 mm margins). The file is sent directly to Topic 405, followed by queue acknowledgement via `LREM`.

---

### 8.11 Headman & Admin Control Panel /admin Flow

Architecture governing the administrative control center, role-based authorization, emergency broadcast tools, manual topic synchronization, and telemetry inspection.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_admin_command(chat_id, user_id) void
        +handle_admin_callback(query_id, user_id, action) void
        +send_message(chat_id, text, reply_markup) int
        +edit_message_text(chat_id, msg_id, text, reply_markup) bool
    }

    class AdminAuthFilter {
        +is_admin(user_id) bool
        -_check_admin_ids(user_id) bool
    }

    class AdminPanelHandler {
        +show_control_panel(chat_id) void
        +dispatch_action(query, action) void
    }

    class AdminKeyboardBuilder {
        +get_admin_keyboard() InlineKeyboardMarkup
    }

    class ScheduleBroadcaster {
        +broadcast_today_schedule() int
    }

    class AttendanceTopicSyncWorker {
        +force_full_topic_resync() bool
    }

    class SystemTelemetryCollector {
        +get_memory_usage() float
        +get_uptime_seconds() float
        +get_redis_queue_depths() dict
    }

    TelegramGateway --> AdminAuthFilter : enters command admin
    AdminAuthFilter --> AdminPanelHandler : verifies user id in admin list
    AdminPanelHandler --> AdminKeyboardBuilder : attaches admin control buttons
    TelegramGateway --> AdminPanelHandler : clicks button Экстренная рассылка
    AdminPanelHandler --> ScheduleBroadcaster : triggers urgent timetable broadcast
    TelegramGateway --> AdminPanelHandler : clicks button Форсировать обновление топика
    AdminPanelHandler --> AttendanceTopicSyncWorker : triggers full resync of attendance topic
    TelegramGateway --> AdminPanelHandler : clicks button Системная статистика
    AdminPanelHandler --> SystemTelemetryCollector : collects uptime and memory usage metrics
    AdminPanelHandler --> TelegramGateway : updates message with system health dashboard
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Role-Based Authorization (RBAC)**: `AdminAuthFilter` validates `user_id` against the immutable `ADMIN_IDS` configuration. Unauthorized access is blocked immediately.
2. **Control Dashboard Rendering**: The administrator is presented with 7 management controls: `📢 Экстренная рассылка`, `🔄 Форсировать обновление топика`, `📊 Системная статистика`, `📋 Экзамены`, `👥 База подписчиков`, and diagnostic tools.
3. **Emergency Schedule Push**: Clicking Button `📢 Экстренная рассылка` initiates an asynchronous broadcast of the day's timetable to all active subscribers via `services/notifier.py` with semaphore concurrency control.
4. **Forced Topic Rebuild**: Clicking Button `🔄 Форсировать обновление топика` triggers a full re-computation of the pinned Topic 7025 message directly from live sheets.
5. **System Telemetry**: Clicking Button `📊 Системная статистика` displays server metrics, active Redis connections, queue lengths, and memory footprint.

---

### 8.12 Unauthenticated Ingress & Fallback Flow (auth_fallback.py)

Architecture safeguarding the group assistant by isolating unauthorized direct messages, extracting caller identity safely, and displaying onboarding diagnostics.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_private_message(user_id, text) void
        +answer_message(chat_id, html_text) Message
    }

    class UnauthFallbackHandler {
        +unauth_fallback(message) void
        -_validate_caller_identity(user) bool
    }

    class ClassmatesAuthService {
        +is_authorized_user(user) bool
        +load_classmates_registry() list
    }

    class TestersManager {
        +is_tester_allowed(user_id) bool
    }

    TelegramGateway --> UnauthFallbackHandler : sends private message
    UnauthFallbackHandler --> ClassmatesAuthService : checks is_authorized_user(user)
    UnauthFallbackHandler --> TestersManager : checks is_tester_allowed(user_id)
    UnauthFallbackHandler --> TelegramGateway : sends access denied message with user_id
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Identity Extraction & Safe Guard**: The handler extracts `uid = user.id` before executing authorization filters and logging, preventing variable binding errors (`NameError`).
2. **Authorized User & Tester Bypass**: If the sender is an authorized classmate or an active API tester (`is_tester_allowed`), the handler silently passes without interruption.
3. **Diagnostic Access Denied Rendering**: For unauthorized strangers, the handler sends a structured HTML card containing the user's numeric `Telegram ID` (`<code>{uid}</code>`), instructing them to forward the ID to the headman for registry binding.

---

### 8.13 Global Exception Trapping & User-Facing Error Fallback (errors.py)

Architecture capturing unexpected exceptions across all router handlers, extinguishing perpetual spinner state on inline buttons, and delivering friendly diagnostics without revealing internal tracebacks.

```mermaid
classDiagram
    direction TB

    class TelegramDispatcher {
        +feed_update(update) void
        +handle_error(event) void
    }

    class GlobalErrorHandlerRouter {
        +global_error_handler(event) bool
        -_log_exception(error) void
        -_answer_stuck_callback(cb) void
        -_notify_user_message(msg) void
    }

    class ErrorEvent {
        +Update update
        +Exception exception
    }

    class TelegramCallbackQuery {
        +answer(text, show_alert) bool
    }

    class TelegramMessage {
        +answer(text) Message
    }

    TelegramDispatcher --> GlobalErrorHandlerRouter : captures unhandled exception
    GlobalErrorHandlerRouter ..> ErrorEvent : unwraps event and exception
    GlobalErrorHandlerRouter --> TelegramCallbackQuery : clears button spinner with show_alert modal
    GlobalErrorHandlerRouter --> TelegramMessage : replies with user-friendly transient error text
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Dispatcher Interception**: Whenever an unhandled exception bubbles up during handler execution, aiogram routes the context to `@router.error()`.
2. **Deterministic Logging**: The error is logged via `core.logger` (`error_handler`) with full diagnostic context without relying on blind traceback printing.
3. **Spinner Relief via Modal Alert**: If the failing update originated from an inline callback button, `cb.answer("⚠️ Временный сбой сервиса. Попробуйте снова.", show_alert=True)` is dispatched, immediately ending the UI loading freeze.
4. **Resilient Network Protection**: Fallback answers are wrapped in protected try/except blocks to guarantee zero unhandled cascade crashes even if Telegram API connection drops.

---

### 8.14 Scoped Interactive Telegram Command Menus (commands.py)

Architecture dynamically registering contextual command suggestions in Telegram client UI via `BotCommandScope`, distinguishing general student commands from privileged administrative operations.

```mermaid
classDiagram
    direction TB

    class BotCommandsRegistry {
        +get_default_user_commands() List~BotCommand~
        +get_admin_commands() List~BotCommand~
        +register_bot_commands(bot) void
    }

    class TelegramBotAPI {
        +set_my_commands(commands, scope) bool
    }

    class BotCommandScopeDefault {
        +String type = "default"
    }

    class BotCommandScopeChat {
        +String type = "chat"
        +int chat_id
    }

    class BotCommand {
        +String command
        +String description
    }

    BotCommandsRegistry --> TelegramBotAPI : registers scoped menu commands
    BotCommandsRegistry ..> BotCommandScopeDefault : applies today, notice, my_attendance, help
    BotCommandsRegistry ..> BotCommandScopeChat : applies admin, attendance, all, testers, swagger to headman
    BotCommandsRegistry ..> BotCommand : creates typed commands
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **User Scope Segregation**: Standard students receive a minimalist, uncluttered menu (`/today`, `/notice`, `/my_attendance`, `/help`) via `BotCommandScopeDefault`.
2. **Privileged Headman Scope**: Chat-scoped commands (`BotCommandScopeChat(chat_id=ALLOWED_USER_ID)`) expose admin workflows (`/admin`, `/attendance`, `/all`, `/testers`, `/swagger`).
3. **Graceful Startup Registration**: Invoked during `main()` bootstrap, non-blocking with error capture to prevent bot launch failure on Telegram rate-limits.

---

### 8.15 Distributed Redis FSM Storage & Resilient Fallback (core/bot.py)

Architecture replacing volatile memory storage with distributed Redis-backed Finite State Machine storage, enabling state preservation across process restarts, deployments, and multi-worker clusters.

```mermaid
classDiagram
    direction TB

    class CoreBotFactory {
        +create_bot_session() AiohttpSession
        +create_fsm_storage() BaseStorage
    }

    class RedisPoolManager {
        +get_redis_pool() ConnectionPool
    }

    class RedisStorage {
        +Redis redis
        +KeyBuilder key_builder
        +set_state(key, state) void
        +get_state(key) State
        +set_data(key, data) void
    }

    class MemoryStorage {
        +dict storage
    }

    class AiogramDispatcher {
        +BaseStorage storage
        +start_polling(bot) void
    }

    CoreBotFactory --> RedisPoolManager : acquires async redis connection pool
    CoreBotFactory --> RedisStorage : instantiates prefix='fsm' distributed storage
    CoreBotFactory ..> MemoryStorage : fallbacks on connection/import fault
    CoreBotFactory --> AiogramDispatcher : initializes dispatcher with resilient storage
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Connection Pooling**: Utilizes shared asynchronous connection pool `get_redis_pool()` to avoid connection exhaustion under high concurrency.
2. **Namespaced Keys**: FSM keys are organized under prefix `fsm:` (`fsm:{chat_id}:{user_id}:state` / `data`), preventing key collision with timetable cache or attendance records.
3. **High-Availability Fallback**: If Redis service is unreachable or uninstalled during standalone test runs, `create_fsm_storage()` seamlessly falls back to `MemoryStorage`.
4. **Graceful Shutdown**: On process exit (`shutdown_bot`), `dp.storage.close()` is awaited to cleanly release active network descriptors and pool slots.

---

## 9. Dual-Protocol gRPC & Telegram Mini App Swagger UI Architecture

The dual-protocol architecture combines a high-speed gRPC server (HTTP/2 binary Protobuf) for internal inter-service communication between `para-bot`, `para-worker`, `para-solver`, and `para-api`, alongside a FastAPI REST engine exposing interactive **Swagger UI** (`/docs`, `/openapi.json`) and a **Telegram Mini App** gateway with cryptographic HMAC-SHA256 verification and Redis whitelist access control.

```mermaid
classDiagram
    direction TB

    class GrpcServerManager {
        -_server aio_Server
        +create_grpc_server() aio_Server
        +start_grpc_server(server, host, port) void
        +stop_grpc_server(server, grace) void
    }

    class ScheduleServiceServicer {
        +GetDaySchedule(request, context) DayScheduleResponse
        +GetWeekSchedule(request, context) WeekScheduleResponse
        -_resolve_day(raw_date) date
        -_resolve_monday(raw_monday) date
    }

    class ExamsServiceServicer {
        +GetExams(request, context) ExamsResponse
    }

    class TeachersServiceServicer {
        +GetTeachers(request, context) TeachersResponse
    }

    class GrpcConverters {
        +lesson_to_proto(lesson) LessonProto
        +proto_to_lesson(proto) Lesson
        +week_days_to_proto(raw_days) list
        +exam_item_to_proto(exam) ExamItemProto
        +proto_to_exam_item(proto) ExamItem
        +teachers_dict_to_proto(raw) TeachersResponse
    }

    class ApiClientGrpc {
        -_CHANNEL aio_Channel
        -_CLIENT AsyncClient
        +_get_grpc_channel() aio_Channel
        +fetch_day_schedule(target_date, force_refresh) dict
        +fetch_week_schedule(monday, force_refresh) dict
        +fetch_exams(force_refresh) dict
        +fetch_teachers(force_refresh) dict
        +close_api_client() void
    }

    class MiniappRouter {
        +serve_miniapp_page() HTMLResponse
        +authenticate_miniapp(payload, response) MiniappAuthResponse
        +check_tester_status(session) MiniappCheckResponse
        +list_api_testers() TesterListResponse
        +api_add_tester(user_id) dict
        +api_remove_tester(user_id) dict
    }

    class MiniappAuthService {
        +validate_telegram_init_data(init_data) dict
        +generate_tester_session(user_id) str
        +verify_tester_session(token, max_age) int
        -_compute_init_data_hash(data_check_str) str
        -_is_auth_date_valid(auth_date_str) bool
    }

    class TestersManager {
        -_ADMIN_TESTERS set
        +add_tester(user_id) bool
        +remove_tester(user_id) bool
        +is_tester_allowed(user_id) bool
        +get_all_testers() list
    }

    class AdminTestersHandler {
        +cmd_list_testers(message) void
        +cmd_add_tester(message) void
        +cmd_del_tester(message) void
        +cmd_open_swagger(message) void
        +cb_admin_testers(callback) void
        +process_tester_id_input(message, state) void
    }

    GrpcServerManager --> ScheduleServiceServicer : registers servicer
    GrpcServerManager --> ExamsServiceServicer : registers servicer
    GrpcServerManager --> TeachersServiceServicer : registers servicer
    ScheduleServiceServicer --> GrpcConverters : converts models
    ExamsServiceServicer --> GrpcConverters : converts models
    TeachersServiceServicer --> GrpcConverters : converts models
    ApiClientGrpc --> ScheduleServiceServicer : RPC HTTP/2 stream
    ApiClientGrpc --> ExamsServiceServicer : RPC HTTP/2 stream
    ApiClientGrpc --> TeachersServiceServicer : RPC HTTP/2 stream
    MiniappRouter --> MiniappAuthService : validates HMAC initData
    MiniappRouter --> TestersManager : checks tester whitelist in Redis
    AdminTestersHandler --> TestersManager : manages whitelist via Bot FSM
```

---

### 9.1. gRPC Microservices Ingress & Protobuf Multiplexing Flow

Architecture governing high-performance binary RPC data exchange between microservices (`para-bot`, `para-worker`, `para-solver`) and `para-api` over HTTP/2 multiplexed streams with low-latency binary serialization.

```mermaid
sequenceDiagram
    autonumber
    actor Caller as para-bot / para-worker
    participant Client as core/api_client.py
    participant Channel as grpc.aio.Channel (:50051)
    participant Servicer as ScheduleServiceServicer
    participant Parser as services/schedule_parser.py
    participant RedisStore as Redis L1/L2 Cache

    Caller->>Client: get_api_schedule_for_date(target_date)
    Client->>Channel: ScheduleServiceStub.GetDaySchedule(DayScheduleRequest)
    Channel->>Servicer: Ingest binary protobuf RPC frame
    Servicer->>Parser: get_schedule_for_date(day, force_refresh)
    Parser->>RedisStore: GET schedule:snapshot / L1 memory cache
    RedisStore-->>Parser: Return cached schedule / live parse
    Parser-->>Servicer: List[Lesson] domain models
    Servicer->>Servicer: lesson_to_proto() converter
    Servicer-->>Channel: DayScheduleResponse (binary frame)
    Channel-->>Client: Receive Protobuf response
    Client->>Client: proto_to_lesson() deserialization
    Client-->>Caller: List[Lesson] Pydantic models
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Persistent Channel Multiplexing**: `ApiClientGrpc` maintains a persistent HTTP/2 connection channel (`grpc.aio.insecure_channel`) directed to `api:50051`, eliminating TCP handshake overhead for recurring timetable checks.
2. **Binary Frame Ingress**: Methods such as `get_api_schedule_for_date` construct typed `DayScheduleRequest` protobuf structures, achieving high compression and zero JSON parsing CPU overhead.
3. **Servicer Dispatch**: `ScheduleServiceServicer.GetDaySchedule` unpacks request parameters, delegates timetable resolution to `services/schedule_parser.py`, and inspects Redis L1/L2 snapshot caches.
4. **Data Mapping & Serialization**: Domain `Lesson` objects are mapped to Protobuf structures by `GrpcConverters.lesson_to_proto`, preserving subgroup partitioning, stream markers, and remote lecture identifiers.
5. **High Availability & HTTP Fallback**: If gRPC experiences communication disruption (`grpc.RpcError`), `ApiClientGrpc` intercepts the error and executes transparent fallback to legacy REST endpoints, ensuring zero downtime for end users.

---

### 9.2. Telegram Mini App Cryptographic Auth & Embedded Swagger UI Flow

Architecture governing cryptographic authentication via Telegram WebApp `initData`, session token minting, and embedding interactive OpenAPI Swagger UI within the Telegram client for authorized testers.

```mermaid
sequenceDiagram
    autonumber
    actor Tester as Tester (Telegram App)
    participant WebApp as Telegram Mini App (/miniapp)
    participant ApiRouter as api/router/miniapp.py
    participant AuthService as utils/miniapp_auth.py
    participant TestersMgr as services/testers_manager.py
    participant RedisStore as Redis (api:testers:whitelist)
    participant SwaggerUI as Swagger UI Bundle (/docs)
    participant ApiEndpoints as api/router/schedule.py

    Tester->>WebApp: Opens WebApp from Bot button
    WebApp->>WebApp: Reads window.Telegram.WebApp.initData
    WebApp->>ApiRouter: POST /miniapp/auth (init_data)
    ApiRouter->>AuthService: validate_telegram_init_data(init_data)
    AuthService->>AuthService: HMAC-SHA256(secret=WebAppData, BOT_TOKEN)
    AuthService->>AuthService: Verify hash equals computed_hash
    AuthService->>AuthService: Verify auth_date <= 86400s (Replay guard)
    AuthService-->>ApiRouter: Valid user data (id=12345, first_name=Alex)
    ApiRouter->>TestersMgr: is_tester_allowed(12345)
    TestersMgr->>RedisStore: SISMEMBER api:testers:whitelist 12345
    RedisStore-->>TestersMgr: 1 (Allowed)
    TestersMgr-->>ApiRouter: True (Authorized Tester)
    ApiRouter->>AuthService: generate_tester_session(12345)
    AuthService-->>ApiRouter: Signed token 12345:ts:hmac
    ApiRouter-->>WebApp: Set-Cookie para_session=token (HttpOnly, Secure)
    WebApp->>SwaggerUI: Mount Swagger UI with CleanSwaggerPlugin & relative gateway
    SwaggerUI->>ApiRouter: GET /openapi.json (para_session cookie authenticated)
    ApiRouter-->>SwaggerUI: 200 OK (OpenAPI 3.1 schema without server IP)
    SwaggerUI->>SwaggerUI: CleanSwaggerPlugin disables InfoUrl (no /openapi.json link)
    SwaggerUI-->>Tester: Render clean interactive API documentation (IP masked)
    Tester->>SwaggerUI: Click Try it out and Execute GET /schedule/day
    SwaggerUI->>SwaggerUI: requestInterceptor strips VPS host/IP -> relative URL
    SwaggerUI->>ApiEndpoints: GET /schedule/day (with para_session cookie)
    ApiEndpoints->>ApiRouter: verify_api_or_tester() validates cookie
    ApiEndpoints-->>SwaggerUI: 200 OK (lessons list)
    SwaggerUI-->>Tester: Display clean Curl & Request URL (no IP exposed)
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Telegram WebApp Initialization**: When a user clicks the Mini App button inside Telegram, the WebApp platform injects cryptographically signed `window.Telegram.WebApp.initData` containing user attributes, query timestamp, and signature hash.
2. **HMAC-SHA256 Cryptographic Verification**: The backend sorts parameters alphabetically to construct a deterministic `data_check_string`, computes `secret_key = HMAC-SHA256("WebAppData", BOT_TOKEN)`, and compares the derived digest against the provided `hash` using timing-attack safe comparison (`hmac.compare_digest`).
3. **Replay Attack Defense**: `MiniappAuthService` validates `auth_date` against `SESSION_MAX_AGE_SECONDS` (86400 seconds). Payloads older than 24 hours are rejected immediately with HTTP 401.
4. **RBAC Whitelist Enforcement**: `TestersManager.is_tester_allowed(user_id)` checks the Redis set `api:testers:whitelist` in O(1) time complexity. Unwhitelisted accounts are rejected with HTTP 403 Forbidden.
5. **Signed Session Token Minting**: `generate_tester_session(user_id)` constructs a tamper-proof session token format `<user_id>:<timestamp>:<signature>` and binds it to the browser via an HTTP-only secure cookie `para_session`.
6. **Embedded Swagger UI Execution & Host Sanitization**: The Mini App mounts Swagger UI Bundle pointing to `/openapi.json` with `CleanSwaggerPlugin` removing the `/openapi.json` header link, CSS hiding server selectors, and `requestInterceptor` stripping public VPS IP addresses and absolute hosts (`45-81-154-175.sslip.io`) to relative routes (`/schedule/day`). The `/openapi.json` endpoint itself is strictly guarded by `verify_api_or_tester()`, preventing unauthorized schema leakage.

---

### 9.3. Tester Whitelist Management & Personal API Key Flow

Administrative control flow for managing authorized testers in Redis, automatic personal API key generation (`para_test_<token_hex>`), and end-to-end request audit logging.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Headman / Admin
    participant Bot as para-bot
    participant Handler as bot/handlers/admin/testers.py
    participant TestersMgr as services/testers_manager.py
    participant RedisStore as Redis Cache
    actor Tester as External Tester (e.g. 8894263260)
    participant ApiServer as para-api (FastAPI)

    Admin->>Bot: /add_tester 8894263260
    Bot->>Handler: cmd_add_tester(message)
    Handler->>Handler: Validate numeric Telegram ID
    Handler->>TestersMgr: add_tester(8894263260)
    TestersMgr->>RedisStore: SADD api:testers:whitelist 8894263260
    TestersMgr->>TestersMgr: generate_or_get_tester_key(8894263260)
    TestersMgr->>RedisStore: SET api:uid_to_key:8894263260 para_test_xxx
    TestersMgr->>RedisStore: SET api:key_to_uid:para_test_xxx 8894263260
    TestersMgr-->>Handler: Return True & Generated Key
    Handler-->>Admin: Alert with tester ID & Personal API Key
    
    Tester->>Bot: /start or /swagger
    Bot->>Bot: Check is_tester_allowed(8894263260) == True
    Bot-->>Tester: Render Tester Cabinet with Key & Swagger UI buttons
    
    Tester->>ApiServer: Request with Header X-API-Key or Bearer para_test_xxx
    ApiServer->>TestersMgr: get_tester_by_key(para_test_xxx)
    TestersMgr->>RedisStore: GET api:key_to_uid:para_test_xxx -> 8894263260
    ApiServer->>ApiServer: _log_audit_access("tester:8894263260", request)
    ApiServer-->>Tester: 200 OK Response
```

#### Execution Flow & Under-the-Hood Lifecycle

1. **Administrative Access Gate**: Only administrators present in `ADMIN_IDS` (headman and deputy) are permitted to manage API testing access.
2. **Atomic Whitelist & Key Minting**: The `/add_tester <id>` command adds the user ID to `api:testers:whitelist` and generates an cryptographically secure 16-byte hex token prefixed with `API_TESTER_KEY_PREFIX`.
3. **Bidirectional O(1) Indexing**: Redis stores dual keys:
   - `{REDIS_TESTER_UID_TO_KEY_PREFIX}{uid}` -> `api_key`
   - `{REDIS_TESTER_KEY_TO_UID_PREFIX}{api_key}` -> `uid`
4. **Security Audit Logging**: Every incoming request passing through `verify_api_or_tester()` resolves the caller to `tester:<uid>` or `master_admin` and writes an audit record to the structured log: `[AUDIT] {identity} -> {method} {path} (IP: {client_ip})`.
5. **Cabinet Access for Non-Students**: If an authorized tester is not a student in group 1-КПД-3, `cmd_start` does not reject them, but automatically displays their Tester Cabinet with Swagger UI and API key.

---

### 9.4. Full REST OpenAPI & Security Architecture (11 Subsystems & Schemas)

Comprehensive architecture diagram mapping the 11 integrated subsystem routers, typed Pydantic V2 request/response schemas, security dependencies, and data flow layers in `para-api`.

```mermaid
classDiagram
    direction TB

    class FastApiApplication {
        +title str = "para-api"
        +version str = "2.0.0"
        +openapi_schema dict
        +_register_routers(app) void
        +_custom_openapi_schema(app) dict
    }

    class ErrorDetail {
        +detail str
        +code Optional~str~
        +timestamp str
    }

    class ExceptionHandlers {
        +http_exception_handler(request, exc) JSONResponse
        +validation_exception_handler(request, exc) JSONResponse
        +unhandled_exception_handler(request, exc) JSONResponse
    }

    class SecurityDependencies {
        +verify_api_or_tester(key, bearer, cookie) str
        +verify_admin_access(auth_identity) str
        -_resolve_key_identity(key) str
        -_resolve_token_identity(token) str
        -_log_audit_access(identity, request) void
    }

    class ScheduleRouter {
        +GET /schedule/day
        +GET /schedule/today
        +GET /schedule/tomorrow
        +GET /schedule/week
        +GET /schedule/current
        +POST /schedule/refresh
    }

    class ExamsRouter {
        +GET /exams
        +GET /exams/upcoming
        +POST /exams/refresh
    }

    class TeachersRouter {
        +GET /teachers
        +GET /teachers/search
        +GET /teachers/:last_name
        +POST /teachers/custom
        +DELETE /teachers/custom/:last_name
        +POST /teachers/refresh
    }

    class AttendanceRouter {
        +GET /attendance/stats
        +GET /attendance/student/:fio
        +GET /attendance/session
        +POST /attendance/session/start
        +POST /attendance/session/mark
        +POST /attendance/session/batch_present
        +POST /attendance/session/commit
        +DELETE /attendance/session
    }

    class ClassmatesRouter {
        +GET /classmates
        +GET /classmates/:student_id
    }

    class BirthdaysRouter {
        +GET /birthdays
        +GET /birthdays/upcoming
        +GET /birthdays/today
    }

    class SolverRouter {
        +GET /solver/status
        +POST /solver/solve
        +GET /solver/task/:msg_id
        +POST /solver/queue/clear
    }

    class SubscribersRouter {
        +GET /subscribers
        +GET /subscribers/count
        +GET /subscribers/:chat_id
        +POST /subscribers/:chat_id
        +DELETE /subscribers/:chat_id
    }

    class SystemRouter {
        +GET /system/info
        +POST /system/cache/flush
    }

    class MiniappRouter {
        +GET /miniapp
        +POST /miniapp/auth
        +GET /miniapp/status
        +GET /miniapp/testers
        +POST /miniapp/testers/:uid
        +DELETE /miniapp/testers/:uid
    }

    class HealthRouter {
        +GET /health
    }

    FastApiApplication --> SecurityDependencies : enforces OpenAPI SecuritySchemes
    FastApiApplication --> ScheduleRouter : mounts
    FastApiApplication --> ExamsRouter : mounts
    FastApiApplication --> TeachersRouter : mounts
    FastApiApplication --> AttendanceRouter : mounts
    FastApiApplication --> ClassmatesRouter : mounts
    FastApiApplication --> BirthdaysRouter : mounts
    FastApiApplication --> SolverRouter : mounts
    FastApiApplication --> SubscribersRouter : mounts
    FastApiApplication --> SystemRouter : mounts
    FastApiApplication --> MiniappRouter : mounts
    FastApiApplication --> HealthRouter : mounts

    ScheduleRouter ..> SecurityDependencies : verify_api_or_tester
    ExamsRouter ..> SecurityDependencies : verify_api_or_tester
    TeachersRouter ..> SecurityDependencies : verify_api_or_tester
    AttendanceRouter ..> SecurityDependencies : verify_api_or_tester
    ClassmatesRouter ..> SecurityDependencies : verify_api_or_tester
    BirthdaysRouter ..> SecurityDependencies : verify_api_or_tester
    SolverRouter ..> SecurityDependencies : verify_api_or_tester
    SubscribersRouter ..> SecurityDependencies : verify_api_or_tester
    SystemRouter ..> SecurityDependencies : verify_api_or_tester
    MiniappRouter ..> SecurityDependencies : verify_api_or_tester
```

---

### 9.5. Public HTTPS Edge Gateway & Reverse SSH Tunnel Architecture

Architecture diagram detailing the edge ingress topology: public mobile clients connect via standard HTTPS (port 443) to the European Edge VPS gateway (`45-81-154-175.sslip.io`), where Caddy terminates TLS via Let's Encrypt and forwards traffic over an encrypted reverse SSH tunnel directly into the local `para-api` backend container on `home`.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Mobile Client (Telegram / Browser)
    participant Caddy as Caddy TLS Gateway (45.81.154.175:443)
    participant VpsLocal as VPS Loopback (127.0.0.1:8080)
    participant SshTunnel as SSH Reverse Tunnel (para-vps-tunnel)
    participant HomeApi as para-api (home:8080)
    participant Redis as para-redis (home:6379)

    Client->>Caddy: HTTPS GET https://45-81-154-175.sslip.io/miniapp
    Note over Caddy: TLS Termination (Let's Encrypt DV Cert)<br/>Standard Port 443 (HTTP/2, HTTP/3)
    Caddy->>VpsLocal: Proxy HTTP to 127.0.0.1:8080
    VpsLocal->>SshTunnel: Encrypted TCP channel
    SshTunnel->>HomeApi: Forward to 127.0.0.1:8080 (Docker bridge)
    HomeApi->>Redis: Session & Whitelist lookup
    Redis-->>HomeApi: Cache / State response
    HomeApi-->>SshTunnel: HTTP 200 OK
    SshTunnel-->>VpsLocal: Forward response
    VpsLocal-->>Caddy: Upstream response
    Caddy-->>Client: HTTPS 200 OK (Clean WebView render)
```


---

## 10. Performance Hardening & Security Audit Architecture

### 10.1. API Security Boundary & Privilege Escalation Prevention

Sequence diagram detailing the defense-in-depth protection added during the security audit:
1. `POST /teachers/custom` requires admin role verification (`verify_admin_access`), preventing testers from altering custom Zoom links.
2. `POST /solver/solve` enforces per-identity rate limiting (`_check_solver_rate_limit`) via Redis sliding window counters (5 req/min).
3. `POST /system/cache/flush` enforces strict prefix whitelisting (`_validate_flush_pattern`), rejecting broad flush attempts like `*` or critical namespaces.

```mermaid
sequenceDiagram
    autonumber
    actor Caller as Client (Tester / Admin / Attacker)
    participant ApiApp as FastAPI Ingress (para-api)
    participant AuthDep as Security Dependencies (deps.py)
    participant SecRule as Validation & Rate Limiter
    participant Redis as Redis Cache (para-redis)
    participant Handler as Business Logic Router

    alt Direct Solver API Rate Limiting
        Caller->>ApiApp: POST /solver/solve (DirectSolveRequest)
        ApiApp->>AuthDep: verify_api_or_tester()
        AuthDep-->>ApiApp: identity ("tester:12345" or "apikey")
        ApiApp->>SecRule: _check_solver_rate_limit(identity)
        SecRule->>Redis: INCR "ratelimit:solver:{identity}" & EXPIRE 60
        Redis-->>SecRule: current_count
        alt Count > 5 requests / min
            SecRule-->>ApiApp: raise HTTPException(429, Rate limit exceeded)
            ApiApp-->>Caller: HTTP 429 Too Many Requests
        else Allowed
            SecRule-->>ApiApp: OK
            ApiApp->>Handler: solve_direct_task()
            Handler-->>Caller: HTTP 200 TaskResult
        end
    else Custom Teacher Zoom Link Tampering Attempt
        Caller->>ApiApp: POST /teachers/custom (CustomTeacherRequest)
        ApiApp->>AuthDep: verify_admin_access()
        alt Caller is Tester (not Admin)
            AuthDep-->>ApiApp: raise HTTPException(403, Admin access required)
            ApiApp-->>Caller: HTTP 403 Forbidden
        else Caller is Root Admin
            AuthDep-->>ApiApp: OK
            ApiApp->>Handler: save_custom_teacher()
            Handler->>Redis: HSET "teachers:custom"
            Handler-->>Caller: HTTP 200 OK
        end
    else Cache Flush Pattern Boundary
        Caller->>ApiApp: POST /system/cache/flush?pattern=*
        ApiApp->>AuthDep: verify_api_key()
        AuthDep-->>ApiApp: OK
        ApiApp->>SecRule: _validate_flush_pattern("*")
        alt Pattern not in SAFE_FLUSH_PREFIXES
            SecRule-->>ApiApp: raise HTTPException(400, Flush pattern not allowed)
            ApiApp-->>Caller: HTTP 400 Bad Request
        else Pattern allowed (e.g. "sched:*")
            SecRule-->>ApiApp: OK
            ApiApp->>Handler: flush_cache(pattern)
            Handler->>Redis: SCAN & DEL matching keys
            Handler-->>Caller: HTTP 200 {"deleted": count}
        end
    end
```

---

### 10.2. High-Performance Attendance Caching & Thread-Offloading Flow

Architecture flow showing the mitigation of WOPI network latency and Excel parsing Event Loop blocking:
- Student roster is cached in Redis (`att:cached_students`) for 24 hours, reducing headman session startup from 3–7 seconds to 10–20 ms.
- Synchronous CPU-intensive 12-sheet Excel parsing (`parse_workbook_attendance`) is offloaded via `asyncio.to_thread`, keeping the async event loop responsive.

```mermaid
sequenceDiagram
    autonumber
    actor Headman as Headman / Admin User
    participant Bot as Telegram Bot (para-bot)
    participant AttMgr as AttendanceManager
    participant Redis as Redis Cache (para-redis)
    participant Wopi as WOPI Client (Yandex Docs)
    participant StatsMgr as AttendanceStats
    participant WorkerThread as asyncio.to_thread (Threadpool)

    Headman->>Bot: /attendance (Start Marking)
    Bot->>AttMgr: fetch_target_students()
    AttMgr->>Redis: GET "att:cached_students"
    alt Cache Hit (Warm Roster)
        Redis-->>AttMgr: JSON student list (29 items)
        Note over AttMgr: Zero network roundtrips (~15ms latency)
    else Cache Miss (Cold / Expired)
        Redis-->>AttMgr: null
        AttMgr->>Wopi: Download raw XLSX & extract students
        Wopi-->>AttMgr: Excel bytes
        AttMgr->>Redis: SETEX "att:cached_students" 86400 (24h)
    end
    AttMgr-->>Bot: List[str] students
    Bot-->>Headman: Inline Keyboard (Student 1/29)

    Headman->>Bot: /my_attendance (Fetch Stats)
    Bot->>StatsMgr: get_all_students_stats()
    StatsMgr->>Wopi: Download current XLSX
    Wopi-->>StatsMgr: Excel raw bytes
    Note over StatsMgr,WorkerThread: CPU-bound 12-month sheets traversal
    StatsMgr->>WorkerThread: asyncio.to_thread(parse_workbook_attendance, wb)
    WorkerThread-->>StatsMgr: Parsed Attendance Matrix
    Note over StatsMgr: Main event loop remains unblocked
    StatsMgr-->>Bot: Formatted Student Stats
    Bot-->>Headman: Telegram Message with Attendance Summary
```

---

### 10.3. Concurrent AI Solver Worker Pipeline with Semaphore Control

Sequence diagram illustrating concurrent AI task processing in `solver.py` with `asyncio.Semaphore(MAX_CONCURRENT_TASKS)`:

```mermaid
sequenceDiagram
    autonumber
    actor Student as Student in Topic 405
    participant Queue as Redis Reliable Queue (hw:queue)
    participant SolverLoop as Solver Loop (solver.py)
    participant Sem as asyncio.Semaphore(limit=3)
    participant AiTask as Worker Coroutine
    participant DeepSeek as DeepSeek AI Provider
    participant DocxGen as GOST Docx Generator
    participant Bot as Telegram Bot Notification

    Student->>Queue: Enqueue Task (task_id, prompt, files)
    loop Main Ingestion Loop
        SolverLoop->>Queue: BLPOP "hw:queue" (timeout=2)
        Queue-->>SolverLoop: Task Payload
        SolverLoop->>Sem: acquire()
        SolverLoop->>AiTask: asyncio.create_task(_process_with_semaphore())
        Note over SolverLoop: Loop immediately continues to fetch next task
    end

    par Concurrent Task Execution (up to 3 parallel)
        AiTask->>DeepSeek: generate_solution(prompt, attachments)
        DeepSeek-->>AiTask: Formatted solution text
        AiTask->>DocxGen: create_gost_document(solution)
        DocxGen-->>AiTask: output.docx bytes
        AiTask->>Bot: send_document(topic=405, docx)
        AiTask->>Queue: HSET "hw:tasks:{id}" status="done"
        AiTask->>Sem: release()
    end
```

---

### 10.4. Multi-Tier High-Performance Architecture: L1 In-Memory, uvloop & gRPC Keepalive

Architecture flow illustrating the multi-tier performance optimization:
1. **L1 In-Memory Cache**: `_RESOLVED_DAY_CACHE` serves pre-constructed `Lesson` models in 10 microseconds without touching Redis or running regex parsers.
2. **Network Acceleration**: Uvicorn runs with `uvloop` (libuv C-bindings) and `httptools` (Nginx C-parser) for high concurrency.
3. **gRPC HTTP/2 Warm Keepalive**: Channels maintain active ping intervals (`GRPC_KEEPALIVE_TIME_MS`), eliminating cold socket renegotiations.
4. **Bandwidth Optimization**: `GZipMiddleware` automatically compresses payloads >1 KB for mobile Mini App clients.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Ingress Client (Bot / Worker / Mini App)
    participant Uvicorn as Uvicorn (uvloop + httptools)
    participant Gzip as GZip Middleware (>1KB)
    participant GrpcClient as gRPC Stub (Keepalive: 10s)
    participant GrpcServer as grpc.aio.Server
    participant L1Cache as L1 In-Memory Cache (_RESOLVED_DAY_CACHE)
    participant L2Redis as L2 Redis Snapshot (schedule:snapshot)

    alt gRPC High-Speed Path
        Client->>GrpcClient: GetDaySchedule(date=2026-10-12)
        Note over GrpcClient,GrpcServer: HTTP/2 Persistent TCP Stream (Pre-warmed Keepalive)
        GrpcClient->>GrpcServer: Binary Protobuf Request (32 bytes)
        GrpcServer->>L1Cache: Check _RESOLVED_DAY_CACHE[date]
        alt L1 Cache Hit (Warm Memory)
            L1Cache-->>GrpcServer: Ready list[Lesson] (10 microseconds)
        else L1 Cache Miss
            GrpcServer->>L2Redis: Load group snapshot
            L2Redis-->>GrpcServer: JSON Snapshot
            GrpcServer->>L1Cache: Save compiled models
        end
        GrpcServer-->>GrpcClient: Binary Protobuf Response (1.3 KB, ~0.3 ms)
    else REST / Mini App HTTP/2 Path
        Client->>Uvicorn: GET /schedule/day?target_date=2026-10-12
        Note over Uvicorn: Handled by uvloop + httptools C-engine
        Uvicorn->>L1Cache: Lookup resolved lessons
        L1Cache-->>Uvicorn: list[Lesson]
        Uvicorn->>Gzip: Serialize directly to JSON bytes
        Gzip-->>Client: HTTP 200 OK (Gzip Compressed, <1 ms)
    end
```

---

## 11. Automated CI/CD Pipeline & Delivery Verification

The automated GitHub Actions workflow (`.github/workflows/ci.yml`) enforces multi-tier quality gates on every push and pull request before code reaches the production server.

```mermaid
flowchart TD
    GitPush(["Git Push / PR (main)"]) --> Trigger["GitHub Actions Runner (ubuntu-latest)"]
    
    subgraph Stage1["1. Static Analysis & Security (Python 3.12)"]
        Ruff["Ruff Linter\n(UP, B, SIM, E, F, I)"]
        Bandit["Bandit AST Scanner\n(pyproject.toml config)"]
    end
    
    subgraph Stage2["2. Isolated Test Matrix (Strict AsyncIO)"]
        Py311["Pytest Suite\n(Python 3.11 Runtime)"]
        Py312["Pytest Suite\n(Python 3.12 Runtime)"]
        EnvCI["Mock Env Loader\n(.env.ci -> .env)"]
    end
    
    subgraph Stage3["3. Container Delivery Gate"]
        DockerBuild["Docker Compose Build Matrix\n(--parallel)"]
        SrvApi["para-api (FastAPI + gRPC)"]
        SrvBot["para-bot (Aiogram 3.4)"]
        SrvWorker["para-worker (Topic & Notifier)"]
        SrvSolver["para-solver (DeepSeek Worker)"]
    end
    
    Trigger --> Stage1
    Trigger --> Stage2
    Stage1 --> Stage3
    Stage2 --> Stage3
    
    EnvCI --> Py311
    EnvCI --> Py312
    
    DockerBuild --> SrvApi
    DockerBuild --> SrvBot
    DockerBuild --> SrvWorker
    DockerBuild --> SrvSolver
    
    Stage3 --> Success(["✅ Deployment Verified (Production Ready)"])
```

