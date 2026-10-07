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
    }

    class ScheduleApiService {
        +get_day_schedule(group, date) DayScheduleResponse
        +get_week_schedule(group, week) WeekScheduleResponse
        +get_exams(group) ExamsResponse
    }

    class TopicWorkerService {
        +run_check_cycle() void
        +send_bell_reminder() void
        +cleanup_old_messages() void
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
