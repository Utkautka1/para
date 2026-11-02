# Privacy Policy

**Effective Date:** October 5, 2026
**Last Updated:** October 5, 2026
**Project:** Telegram Group Automation & Timetable Service for Student Group 1-KPD-3 («para»)
**Repository:** [https://github.com/Utkautka1/para](https://github.com/Utkautka1/para)

---

## Table of Contents

1. [Introduction & Scope](#1-introduction--scope)
2. [Data Controller & Administration](#2-data-controller--administration)
3. [Categories of Personal Data Collected](#3-categories-of-personal-data-collected)
4. [Lawful Bases & Purposes of Data Processing](#4-lawful-bases--purposes-of-data-processing)
5. [Third-Party Services & Subprocessors](#5-third-party-services--subprocessors)
6. [Data Storage Architecture, Security & Retention](#6-data-storage-architecture-security--retention)
7. [User Rights & Self-Service Controls](#7-user-rights--self-service-controls)
8. [Cookies, Session Tokens & Storage Technologies](#8-cookies-session-tokens--storage-technologies)
9. [Protection of Minors](#9-protection-of-minors)
10. [Amendments & Notification of Changes](#10-amendments--notification-of-changes)
11. [Contact Information & Redress](#11-contact-information--redress)

---

## 1. Introduction & Scope

This Privacy Policy («Policy») governs the collection, processing, storage, and protection of information obtained from users interacting with the open-source software suite developed for student academic group **1-KPD-3** at the College of Technology, Modeling and Design (KTMU), St. Petersburg State University of Industrial Technologies and Design (SPbSUITD).

The software ecosystem comprises five distributed microservices:
- **`para-bot`**: An interactive Telegram Bot interface built on `aiogram 3.x` with asynchronous event handling;
- **`para-api`**: A high-performance internal RESTful backend service built on `FastAPI` providing group timetable and WOPI integration;
- **`para-worker`**: An autonomous background scheduler managing topic updates, bell reminders, and birthday congratulations;
- **`para-solver`**: An asynchronous worker consumer processing student homework tasks and compiling GOST-compliant Word reports;
- **`para-redis`**: An in-memory key-value cache and reliable queue broker coordinating state across containers.

This Policy applies to all students, group administrators (headmen and deputies), instructors, and guests who interact with the bot in direct messages (private chat) or through forum topics within the group's official Telegram supergroup.

---

## 2. Data Controller & Administration

The Data Controller responsible for personal data processing within the scope of this repository is the student administration of group 1-KPD-3:
- **Project Name:** `para`
- **Lead Maintainer / Developer:** `qwerty9357u`
- **Contact:** Via Telegram Group Administration or GitHub Issues at [https://github.com/Utkautka1/para/issues](https://github.com/Utkautka1/para/issues)

Processing is carried out strictly on a non-commercial, academic basis to facilitate group management, study schedule accessibility, and transparent attendance tracking.

---

## 3. Categories of Personal Data Collected

The system operates under the principle of **Data Minimization**; only information strictly necessary for academic organization is collected.

### 3.1. Telegram Account Identifiers
When an individual initiates interaction with the bot or posts within registered group forum threads, the following metadata is processed:
- **Numeric Telegram User ID (`user_id` / `tg_id`)**: A unique 64-bit integer assigned by Telegram;
- **Telegram Username (`@username`)**: Public alias (where configured by the user);
- **Profile Display Name (`first_name`, `last_name`)**: Publicly accessible profile strings;
- **Chat and Thread Identifiers (`chat_id`, `message_thread_id`)**: Routing targets for forum topics and private messages.

### 3.2. Student Group Roster & Whitelist
- **Full Legal/Academic Name**: Student surname and first name as recorded in official college enrollment registries;
- **Academic Subgroup**: Division into Subgroup 1 or Subgroup 2 for laboratory and practical classes;
- **Administrative Roles**: Authorization flags designating regular Student status, Headman, Deputy Headman, or System Administrator;
- **Custom Teacher Registry**: Instructor full names, disciplines taught, campus classroom numbers, and videoconferencing (Zoom/Pruffme) links.

### 3.3. Attendance & Academic Registry Records
- **Session Attendance Marks**: Lesson presence recorded per period slot (0 through 5) and date:
  - `П` (Present / Attended in full);
  - `О` / `1 оп` (Tardy / Late arrival);
  - `У` (Excused absence substantiated by medical certificate or dean's permission);
  - `Н` (Unexcused absence / Truancy).
- **Aggregated Academic Metrics**: Cumulative counts of attendance categories across academic terms (`СЕНТ`, `ОКТ`, `НОЯБ`, `ДЕК`...) and calculated attendance percentage;
- **Academic League Placement**: Classification into academic tiers (Gold League: 90–100%, Silver League: 60–89%, Risk Zone: <60%).

### 3.4. Birthday Celebration Registry
- **Day and Month of Birth (`DD.MM`)**: Used exclusively to generate automated festive greeting cards in the dedicated Telegram topic;
- **Explicit Telegram ID Binding**: Links a student's record to their Telegram account to allow polite personal mentions (`@username` or inline user mention) on their birthday.

### 3.5. Homework Solver Artifacts (Optional User Submission)
- **Input Problem Content**: Textual queries and photographic images of problem sheets, handwritten exercises, or lab prompts voluntarily submitted by a student to the homework solver queue;
- **Compiled GOST Reports**: Output Microsoft Word (`.docx`) solution documents structured in accordance with Russian Academic Standard GOST 7.32-2017.

### 3.6. Technical System Telemetry
- **API Request Headers**: Internal client identification (`X-API-Key`) and basic timestamp data;
- **Rate-Limiting State**: Inline button click timestamps recorded in Redis to prevent flooding and double-clicks (throttling windows ranging between 1.0 and 4.0 seconds);
- **Diagnostic Execution Logs**: Timestamped operational logs recorded in `logs/` without recording sensitive message bodies.

---

## 4. Lawful Bases & Purposes of Data Processing

All data processing is conducted under the lawful bases of **Legitimate Academic Interests** and **Voluntary User Consent** (implied by issuing bot commands or explicitly providing data to the headman).

| Processing Activity | Categories of Data Involved | Primary Purpose & Justification |
| :--- | :--- | :--- |
| **Access Control & Whitelisting** | Telegram ID, Username, Full Name | Restricting access to internal group documents, attendance links, and contact registers strictly to verified group classmates (`ClassmateAuthFilter`). |
| **Timetable Delivery** | Subgroup, Chat ID, User ID | Delivering custom-filtered daily and weekly lesson schedules, room locations, teacher contacts, and remote links upon student request. |
| **Electronic Attendance Journal** | Full Name, Attendance Marks, Dates | Enabling group headmen to record attendance in class, synchronizing records directly into Yandex Documents (.xlsx), and updating group ranking. |
| **Private Attendance Self-Service** | Telegram ID, Full Name, Attendance Metrics | Empowering students to inspect their personal cumulative attendance percentage and absence reasons in private chat via `/my_attendance`. |
| **Bell Reminders & Alerts** | Topic ID, Lesson Times | Publishing automatic reminder alerts 10 minutes prior to lesson start/end in the general chat, followed by automatic cleanup after 15 minutes. |
| **Birthday Greetings** | Full Name, Birthdate, Telegram ID | Publishing automated festive congratulatory messages in the forum topic at **07:00 MSK** on the student's birthday. |
| **Academic Homework Solver** | Input Photos/Text, Telegram ID | Performing AI-assisted step-by-step problem reasoning and generating downloadable GOST `.docx` reports for the requesting student. |

---

## 5. Third-Party Services & Subprocessors

The software integrates with select external services to fulfill its operational functions. The maintainers do not sell, rent, monetize, or disclose personal data to advertising networks or third-party data brokers.

### 5.1. Telegram Messenger (Telegram FZ-LLC / Telegram Group Inc.)
- **Role:** Communication infrastructure and bot hosting platform.
- **Data Transferred:** Message contents, user IDs, usernames, and callback query payloads transmitted over Telegram MTProto encrypted protocol.
- **Privacy Policy:** [https://telegram.org/privacy](https://telegram.org/privacy)

### 5.2. Yandex Cloud & Yandex 360 (Yandex LLC)
- **Role:** Cloud storage provider for the official attendance spreadsheet (.xlsx) and WOPI (Web Application Open Platform Interface) host.
- **Data Transferred:** Group attendance sheets containing student names and attendance marks. WOPI session tokens and administrative session cookies (`Session_id`, `_yasc`) are handled securely with automated keepalive refresh.
- **Privacy Policy:** [https://yandex.ru/legal/confidential/](https://yandex.ru/legal/confidential/)

### 5.3. DeepSeek AI (DeepSeek Technology Co., Ltd.)
- **Role:** Large Language and Vision Model API provider for homework solving.
- **Data Transferred:** Base64-encoded problem images and user-provided problem prompts.
- **Data Protection Safeguards:** Requests are dispatched in **stateless mode** (`temperature=0.0`, zero conversation history). DeepSeek does not use API payloads submitted through developer endpoints to train public foundation models.
- **Privacy Policy:** [https://www.deepseek.com/privacy](https://www.deepseek.com/privacy)

### 5.4. KTMU College Timetable Servers
- **Role:** Public timetable data source.
- **Data Transferred:** Outbound HTTP requests from `para-api` download the public college schedule. **No personal student data** is ever transmitted to the college servers during scraping.

---

## 6. Data Storage Architecture, Security & Retention

### 6.1. Ephemeral & In-Memory Storage (Redis & RAM-Disk)
Operational state is isolated in Redis key-value storage and in-memory tmpfs with strictly configured Time-To-Live (TTL) expiration:
- **Button Click Debounce Flags (`cb_throttle:{user_id}`)**: Automatically expire after 1.0–4.0 seconds;
- **Day Schedule Cache Pack (`sched:day_pack:{date}`)**: Expires after 180 seconds;
- **Bell Reminder Sent Flags (`rem:sent:{group}:{date}:{period}:{type}`)**: Expire after 2 hours;
- **WOPI Session Tokens (`att:session:{session_id}`)**: Expire after 1 hour;
- **Homework Task Queue Buffers (`hw:tasks:queue`, `hw:tasks:processing`)**: Removed via atomic `LREM` immediately upon document delivery;
- **All-Time Attendance Stats Cache (`att:stats:all_time`)**: Retained for 1 hour with instant optimistic invalidation upon headman updates;
- **Voice Audio Processing in Transient RAM-Disk (`/dev/shm`)**: Audio notes and voice messages submitted for attendance marking or schedule search are buffered strictly in the volatile memory filesystem (`/dev/shm`), converted to text via local Whisper STT, and physically unlinked via `os.remove()` inside guaranteed `finally` blocks immediately after transcription. No student voice recordings are ever persisted to magnetic/SSD disk storage or retained in backup archives.

### 6.2. Persistent Storage & Security Measures
- **File System Permissions**: Local data stores (`data/bot/birthdays.json`, `data/bot/user_cache.json`, `data/bot/subscribers.json`) reside on restricted server storage with strict POSIX permissions (`chmod 600`), preventing unauthorized local access.
- **Atomic File Operations**: All disk modifications execute through temporary files with atomic swap (`os.replace`) to guard against data corruption during unexpected restarts.
- **Container Isolation**: Microservices execute within isolated Docker bridge networks (`para-network`), exposing only necessary ports internally and rejecting inbound external traffic.
- **Authentication Safeguards**: All administrative actions require matching Telegram ID verification (`IsAdminFilter`, `ALLOWED_USER_ID`), and concurrent headman survey collision locks guarantee mutual exclusion.

### 6.3. Data Retention Schedule
Personal data is retained only for the duration of the student's active enrollment in academic group 1-KPD-3. Upon completion of the academic program, graduation, or student transfer, associated identifiers are purged from active configuration files within thirty (30) calendar days upon notice.

### 6.4. Data Localization & Russian Federal Law 152-FZ Compliance
In strict compliance with Article 18, Paragraph 5 of Federal Law No. 152-FZ «On Personal Data»:
- All recording, systematization, accumulation, storage, clarification (updating, changing), and extraction of personal data of Russian Federation citizens is conducted exclusively utilizing computing infrastructure, databases, and physical servers situated within the territory of the Russian Federation;
- Primary persistent storage volumes and in-memory caches reside in Russian Tier-III data centers;
- Cross-border data transmission during homework solving is limited to non-personally identifiable problem formulations without student identity attributes.

---

## 7. User Rights & Self-Service Controls

Under established data protection principles (including fair information practices consistent with GDPR and Russian Federal Law No. 152-FZ «On Personal Data»), users enjoy the following rights:

1. **Right of Access & Inspection**:
   - Any student may inspect their personal attendance record, late arrival tallies, and percentage by sending `/my_attendance` directly to the bot in private messages.
2. **Right to Rectification**:
   - Students may request updates to their registered name, subgroup designation, or Telegram username by notifying the group headman or using the `/help` command to discover administrative contacts.
   - Headmen can link Telegram IDs for students without usernames via the in-bot administrative command `admin:bind_student`.
3. **Right to Erasure («Right to be Forgotten» / Ст. 15 152-ФЗ)**:
   - Any user may request complete purging of their personal data from the platform. Execution occurs through a formal 5-step procedure:
     1. **Submission**: Send an erasure request to the system administrator or submit an issue via repository redress channels.
     2. **Roster Removal**: Immediate removal of birthdate from `data/bot/birthdays.json`, halting automated congratulatory messages.
     3. **Cache Eviction**: Expulsion of the user's mapping from `data/bot/user_cache.json` and unlinking from `data/bot/subscribers.json`.
     4. **Redis Purge**: Atomic invalidation of all related keys (`cb_throttle:{user_id}`, `auth:session:{user_id}`).
     5. **Historical Anonymization**: Replacement of the student's legal name in attendance sheets with a cryptographic pseudonym (`STUDENT_ANON_xxxx`) to preserve historical class statistical integrity without retaining PII.
     6. **Notice of Completion**: Formal confirmation delivered to the requesting student within ten (10) business days pursuant to 152-FZ.
4. **Right to Restriction of Automated Notifications**:
   - Students may opt out of broadcast notifications and daily schedule alerts at any time by issuing the unsubscribe action.
5. **Right to File an Inquiry**:
   - Students may raise concerns regarding data accuracy or system behavior with group administrators or directly via repository issue tracking.

---

## 8. Cookies, Session Tokens & Storage Technologies

The project does **not** employ browser cookies, tracking beacons, fingerprinting scripts, or third-party analytics pixels on user devices.

- **Web Browser Independence**: Student interactions occur entirely within the native Telegram client;
- **Administrative Cloud Office Keepalive**: The backend utilizes an administrative session cookie for Yandex Documents (`Session_id`, `_yasc`) strictly on the server side to maintain connectivity with the electronic attendance sheet. These cookies are never transmitted to regular students.

---

## 9. Protection of Minors

The service is developed for students of a vocational secondary college (typically aged 15 years and older). We do not knowingly harvest information beyond academic records and basic Telegram account identifiers necessary for educational coordination.

Parents or legal guardians seeking clarification on data processed regarding minor students may contact the group administration as outlined in Section 11.

---

## 10. Amendments & Notification of Changes

The maintainers reserve the right to amend this Privacy Policy to reflect modifications in college regulations, Telegram API policies, or software architecture.

- Substantial revisions will be documented in the repository commit history;
- An announcement summarizing significant privacy adjustments will be posted in the group's Telegram forum topic prior to entry into force;
- Continued use of the bot following the publication of an updated Policy constitutes acceptance of the amended terms.

---

## 11. Contact Information & Redress

For any questions, privacy requests, data deletion inquiries, or bug reports regarding this Privacy Policy, please reach out via:

- **GitHub Issues:** [https://github.com/Utkautka1/para/issues](https://github.com/Utkautka1/para/issues)
- **Telegram Administration:** Contact the group headman or deputy headman in the official 1-KPD-3 chat.
- **Repository Documentation:** [docs/UML.md](UML.md)
