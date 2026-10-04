# 🏛️ Архитектура системы «para»

Техническая спецификация архитектуры, сквозных потоков данных (End-to-End Data Flow), объектных моделей и жизненного цикла распределенных процессов Telegram-бота группы, сервиса расписания и фоновых воркеров.

---

## 📑 Содержание

1. [Сквозная архитектура потоков данных (End-to-End Data Flow)](#1-сквозная-архитектура-потоков-данных)
2. [Диаграмма классов, моделей и сервисных контрактов](#2-диаграмма-классов-моделей-и-сервисных-контрактов)
3. [Сквозной процесс: Запрос и кэширование расписания](#3-сквозной-процесс-запрос-и-кэширование-расписания)
4. [Сквозной процесс: Уведомления о парах и очистка топика](#4-сквозной-процесс-уведомления-о-парах-и-очистка-топика)
5. [Сквозной процесс: Надежная очередь решения домашних заданий](#5-сквозной-процесс-надежная-очередь-решения-домашних-заданий)
6. [Сквозной процесс: Электронная ведомость посещаемости (WOPI)](#6-сквозной-процесс-электронная-ведомость-посещаемости-wopi)
7. [Модели сущностей и структура хранилища Redis](#7-модели-сущностей-и-структура-хранилища-redis)

---

## 1. Сквозная архитектура потоков данных

Архитектура построена по многоуровневой схеме (Layered Pipeline). Запросы и события проходят строго сверху вниз: от инициаторов через шлюзы и слой бизнес-логики в кэш и внешние системы.

```mermaid
flowchart TD
    subgraph L1["1. Слой инициаторов событий"]
        User["Студент / Пользователь"]
        Admin["Староста группы"]
        Timer["Системный таймер (APScheduler)"]
    end

    subgraph L2["2. Слой маршрутизации и шлюзов"]
        TG_Gate["Шлюз Telegram (Диспетчер событий)"]
        HTTP_Gate["Внутренний HTTP-контроллер"]
    end

    subgraph L3["3. Слой сервисов и бизнес-логики"]
        Schedule_Svc["Сервис расписания\n(нормализация и выборка пар)"]
        Topic_Svc["Сервис управления топиком\n(расчет звонков и статуса)"]
        Solver_Svc["Воркер решения ДЗ\n(обработка очереди и генератор Word)"]
        WOPI_Svc["WOPI-сервер ведомостей\n(интеграция с редактором таблиц)"]
    end

    subgraph L4["4. Слой состояния и очередей (Redis 7)"]
        R_Snapshot[("L2-кэш расписания\nsched:group:snapshot")]
        R_Queue[("Очередь задач ДЗ\nhw:tasks:queue")]
        R_Proc[("Обработка ДЗ\nhw:tasks:processing")]
        R_Zset[("Таймеры удаления сообщений\ntopic:cleanup_messages")]
        R_Sessions[("Сессии ведомостей\natt:session:*")]
        R_Flags[("Идемпотентные метки звонков\nrem:sent:*")]
    end

    subgraph L5["5. Слой внешних провайдеров и диска"]
        KTMU["Сервер расписания КТМУ"]
        DeepSeek["Модуль генерации решений"]
        YandexDocs["Облачный редактор документов"]
        YandexDisk["Хранилище Яндекс Диск"]
        DiskVolume["Файловый том ./data"]
    end

    %% Потоки инициации
    User -->|Команда расписания / Отправка ДЗ| TG_Gate
    Admin -->|Команда отметки посещаемости| TG_Gate
    Timer -->|Тик каждую минуту| Topic_Svc

    %% Потоки диспетчеризации
    TG_Gate -->|Запрос пар на день| HTTP_Gate
    TG_Gate -->|Постановка задачи в очередь| R_Queue
    TG_Gate -->|Старт сессии отметки| HTTP_Gate
    HTTP_Gate -->|Вызов логики| Schedule_Svc
    HTTP_Gate -->|Управление файлами| WOPI_Svc

    %% Потоки данных расписания
    Schedule_Svc -->|1. Проверка наличия снимка| R_Snapshot
    Schedule_Svc -->|2. При промахе: загрузка источника| KTMU
    Schedule_Svc -->|3. Сохранение снимка на 4 часа| R_Snapshot

    %% Потоки топика и звонков
    Topic_Svc -->|Запрос актуального расписания| HTTP_Gate
    Topic_Svc -->|Проверка: звонок уже отправлялся?| R_Flags
    Topic_Svc -->|Публикация напоминания| TG_Gate
    Topic_Svc -->|Регистрация сообщения на автоудаление| R_Zset
    Topic_Svc -->|Сборка истекших сообщений| R_Zset

    %% Потоки решения ДЗ (Reliable Queue)
    R_Queue -.->|Атомарный захват BLMOVE| R_Proc
    R_Proc -->|Чтение задачи| Solver_Svc
    Solver_Svc -->|Запрос на решение| DeepSeek
    Solver_Svc -->|Сборка документа Word по ГОСТ| DiskVolume
    Solver_Svc -->|Доставка файла студенту| TG_Gate
    Solver_Svc -->|Подтверждение выполнения LREM| R_Proc

    %% Потоки WOPI-ведомости
    Admin -->|Переход по ссылке| YandexDocs
    YandexDocs -->|Запрос проверки прав и контента| WOPI_Svc
    WOPI_Svc -->|Проверка токена доступа| R_Sessions
    WOPI_Svc -->|Синхронизация таблицы .xlsx| YandexDisk
    WOPI_Svc -->|Фиксация изменений| DiskVolume
```

---

## 2. Диаграмма классов, моделей и сервисных контрактов

Диаграмма описывает типизацию предметной области, структуру передаваемых ответов и контракты сервисов.

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
        +fetch_schedule(group) dict
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

    DayScheduleResponse "1" *-- "many" Lesson : содержит
    WeekScheduleResponse "1" *-- "many" DayScheduleResponse : содержит
    ExamsResponse "1" *-- "many" ExamItem : содержит

    ApiClient ..> DayScheduleResponse : возвращает
    ApiClient ..> WeekScheduleResponse : возвращает
    ApiClient ..> TeachersResponse : возвращает
    ApiClient ..> ExamsResponse : возвращает

    ScheduleParser ..> Lesson : парсит
    ScheduleParser ..> RedisPool : L2 кэш
    ScheduleParser ..> RedisCacheManager : сохранение снимка

    TopicUpdater --> ApiClient : запрашивает расписание
    TopicUpdater --> RedisCacheManager : флаги и очередь очистки
    TopicUpdater ..> Lesson : выводит в топик

    RedisCacheManager --> RedisPool : пул соединений
```

---

## 3. Сквозной процесс: Запрос и кэширование расписания

Цепочка движения данных при запросе расписания пользователем или фоновым воркером. Процесс гарантирует холодный старт за `<2мс` за счет снимка в Redis.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Студент / Воркер
    participant Bot as Telegram-бот
    participant API as Сервис расписания
    participant Redis as Кэш Redis
    participant KTMU as Сервер КТМУ

    Client->>Bot: Запрос: "Пары на сегодня"
    activate Bot
    Bot->>API: GET /schedule/day?group=...&date=...
    activate API

    API->>Redis: 1. Проверка снимка: GET sched:group:snapshot
    activate Redis
    
    alt Снимок найден в Redis (Штатный быстрый путь: <2мс)
        Redis-->>API: Готовый JSON расписания группы
    else Снимок отсутствует или истек (Холодный старт)
        Redis-->>API: nil (кэш пуст)
        API->>KTMU: 2. Загрузка исходных данных КТМУ (40 МБ)
        activate KTMU
        KTMU-->>API: Исходный JSON расписания всех групп
        deactivate KTMU
        API->>API: 3. Фильтрация и валидация в модели Lesson
        API->>Redis: 4. Запись снимка: SET sched:group:snapshot EX 14400
    end
    deactivate Redis

    API-->>Bot: Ответ: DayScheduleResponse (список пар)
    deactivate API

    Bot->>Bot: Форматирование красивого сообщения с аудиториями
    Bot-->>Client: Карточка расписания на день
    deactivate Bot
```

---

## 4. Сквозной процесс: Уведомления о парах и очистка топика

Цепочка ежеминутного контроля времени звонков, предотвращения повторов и автоудаления временных сообщений.

```mermaid
sequenceDiagram
    autonumber
    actor Scheduler as Воркер (каждые 60 сек)
    participant Updater as Сервис топика
    participant API as Сервис расписания
    participant Redis as Хранилище Redis
    participant Telegram as Чат группы

    Scheduler->>Updater: Запуск цикла проверки
    activate Updater

    Updater->>API: Запрос расписания на сегодня
    activate API
    API-->>Updater: Список занятий с временными интервалами
    deactivate API

    Updater->>Updater: Расчет интервалов звонков относительно текущего времени

    opt До начала пары или звонка осталось ровно 10 минут
        Updater->>Redis: 1. Проверка флага: EXISTS rem:sent:{group}:{date}:{period}:{type}
        activate Redis
        Redis-->>Updater: 0 (еще не отправлялось)
        deactivate Redis

        Updater->>Redis: 2. Фиксация флага отправки (TTL 2 часа)
        activate Redis
        Redis-->>Updater: OK
        deactivate Redis

        Updater->>Telegram: 3. Отправка сообщения: "Через 10 минут звонок на пару..."
        activate Telegram
        Telegram-->>Updater: Message(id = 8124)
        deactivate Telegram

        Updater->>Redis: 4. Регистрация на автоудаление через 15 минут:<br/>ZADD topic:cleanup_messages (now + 900) "chat:8124"
        activate Redis
        Redis-->>Updater: 1
        deactivate Redis
    end

    note over Updater,Redis: Процедура сбора устаревших сообщений
    Updater->>Redis: 5. Выборка истекших: ZRANGEBYSCORE topic:cleanup_messages -inf {now}
    activate Redis
    Redis-->>Updater: Список ID сообщений для удаления
    deactivate Redis

    loop Для каждого истекшего сообщения
        Updater->>Telegram: 6. Удаление сообщения из чата (deleteMessage)
        activate Telegram
        Telegram-->>Updater: OK
        deactivate Telegram

        Updater->>Redis: 7. Удаление записи из ZSET (ZREM)
        activate Redis
        Redis-->>Updater: 1
        deactivate Redis
    end

    deactivate Updater
```

---

## 5. Сквозной процесс: Надежная очередь решения домашних заданий

Паттерн **Reliable Queue**: исключает потерю задания студента при аварийном завершении воркера благодаря атомарному разделению очередей `queue` и `processing`.

```mermaid
sequenceDiagram
    autonumber
    actor Student as Студент
    participant Bot as Telegram-бот
    participant Queue as Redis (Queue)
    participant Processing as Redis (Processing)
    participant Solver as Воркер решений
    participant DeepSeek as Модуль решений
    participant WordGen as Генератор Word

    note over Solver,Processing: Автоматическое восстановление при старте воркера
    Solver->>Processing: 1. Проверка зависших задач при перезапуске
    activate Solver
    activate Processing
    Processing->>Queue: 2. Атомарный перенос RPOPLPUSH в основную очередь
    Processing-->>Solver: Восстановлено N задач
    deactivate Processing
    deactivate Solver

    Student->>Bot: 3. Отправка фото / текста домашнего задания
    activate Bot
    Bot->>Bot: Проверка формата и генерация ID задачи
    Bot->>Queue: 4. Постановка задачи: LPUSH hw:tasks:queue {id, user, task}
    activate Queue
    Queue-->>Bot: Номер в очереди
    deactivate Queue
    Bot-->>Student: Задание принято! Передано в обработку...
    deactivate Bot

    loop Непрерывное ожидание задач
        Solver->>Queue: 5. Атомарный захват задачи:<br/>BLMOVE hw:tasks:queue hw:tasks:processing 2 LEFT RIGHT
        activate Solver
        activate Queue
        activate Processing
        note over Queue,Processing: Задача извлекается из Queue и МГНОВЕННО<br/>оказывается в Processing. Потеря исключена.
        Processing-->>Solver: Данные задачи (JSON)
        deactivate Queue
        deactivate Processing

        Solver->>DeepSeek: 6. Запрос на пошаговое решение с формулами
        activate DeepSeek
        DeepSeek-->>Solver: Полный текст решения в Markdown
        deactivate DeepSeek

        Solver->>WordGen: 7. Сборка документа по ГОСТ (asyncio.to_thread)
        activate WordGen
        WordGen-->>Solver: Файл Решение_ДЗ.docx
        deactivate WordGen

        Solver->>Student: 8. Доставка готового документа студенту в Telegram

        Solver->>Processing: 9. Подтверждение выполнения: LREM hw:tasks:processing 1 task
        activate Processing
        Processing-->>Solver: 1 (задача закрыта)
        deactivate Processing
        deactivate Solver
    end
```

---

## 6. Сквозной процесс: Электронная ведомость посещаемости (WOPI)

Сквозная цепочка взаимодействия старосты, Telegram-бота, бэкенда и облачного редактора Яндекс Документов по стандарту WOPI.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Староста
    participant Bot as Telegram-бот
    participant Backend as WOPI-сервер
    participant Redis as Хранилище сессий
    participant Yandex as Яндекс Документы
    participant Disk as Яндекс Диск

    Admin->>Bot: 1. Нажатие кнопки «Отметить пару»
    activate Bot
    Bot->>Backend: 2. Инициализация сессии: POST /attendance/init
    activate Backend

    Backend->>Redis: 3. Создание сессии: SET att:session:{id} (TTL 1 час)
    activate Redis
    Redis-->>Backend: OK
    deactivate Redis

    Backend-->>Bot: 4. Ссылка на редактор и временный токен
    deactivate Backend
    Bot-->>Admin: 5. Сообщение с кнопкой «Открыть ведомость»
    deactivate Bot

    Admin->>Yandex: 6. Переход по ссылке ведомости
    activate Yandex

    note over Yandex,Backend: Протокол WOPI (Проверка прав и скачивание)
    Yandex->>Backend: 7. GET /wopi/files/{id}?access_token={token} (CheckFileInfo)
    activate Backend
    Backend->>Redis: 8. Валидация токена сессии
    activate Redis
    Redis-->>Backend: Токен действителен, доступ разрешен
    deactivate Redis
    Backend-->>Yandex: Метаданные (имя файла, размер, права на запись)
    deactivate Backend

    Yandex->>Backend: 9. GET /wopi/files/{id}/contents (Скачивание таблицы)
    activate Backend
    Backend->>Disk: 10. Чтение файла ведомости группы
    Disk-->>Backend: Бинарный поток .xlsx
    Backend-->>Yandex: Поток таблицы для открытия в редакторе
    deactivate Backend

    Yandex-->>Admin: Отображение таблицы со списком студентов в браузере

    Admin->>Yandex: 11. Проставление отметок (Н — отсутствовал, Б — болен)

    Yandex->>Backend: 12. POST /wopi/files/{id}/contents (Сохранение изменений)
    activate Backend
    Backend->>Disk: 13. Запись обновленной таблицы на Яндекс Диск
    Backend->>Redis: 14. Фиксация флага: SET att:committed:{group}:{date}:{period}
    activate Redis
    Redis-->>Backend: OK
    deactivate Redis
    Backend-->>Yandex: 200 OK (Сохранено)
    deactivate Backend

    Backend->>Bot: 15. Уведомление об успешной отметке
    activate Bot
    Bot-->>Admin: Отметки успешно зафиксированы в ведомости!
    deactivate Bot
    deactivate Yandex
```

---

## 7. Модели сущностей и структура хранилища Redis

### Диаграмма сущностей предметной области (ERD)

```mermaid
erDiagram
    DAY_SCHEDULE ||--|{ LESSON : "содержит пары дня"
    DAY_SCHEDULE ||--o{ ATTENDANCE_RECORD : "содержит отметки"

    DAY_SCHEDULE {
        date date PK "Дата занятий"
        string weekday "День недели"
        string group_name "Название группы"
    }

    LESSON {
        int period PK "Номер слота (0-5)"
        string time_str "Время пары"
        string subject "Дисциплина"
        string lesson_type "Тип (Лек / Пр / Лаб)"
        string teacher "Преподаватель"
        boolean is_remote "Дистанционный формат"
        string room "Аудитория"
        string address "Корпус"
        int subgroup "Подгруппа (0 - вся группа)"
    }

    ATTENDANCE_RECORD {
        int id PK "Идентификатор"
        string student_name "ФИО студента"
        date date "Дата пары"
        int period "Номер пары"
        string status "Отметка (Н, Б, У)"
    }

    EXAM_ITEM {
        int id PK "Идентификатор"
        string subject "Предмет"
        string exam_type "Форма контроля"
        string teacher "Преподаватель"
        string room "Аудитория"
        string weeks "Номера учебных недель"
    }

    BIRTHDAY_RECORD {
        string student_name PK "ФИО студента"
        string birthdate "День рождения (DD.MM)"
        bigint tg_id "Telegram ID"
    }
```

---

### Реестр ключей хранилища Redis

Таблица описывает все ключи, используемые в системе, их тип данных, время жизни и происхождение данных:

| Ключ / Шаблон ключа | Тип структуры | Время жизни (TTL) | Откуда поступает | Куда передается / Назначение |
| :--- | :--- | :--- | :--- | :--- |
| `sched:group:snapshot` | String (JSON) | 4 часа | Сервер КТМУ (после нормализации) | Сервис расписания: отдает готовые данные за `<2мс` без повторного разбора файлов |
| `hw:tasks:queue` | List (FIFO) | Бессрочно | Telegram-бот от студентов | Воркер решений: очередь входящих заданий на решение |
| `hw:tasks:processing` | List | Бессрочно | Очередь `hw:tasks:queue` (через `BLMOVE`) | Воркер решений: изоляция задачи на время генерации. Удаляется после успешной отправки |
| `topic:cleanup_messages` | Sorted Set (ZSET) | Динамический | Сервис топика при отправке напоминания | Сервис топика: сборщик устаревших сообщений каждые 60с по истечении 15 минут |
| `rem:sent:{group}:{date}:{period}:{type}` | String (флаг) | 2 часа | Сервис топика перед отправкой звонка | Предотвращение дублирования сообщений при частых перезапусках сервисов |
| `att:session:{session_id}` | String (JSON) | 1 час | Бэкенд при нажатии старостой кнопки | Редактор Яндекс Документов: валидация временного доступа по стандарту WOPI |
| `att:committed:{group}:{date}:{period}` | String (флаг) | 24 часа | WOPI-контроллер после сохранения таблицы | Бот и сервисы: статус того, что староста зафиксировал посещаемость на пару |
| `topic:schedule_msg_id:{group}` | String (int) | Бессрочно | Бот при первой публикации расписания | Сервис топика: ID главного закрепленного сообщения для обновления на месте |
