# 🏛️ Архитектура системы «para»

Техническое описание архитектуры, взаимосвязи микросервисов, моделей данных, распределенных очередей и сценариев работы Telegram-бота группы, внутреннего бэкенда расписания и фоновых воркеров.

---

## 📑 Содержание

1. [Компонентная структура и развертывание](#1-компонентная-структура-и-развертывание)
2. [Диаграмма классов и структур данных](#2-диаграмма-классов-и-структур-данных)
3. [Сценарий: Синхронизация топика и автоочистка уведомлений](#3-сценарий-синхронизация-топика-и-автоочистка-уведомлений)
4. [Сценарий: Надежная очередь решения задач](#4-сценарий-надежная-очередь-решения-задач)
5. [Сценарий: Фиксация посещаемости старостой](#5-сценарий-фиксация-посещаемости-старостой)
6. [Модели данных и структура хранилища Redis](#6-модели-данных-и-структура-хранилища-redis)
7. [Реестр ключей хранилища Redis](#реестр-ключей-хранилища-redis)

---

## 1. Компонентная структура и развертывание

Система развернута в изолированном окружении Docker Compose и взаимодействует через внутреннюю сеть `internal_bridge`.

```mermaid
flowchart TD
    subgraph External["Внешние платформы и пользователи"]
        User["Пользователь / Студент"]
        Admin["Староста / Администратор"]
        TG["Telegram"]
        KTMU["Сервер расписания КТМУ"]
        YD_DISK["Яндекс Диск"]
        YD_DOCS["Яндекс Документы"]
        DEEPSEEK["Модуль решений DeepSeek"]
    end

    subgraph Docker["Стек Docker Compose"]
        subgraph S_Redis["para-redis (Redis 7)"]
            RCache[("Снимок расписания")]
            RQueue[("Очередь задач ДЗ")]
            RProc[("Очередь обработки")]
            RClean[("ZSET очистки топика")]
            RSess[("Сессии посещаемости")]
            RFlags[("Идемпотентные флаги")]
        end

        subgraph S_API["para-api (FastAPI бэкенд)"]
            Rout_Sched["Контроллер расписания"]
            Rout_Exams["Контроллер сессии"]
            Rout_Teachers["Контроллер преподавателей"]
            Rout_Wopi["WOPI-контроллер"]
            Parser_Sched["Модуль парсинга КТМУ"]
        end

        subgraph S_Bot["para-bot (Telegram-бот)"]
            Bot_Dispatch["Диспетчер событий"]
            Bot_User["Пользовательские сценарии"]
            Bot_Admin["Административные функции"]
        end

        subgraph S_Worker["para-worker (Планировщик и задачи)"]
            Worker_Topic["Синхронизация топика"]
            Worker_Clean["Очистка уведомлений"]
            Worker_Digest["Утренний дайджест"]
            Worker_Keepalive["Продление сессий Яндекс"]
        end

        subgraph S_Solver["para-solver (Обработчик решений)"]
            Solver_Loop["Очередь обработки BLMOVE"]
            Solver_Docx["Генератор отчетов Word"]
        end
    end

    subgraph Storage["Файловое хранилище"]
        Vol_Data["Том данных ./data"]
        Vol_Redis["Том Redis ./data/redis"]
        Vol_Logs["Том логов ./logs"]
    end

    User -->|Команды и кнопки| TG
    Admin -->|Отметка пар, управление| TG
    TG -->|События| Bot_Dispatch
    Bot_Dispatch -->|Ответы| TG

    Bot_Dispatch --> Bot_User
    Bot_Dispatch --> Bot_Admin

    Bot_User -->|Запрос расписания| Rout_Sched
    Bot_User -->|Постановка задачи| RQueue
    Bot_Admin -->|Создание сессии| Rout_Wopi

    Rout_Sched --> Parser_Sched
    Parser_Sched -->|Загрузка данных| KTMU
    Rout_Sched -->|Чтение и запись снимка| RCache

    Worker_Topic -->|Запрос расписания дня| Rout_Sched
    Worker_Topic -->|Проверка отправки| RFlags
    Worker_Topic -->|Публикация в топик| TG
    Worker_Topic -->|Регистрация на удаление| RClean
    Worker_Clean -->|Выборка истекших| RClean
    Worker_Clean -->|Удаление звонков| TG

    Solver_Loop -->|Атомарный захват| RProc
    RQueue -.->|BLMOVE| RProc
    Solver_Loop -->|Генерация решения| DEEPSEEK
    Solver_Loop --> Solver_Docx
    Solver_Docx -->|Отправка готового документа| TG

    Admin -->|Редактирование ведомости| YD_DOCS
    YD_DOCS -->|WOPI-синхронизация| Rout_Wopi
    Rout_Wopi -->|Чтение и запись таблиц| YD_DISK

    RCache -.-> Vol_Redis
    Parser_Sched -.-> Vol_Data
    Solver_Docx -.-> Vol_Data
    Bot_Dispatch -.-> Vol_Logs
    Worker_Topic -.-> Vol_Logs
```

### Сводная таблица контейнеров

| Контейнер | Базовый образ | Сетевой порт | Зона ответственности |
| :--- | :--- | :--- | :--- |
| `para-redis` | `redis:7-alpine` | `6379` (внутренний) | Быстрый кэш снимка расписания, надежная очередь задач с `BLMOVE`, хранилище сессий и ZSET-таймеры очистки |
| `para-api` | Python 3.12 (slim) | `8000` (внутренний) | Внутренний сервис: нормализация расписания, обработка данных КТМУ, поддержка протокола WOPI для работы с таблицами |
| `para-bot` | Python 3.12 (slim) | Выход через SOCKS5 | Пользовательский интерфейс: обработка команд, интерактивные клавиатуры, опросы старосты, FSM-состояния |
| `para-worker` | Python 3.12 (slim) | — | Фоновый планировщик: синхронизация топика каждую минуту, автоочистка временных сообщений, утренние дайджесты |
| `para-solver` | Python 3.12 (slim) | — | Воркер решения задач: непрерывное чтение очереди, формирование решения, оформление документов в формате Word |

---

## 2. Диаграмма классов и структур данных

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

## 3. Сценарий: Синхронизация топика и автоочистка уведомлений

Синхронизация выполняется каждую минуту воркером `para-worker`.

```mermaid
sequenceDiagram
    autonumber
    actor Scheduler as Фоновый воркер
    participant Updater as Сервис топика
    participant Backend as Сервис расписания
    participant Redis as Хранилище Redis
    participant Bot as Бот
    actor Group as Чат группы

    loop Каждые 60 секунд
        Scheduler->>Updater: Запуск синхронизации
        activate Updater

        Updater->>Backend: Запрос расписания на сегодня
        activate Backend
        Backend->>Redis: Проверка снимка sched:group:snapshot
        activate Redis
        alt Снимок есть в кэше (<2мс)
            Redis-->>Backend: Данные снимка (JSON)
        else Снимок устарел
            Backend->>Backend: Загрузка с сервера КТМУ
            Backend->>Redis: Сохранение снимка на 4 часа
        end
        deactivate Redis
        Backend-->>Updater: Расписание дня (список пар)
        deactivate Backend

        Updater->>Updater: Расчет текущего звонка и остатка времени

        opt До начала или окончания пары ровно 10 минут
            Updater->>Redis: Проверка флага rem:sent:{group}:{date}:{period}:{type}
            activate Redis
            Redis-->>Updater: 0 (еще не отправлялось)
            deactivate Redis

            Updater->>Redis: Установка флага (TTL 2 часа)
            activate Redis
            Redis-->>Updater: OK
            deactivate Redis

            Updater->>Bot: Отправка уведомления в топик
            activate Bot
            Bot->>Group: Сообщение: "Через 10 минут звонок..."
            Group-->>Bot: ID сообщения (например, 5401)
            Bot-->>Updater: msg_id = 5401
            deactivate Bot

            Updater->>Redis: Регистрация в ZSET (score = now + 900, member = "chat:5401")
            activate Redis
            Redis-->>Updater: 1
            deactivate Redis
        end

        note over Updater,Redis: Процедура сборки устаревших сообщений
        Updater->>Redis: Запрос истекших: ZRANGEBYSCORE topic:cleanup_messages -inf {now}
        activate Redis
        Redis-->>Updater: Список ID сообщений
        deactivate Redis

        loop Для каждого истекшего сообщения
            Updater->>Bot: Удаление сообщения из чата
            activate Bot
            Bot->>Group: Удаление сообщения
            Group-->>Bot: Успешно
            Bot-->>Updater: OK
            deactivate Bot

            Updater->>Redis: Удаление из ZSET (ZREM)
            activate Redis
            Redis-->>Updater: 1
            deactivate Redis
        end

        deactivate Updater
    end
```

---

## 4. Сценарий: Надежная очередь решения задач

Очередь построена по принципу **Reliable Queue**: задача не теряется даже при падении или перезапуске воркера.

```mermaid
sequenceDiagram
    autonumber
    actor Student as Студент
    participant Bot as Telegram-бот
    participant Redis as Очередь Redis
    participant Solver as Воркер решений
    participant NeuralNet as Модуль DeepSeek
    participant Docx as Генератор Word

    note over Solver,Redis: Восстановление после сбоев (при старте воркера)
    Solver->>Redis: Проверка зависших задач в hw:tasks:processing
    activate Solver
    activate Redis
    Redis->>Redis: Атомарный перенос RPOPLPUSH в hw:tasks:queue
    Redis-->>Solver: Восстановлено N задач
    deactivate Redis
    deactivate Solver

    Student->>Bot: Загрузка задания (текст или фото)
    activate Bot
    Bot->>Bot: Валидация файла и генерация ID
    Bot->>Redis: LPUSH hw:tasks:queue {task_id, user_id, payload}
    activate Redis
    Redis-->>Bot: Размер очереди
    deactivate Redis
    Bot-->>Student: Задание принято! Приступаем к решению...
    deactivate Bot

    loop Постоянное чтение очереди
        Solver->>Redis: BLMOVE hw:tasks:queue hw:tasks:processing 2 LEFT RIGHT
        activate Solver
        activate Redis
        note over Solver,Redis: Атомарное перемещение: задача переходит в processing
        Redis-->>Solver: Данные задачи (JSON)
        deactivate Redis

        Solver->>NeuralNet: Запрос на генерацию решения (текст + изображения)
        activate NeuralNet
        NeuralNet-->>Solver: Пошаговое решение с формулами
        deactivate NeuralNet

        Solver->>Docx: Генерация документа по ГОСТ в отдельном потоке
        activate Docx
        Docx-->>Solver: Готовый файл solution.docx
        deactivate Docx

        Solver->>Student: Отправка готового документа в Telegram
        
        Solver->>Redis: Подтверждение: LREM hw:tasks:processing 1 task
        activate Redis
        Redis-->>Solver: 1 (задача закрыта)
        deactivate Redis
        deactivate Solver
    end
```

---

## 5. Сценарий: Фиксация посещаемости старостой

Интеграция со страницей редактирования Яндекс Документов по протоколу WOPI.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Староста
    participant Bot as Telegram-бот
    participant Backend as WOPI-сервер
    participant Redis as Хранилище сессий
    participant Yandex as Редактор документов

    Admin->>Bot: Нажатие «Отметить пару»
    activate Bot
    Bot->>Backend: Инициализация сессии посещаемости
    activate Backend
    
    Backend->>Redis: Сохранение сессии att:session:{id} (TTL 1 час)
    activate Redis
    Redis-->>Backend: OK
    deactivate Redis

    Backend-->>Bot: Ссылка на веб-редактор и временный токен
    deactivate Backend
    Bot-->>Admin: Кнопка: «Открыть электронную ведомость»
    deactivate Bot

    Admin->>Yandex: Переход по ссылке
    activate Yandex

    note over Yandex,Backend: Протокол WOPI (Проверка прав и скачивание)
    Yandex->>Backend: GET /wopi/files/{id}?access_token={token} (CheckFileInfo)
    activate Backend
    Backend->>Redis: Валидация токена сессии
    activate Redis
    Redis-->>Backend: Сессия подтверждена
    deactivate Redis
    Backend-->>Yandex: Метаданные файла (имя, размер, права на запись)
    deactivate Backend

    Yandex->>Backend: GET /wopi/files/{id}/contents (Скачивание таблицы)
    activate Backend
    Backend-->>Yandex: Бинарный поток файла .xlsx
    deactivate Backend

    Yandex-->>Admin: Отображение ведомости со списком группы

    Admin->>Yandex: Проставление отметок отсутствующих (Н, Б)

    Yandex->>Backend: POST /wopi/files/{id}/contents (Сохранение изменений)
    activate Backend
    Backend->>Backend: Проверка структуры и запись таблицы
    Backend->>Redis: Фиксация отметки: SET att:committed:{group}:{date}:{period}
    activate Redis
    Redis-->>Backend: OK
    deactivate Redis
    Backend-->>Yandex: 200 OK (Изменения сохранены)
    deactivate Backend

    Backend->>Bot: Уведомление об успешной фиксации
    activate Bot
    Bot-->>Admin: Отметки сохранены в ведомости группы
    deactivate Bot
    deactivate Yandex
```

---

## 6. Модели данных и структура хранилища Redis

### Диаграмма сущностей (ERD)

```mermaid
erDiagram
    DAY_SCHEDULE ||--|{ LESSON : "содержит пары"
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
        string teacher "ФИО преподавателя"
        boolean is_remote "Дистанционный формат"
        string room "Аудитория"
        string address "Корпус"
        int subgroup "Подгруппа (0 - вся группа)"
    }

    ATTENDANCE_RECORD {
        int id PK "Идентификатор"
        string student_name "Студент"
        date date "Дата"
        int period "Номер пары"
        string status "Отметка (Н, Б, У)"
    }

    EXAM_ITEM {
        int id PK "Идентификатор"
        string subject "Предмет"
        string exam_type "Зачет / Экзамен / КР"
        string teacher "Преподаватель"
        string room "Аудитория"
        string weeks "Номера недель"
    }

    BIRTHDAY_RECORD {
        string student_name PK "ФИО студента"
        string birthdate "Дата рождения (DD.MM)"
        bigint tg_id "Telegram ID"
    }
```

---

### Реестр ключей хранилища Redis

Все ключи структурированы по префиксам и имеют четко определенное время жизни (TTL):

| Префикс / Шаблон ключа | Тип данных | Время жизни (TTL) | Назначение |
| :--- | :--- | :--- | :--- |
| `sched:group:snapshot` | String (JSON) | 4 часа | Снимок расписания группы на текущую неделю. Позволяет отдавать расписание за `<2мс` без повторного разбора 40-мегабайтных файлов КТМУ |
| `hw:tasks:queue` | List (FIFO) | Бессрочно | Очередь задач на решение. Пополняется ботом по мере поступления заданий от студентов |
| `hw:tasks:processing` | List | Бессрочно | Задачи в процессе обработки. Часть паттерна Reliable Queue: задача атомарно перемещается сюда через `BLMOVE` и удаляется только после отправки решения |
| `topic:cleanup_messages` | Sorted Set (ZSET) | Динамический | Очередь автоудаления временных сообщений. В качестве `score` используется unix timestamp времени удаления (`now + 900`), `member` — `"chat_id:message_id"` |
| `rem:sent:{group}:{date}:{period}:{type}` | String (флаг) | 2 часа | Защита от дублирования звонков и напоминаний в топике группы при сбоях или частых перезапусках |
| `att:session:{session_id}` | String (JSON) | 1 час | Данные временной авторизованной сессии старосты для доступа к редактированию ведомости через веб-редактор |
| `att:committed:{group}:{date}:{period}` | String (флаг) | 24 часа | Отметка о том, что посещаемость на конкретную пару зафиксирована старостой |
| `topic:schedule_msg_id:{group}` | String (int) | Бессрочно | ID главного закрепленного сообщения с расписанием в топике для его обновления на месте |

---

## 7. Файлы диаграмм

Резервные копии схем в векторном формате также сохранены в каталоге `docs/puml/`:
- [Диаграмма развертывания](puml/01_deployment_and_containers.svg)
- [Диаграмма классов](puml/02_class_diagram.svg)
- [Синхронизация топика](puml/03_sequence_topic_updater.svg)
- [Очередь решений](puml/04_sequence_hw_solver.svg)
- [Ведомость посещаемости](puml/05_sequence_wopi_attendance.svg)
- [Модели данных](puml/06_erd_data_models.svg)
