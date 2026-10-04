# 🏛️ Архитектурная UML-документация проекта «para»

Полная спецификация архитектуры, взаимодействия модулей, структур данных и жизненного цикла процессов Telegram-бота расписания КТМУ, внутреннего REST API и фоновых микросервисов.

---

## 1. 🏗️ Компонентная архитектура (Component & Container Diagram)

Диаграмма контейнеров Docker Compose, сетевого взаимодействия, постоянных томов и интеграций с внешними API.

```mermaid
flowchart TD
    subgraph External_World["🌐 Внешние сервисы и пользователи"]
        User["👤 Пользователь / Студент"]
        Admin["👑 Староста / Администратор"]
        TG_API["✈️ Telegram Bot API"]
        KTMU_API["🏫 API КТМУ (timetable-ktmu.ru)"]
        YD_DISK["📂 Яндекс Диск (Public REST API)"]
        YD_DOCS["📊 Яндекс Документы (WOPI Host)"]
        DEEPSEEK["🧠 DeepSeek API (AI Vision & Text)"]
    end

    subgraph Docker_Compose["🐳 Стек Docker Compose (Сеть: internal_bridge)"]
        subgraph S_Redis["⚡ para-redis (Redis 7 Alpine)"]
            RCache[("Кэш снимка расписания\n(sched:group:snapshot)")]
            RQueue[("Очередь задач ДЗ\n(hw:tasks:queue)")]
            RProc[("Очередь обработки ДЗ\n(hw:tasks:processing)")]
            RClean[("ZSET очистки топика\n(topic:cleanup_messages)")]
            RSess[("Сессии посещаемости\n(att:session:*)")]
            RState[("Идемпотентные флаги\n(rem:sent:*, topic:*)")]
        end

        subgraph S_API["🚀 para-api (FastAPI + Uvicorn)"]
            Router_Sched["/schedule (Day & Week)"]
            Router_Exams["/exams"]
            Router_Teachers["/teachers"]
            Router_Health["/health"]
            SchedParser["Schedule Parser\n(clean 40MB -> target group)"]
            DocxParser["Docx Parser\n(Zip/XML Teacher Links)"]
        end

        subgraph S_Bot["🤖 para-bot (aiogram 3)"]
            Dispatch["Dispatcher & Filters"]
            Handlers_User["User Handlers\n(Schedule, HW Solver)"]
            Handlers_Admin["Admin Handlers\n(Attendance, Panel, Mute, Ping)"]
            Keyboards["Inline & Reply Keyboards"]
        end

        subgraph S_Worker["⚙️ para-worker (Background Worker)"]
            TopicUpdater["Topic Updater Loop\n(60s sync + 10m reminder)"]
            ExamUpdater["Exam Updater Loop\n(10m sync)"]
            BirthdayMgr["Birthday Manager\n(07:00 Wishes & Registry)"]
            YKeepalive["Yandex Keep-Alive Loop\n(6h refresh)"]
            Scheduler["APScheduler\n(06:00 Digest & Attendance Poll)"]
        end

        subgraph S_Solver["📐 para-solver (DeepSeek Worker)"]
            SolverLoop["Solver Queue Loop\n(BLMOVE -> Processing)"]
            DocxGen["Docx Generator\n(GOST Solution Formatter)"]
            FileExtractor["File Extractor\n(Image / Docx / PDF / Text)"]
        end
    end

    subgraph Volumes["💾 Постоянные тома (Data Volumes)"]
        Vol_Redis[("./data/redis (AOF)")]
        Vol_Data[("./data (JSON States)")]
        Vol_Logs[("./logs (Rotating Files)")]
    end

    User -->|Команды / Кнопки| TG_API
    Admin -->|/attendance, /all, /mute| TG_API
    TG_API <-->|Long Polling / Webhook| Dispatch

    Dispatch --> Handlers_User
    Dispatch --> Handlers_Admin

    Handlers_User -->|HTTP GET (X-API-Key)| Router_Sched
    Handlers_User -->|RPUSH hw:tasks:queue| RQueue
    Handlers_Admin -->|Управление сессией| RSess

    TopicUpdater -->|HTTP GET /schedule/day| Router_Sched
    TopicUpdater -->|Проверка/Отметка отправки| RState
    TopicUpdater -->|ZADD / ZRANGEBYSCORE| RClean
    TopicUpdater -->|send_message / delete_message| TG_API

    ExamUpdater -->|HTTP GET /exams| Router_Exams
    ExamUpdater -->|edit_message_text| TG_API

    BirthdayMgr -->|Чтение/Запись| Vol_Data
    BirthdayMgr -->|Поздравления в топик| TG_API

    YKeepalive -->|WOPI Token Refresh| YD_DOCS
    Scheduler -->|Оповещения и опросы| TG_API

    Router_Sched --> SchedParser
    Router_Teachers --> DocxParser
    SchedParser -->|HTTP GET ETag| KTMU_API
    SchedParser <-->|Снимок группы| RCache
    DocxParser -->|HTTP GET .docx| YD_DISK

    SolverLoop -->|BLMOVE| RProc
    SolverLoop -->|Download File| TG_API
    SolverLoop --> FileExtractor
    SolverLoop -->|Prompt + Image| DEEPSEEK
    SolverLoop --> DocxGen
    SolverLoop -->|Send .docx| TG_API
    SolverLoop -->|LREM (ACK)| RProc

    S_Redis --- Vol_Redis
    S_API --- Vol_Logs
    S_Bot --- Vol_Logs
    S_Worker --- Vol_Data
    S_Solver --- Vol_Logs
```

---

## 2. 🧩 Диаграмма классов и структур данных (Class Diagram)

Иерархия Pydantic-моделей, сервисных классов, пулов соединений и контрактов API.

```mermaid
classDiagram
    class BaseModel {
        <<Pydantic>>
    }

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
        +Optional~str~ remote_link
        +Optional~str~ remote_passcode
        +Optional~str~ remote_meeting_id
        +int number() property
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
        +date date
        +List~Lesson~ lessons
    }

    class WeekDayItem {
        +date date
        +List~Lesson~ lessons
    }

    class WeekScheduleResponse {
        +date monday
        +List~WeekDayItem~ days
    }

    class TeacherItem {
        +str full_name
        +str link_info
        +Optional~str~ zoom_url
        +Optional~str~ meeting_id
        +Optional~str~ passcode
    }

    class TeachersResponse {
        +List~TeacherItem~ teachers
    }

    class ExamsResponse {
        +List~ExamItem~ exams
    }

    class WopiSession {
        +str resource_url
        +str access_token
        +str lock_id
        +__init__(resource_url, access_token, lock_id)
    }

    class AttendanceSession {
        +str session_id
        +date target_date
        +int lesson_num
        +str subject
        +int poll_message_id
        +int summary_message_id
        +Dict~int, str~ student_marks
        +bool is_closed
        +datetime created_at
    }

    class ConnectionPool {
        <<Redis>>
        +int max_connections
        +bool socket_keepalive
        +int health_check_interval
        +float socket_timeout
    }

    class RedisClient {
        <<Redis Singleton>>
        +init_redis() Redis
        +get_redis() Redis
        +close_redis() void
        +get_redis_pool() ConnectionPool
    }

    class ApiClient {
        <<HTTP Client>>
        +fetch_day_schedule(target_date, force_refresh)
        +fetch_week_schedule(monday, force_refresh)
        +fetch_exams()
        +fetch_teachers(force_refresh)
        +get_api_schedule_for_date(target_date) List~Lesson~
    }

    class RedisCacheService {
        <<Service>>
        +cache_get(key)
        +cache_set(key, value, ttl)
        +save_schedule_snapshot(snapshot, meta, ttl)
        +load_schedule_snapshot() Tuple
        +pop_hw_task(timeout) dict
        +ack_hw_task(task_data) void
        +recover_stale_hw_tasks() int
        +is_reminder_sent(rem_key) bool
        +mark_reminder_sent(rem_key, ttl) void
        +register_message_for_cleanup(chat_id, msg_id, delay_sec) void
        +get_expired_messages_for_cleanup() List
    }

    BaseModel <|-- Lesson
    BaseModel <|-- ExamItem
    BaseModel <|-- DayScheduleResponse
    BaseModel <|-- WeekDayItem
    BaseModel <|-- WeekScheduleResponse
    BaseModel <|-- TeacherItem
    BaseModel <|-- TeachersResponse
    BaseModel <|-- ExamsResponse

    DayScheduleResponse "1" *-- "many" Lesson
    WeekDayItem "1" *-- "many" Lesson
    WeekScheduleResponse "1" *-- "many" WeekDayItem
    ExamsResponse "1" *-- "many" ExamItem
    TeachersResponse "1" *-- "many" TeacherItem

    RedisClient ..> ConnectionPool : manages
    RedisCacheService ..> RedisClient : uses
    ApiClient ..> DayScheduleResponse : parses
    ApiClient ..> WeekScheduleResponse : parses
```

---

## 3. 🔄 Диаграммы последовательности (Sequence Diagrams)

### 3.1. Синхронизация расписания топика и 10-минутные напоминания (Topic Sync & Ephemeral Reminders)

```mermaid
sequenceDiagram
    autonumber
    actor TG as Telegram Group Topic
    participant W as para-worker (TopicUpdater)
    participant API as para-api (/schedule/day)
    participant R as para-redis (Cache & ZSET)
    participant B as Telegram Bot

    loop Каждые 60 секунд
        W->>API: GET /schedule/day (target_date=today)
        API->>R: load_schedule_snapshot()
        alt Снимок есть в Redis (Cold/Warm hit)
            R-->>API: (snapshot, meta)
        else Снимка нет
            API->>KTMU: GET schedule-data-v2 (40MB)
            API->>API: filter_snapshot_for_target_group()
            API->>R: save_schedule_snapshot()
        end
        API-->>W: DayScheduleResponse (lessons)

        W->>W: Проверка изменений текста расписания
        alt Текст изменился
            W->>B: edit_message_text(TOPIC_CHAT_ID, main_msg_id)
            B->>TG: Обновление карточки текущей пары
        end

        loop Для каждой пары текущего дня
            W->>W: diff = start_time - now
            opt 0 < diff <= 600 сек (за 10 минут)
                W->>R: is_reminder_sent(rem_key)
                alt Еще не отправлялось
                    W->>B: send_message("Пара начнется через 10 минут!")
                    B->>TG: Доставка временного сообщения (msg_id)
                    W->>R: mark_reminder_sent(rem_key, ttl=86400)
                    W->>R: register_message_for_cleanup(chat_id, msg_id, delay=900)
                end
            end
        end

        W->>R: get_expired_messages_for_cleanup()
        R-->>W: List of expired [(chat_id, msg_id)]
        loop Каждое просроченное сообщение (>15 мин)
            W->>B: delete_message(chat_id, msg_id)
            B->>TG: Удаление временного сообщения
        end
    end
```

---

### 3.2. Отказоустойчивое решение домашних заданий (Reliable AI Homework Queue)

```mermaid
sequenceDiagram
    autonumber
    actor Student as Студент
    participant Bot as para-bot
    participant R as para-redis
    participant Solver as para-solver
    participant AI as DeepSeek API
    participant Topic as Топик «Готовое ДЗ»

    Student->>Bot: Присылает фото / документ с заданием
    Bot->>Bot: Валидация промпта & rate-limit
    Bot->>R: push_hw_task(task_data)
    R->>R: RPUSH hw:tasks:queue
    Bot-->>Student: ⏳ «Задание принято в обработку!»

    loop Worker Loop
        Solver->>R: BLMOVE hw:tasks:queue hw:tasks:processing (timeout=2)
        alt Задача поступила
            R-->>Solver: JSON task_data (атомарно в processing)
            Solver->>Bot: download_file(file_id)
            Bot-->>Solver: file_bytes
            Solver->>Solver: asyncio.to_thread(parse_file_payload)
            Solver->>AI: solve_homework(image_bytes, prompt)
            AI-->>Solver: Решение Markdown/LaTeX
            Solver->>Solver: asyncio.to_thread(create_solution_docx)
            Solver->>Bot: send_document(TOPIC_CHAT_ID, HW_OUTPUT_THREAD)
            Bot->>Topic: Публикация .docx файла по ГОСТ
            Solver->>R: ack_hw_task(task_data) [LREM processing]
        end
    end

    note over Solver,R: При аварийном рестарте воркера:
    Solver->>R: recover_stale_hw_tasks() [RPOPLPUSH processing -> queue]
```

---

### 3.3. Фиксация посещаемости в Яндекс Документы через WOPI (Attendance Workflow)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Староста / Зам
    participant Bot as para-bot
    participant AttMgr as AttendanceManager
    participant R as para-redis
    participant YDocs as YandexDocs (WOPI)
    participant YServer as docs.yandex.ru

    Admin->>Bot: /attendance (или выбор пары)
    Bot->>AttMgr: start_attendance_session(date, lesson_num)
    AttMgr->>R: Сохранение черновика (att:session:active)
    Bot-->>Admin: Интерактивный список студентов (кнопки П / У / Н / О)

    Admin->>Bot: Нажатие кнопки статуса студента
    Bot->>AttMgr: register_student_status(student_id, mark)
    AttMgr->>R: Обновление отметки в Redis
    Bot-->>Admin: Обновление счетчиков (Присутствуют / Болеют / Пропуск)

    Admin->>Bot: Кнопка «✅ Записать в таблицу»
    Bot->>AttMgr: commit_session_to_table()
    AttMgr->>YDocs: get_wopi_session(cookie)
    YDocs->>YServer: GET client-config & WOPI Access Token
    YServer-->>YDocs: WopiSession (access_token, lock_id)

    AttMgr->>YDocs: download_workbook(session)
    YServer-->>YDocs: Raw .xlsx bytes
    YDocs->>YDocs: asyncio.to_thread(load_workbook_from_bytes)
    YDocs->>YDocs: Заполнение столбца даты и пары метками
    YDocs->>YDocs: asyncio.to_thread(save_workbook_to_bytes)

    AttMgr->>YDocs: upload_workbook(session, wb)
    YDocs->>YServer: POST /contents (X-WOPI-Override: PUT)
    YServer-->>YDocs: HTTP 200 OK

    AttMgr->>YDocs: verify_upload(session, expected_marks)
    YDocs->>YServer: GET raw XML листа месяца
    YServer-->>YDocs: Sheet XML
    YDocs->>YDocs: Декодирование & валидация меток
    AttMgr->>R: Очистка сессии (is_closed=True)
    Bot-->>Admin: ✅ «Посещаемость успешно сохранена в Яндекс Документы!»
```

---

## 4. 🗄️ Схема данных и хранилищ (Entity-Relationship & Key Schema)

Структура данных постоянных JSON-файлов и ключей Redis.

```mermaid
erDiagram
    LESSON {
        int period PK "Индекс звонка (0..5)"
        string time_str "Интервал (например, 10:05–11:30)"
        string subject "Название предмета"
        string lesson_type "Лекция / Практика / Лабораторная"
        string teacher "ФИО преподавателя"
        string room "Номер кабинета"
        string address "Адрес корпуса"
        int subgroup "Подгруппа (0-общая, 1, 2)"
        boolean is_remote "Флаг дистанта"
        boolean is_stream "Потоковая пара"
        string remote_link "Zoom / Телемост ссылка"
        string remote_meeting_id "ID конференции Zoom"
        string remote_passcode "Код доступа Zoom"
    }

    EXAM_ITEM {
        string subject PK "Название дисциплины"
        string exam_type "Экзамен / Зачет / Дифф.зачет"
        string teacher "ФИО преподавателя"
        string room "Аудитория"
        string address "Адрес корпуса"
        string weeks "Учебные недели проведения"
        int subgroup "Подгруппа"
    }

    BIRTHDAY_RECORD {
        string full_name PK "ФИО одногруппника"
        int day "День рождения (1..31)"
        int month "Месяц (1..12)"
        int year "Год рождения"
        string username "Telegram @username"
        int tg_id "Telegram User ID"
    }

    SUBSCRIBER {
        int chat_id PK "ID чата подписчика"
        string full_name "Имя в Telegram"
        string username "Никнейм"
        string joined_at "Дата подписки"
    }

    REDIS_STORAGE {
        string key PK "Ключ Redis"
        string type "string / list / zset / hash"
        string ttl "Время жизни в секундах"
        string description "Назначение"
    }

    REDIS_STORAGE ||--o{ LESSON : "sched:group:snapshot"
    REDIS_STORAGE ||--o{ EXAM_ITEM : "exams:snapshot"
    REDIS_STORAGE ||--o{ BIRTHDAY_RECORD : "bday:cache:*"
    REDIS_STORAGE ||--o{ SUBSCRIBER : "subscribers:set"
```

### Реестр ключей Redis

| Ключ Redis | Тип | TTL | Описание |
| :--- | :--- | :--- | :--- |
| `sched:group:snapshot` | String (JSON) | 86400 сек (24ч) | Очищенный срез расписания для группы 1-КПД-3 (cold-start <2мс) |
| `sched:group:meta` | String (JSON) | 86400 сек (24ч) | Заголовки `ETag`, `Last-Modified`, `published_at` из API КТМУ |
| `hw:tasks:queue` | List (FIFO) | Бессрочно | Основная очередь входящих заданий на решение |
| `hw:tasks:processing` | List | Бессрочно | Задачи, находящиеся в процессе генерации AI (Reliable Queue) |
| `hw_processed:<msg_id>` | String ("1") | 30 дней | Защита от повторного решения одного и того же сообщения |
| `hw_hash:<sha256>` | String ("1") | 24 часа | Дедупликация идентичных запросов ДЗ |
| `rem:sent:<date>:<period>:<subgroup>` | String ("1") | 86400 сек | Идемпотентный флаг отправки 10-минутного напоминания в топик |
| `topic:main_msg_id` | String (int) | Бессрочно | ID главного зафиксированного сообщения топика расписания |
| `topic:cleanup_messages` | ZSET | До удаления | Очередь удаления временных сообщений (score = UNIX-таймштамп) |
| `att:session:active` | String (JSON) | 86400 сек | Активная сессия заполнения посещаемости пары старостой |
| `yandex:cookie:effective` | String | 604800 сек (7д) | Актуальные сессионные Cookie редактора Яндекс Документов |

---

## 5. 🛡️ Архитектурные правила и гарантии (Quality Attributes)

1. **Производительность (Latency & Throughput)**:
   - Кэширование расписания в Redis с поддержкой ETag/304 Not Modified.
   - Пул соединений `ConnectionPool` в Redis (`max_connections=20`) и `httpx.Limits` в HTTP-клиентах предотвращают постоянные рукопожатия TCP.
   - CPU-bound задачи (парсинг `openpyxl`, `docx`, `pdf`) изолированы в `asyncio.to_thread`, не блокируя Event Loop.
2. **Отказоустойчивость (Fault Tolerance)**:
   - Паттерн Reliable Queue (`BLMOVE` + `ACK` + `recover_stale_hw_tasks`) гарантирует доставку ДЗ даже при падении контейнера.
   - Изоляция состояния топика в Redis исключает дублирование сообщений при перезапуске воркера.
   - Docker Healthchecks и политика запуска `depends_on: condition: service_healthy` обеспечивают детерминированный порядок старта сервисов.
3. **Чистота кода (Code Standards)**:
   - Строгое ограничение: **все функции и методы <= 25 строк**.
   - Принцип единственной ответственности (SRP).
   - 100% покрытие unit-тестами критических путей (445 тестов).
