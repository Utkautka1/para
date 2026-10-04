# 🏛️ Архитектура системы «para»

Техническая спецификация архитектуры, сквозных потоков данных (End-to-End Data Flow), объектных моделей и жизненного цикла распределенных процессов Telegram-бота группы, сервиса расписания и фоновых воркеров.

---

## 📑 Содержание

1. [Сквозная архитектура сервисов и системных контрактов](#1-сквозная-архитектура-сервисов-и-системных-контрактов)
2. [Диаграмма классов, моделей и сервисных контрактов](#2-диаграмма-классов-моделей-и-сервисных-контрактов)
3. [Сквозной процесс: Запрос и кэширование расписания](#3-сквозной-процесс-запрос-и-кэширование-расписания)
4. [Сквозной процесс: Уведомления о парах и очистка топика](#4-сквозной-процесс-уведомления-о-парах-и-очистка-топика)
5. [Сквозной процесс: Надежная очередь решения домашних заданий](#5-сквозной-процесс-надежная-очередь-решения-домашних-заданий)
6. [Сквозной процесс: Электронная ведомость посещаемости (WOPI)](#6-сквозной-процесс-электронная-ведомость-посещаемости-wopi)
7. [Модели сущностей и структура хранилища Redis](#7-модели-сущностей-и-структура-хранилища-redis)

---

## 1. Сквозная архитектура сервисов и системных контрактов

Архитектурная схема описывает взаимодействие распределенных компонентов системы: точки входа запросов, диспетчеры, сервисы бизнес-логики, узлы оперативной памяти и внешние интеграции.

```mermaid
classDiagram
    direction TB

    class TelegramGateway {
        +handle_schedule(chat_id, date) void
        +handle_hw_task(student_id, file) void
        +handle_attendance(admin_id) void
        +send_document(chat_id, docx) void
        +send_alert(chat_id, text) int
        +delete_msg(chat_id, msg_id) bool
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
    }

    class RedisStateManager {
        +get_snapshot(key) dict
        +set_snapshot(key, data, ttl) void
        +push_task(queue, item) void
        +blmove_task(src, dst) str
        +ack_task(dst, item) bool
        +check_flag(key) bool
        +set_flag(key, ttl) void
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

    TelegramGateway --> ScheduleApiService : HTTP GET расписание
    TelegramGateway --> RedisStateManager : LPUSH очереди ДЗ
    TelegramGateway --> WopiAttendanceService : POST старт сессии
    TopicWorkerService --> ScheduleApiService : запрос пар на сегодня
    TopicWorkerService --> RedisStateManager : проверка флагов и ZSET
    TopicWorkerService --> TelegramGateway : публикация звонков
    ScheduleApiService --> RedisStateManager : L2 кэш снимков
    ScheduleApiService ..> KTMUProvider : парсинг при промахе кэша
    HomeworkSolverService --> RedisStateManager : BLMOVE очереди ДЗ
    HomeworkSolverService --> DeepSeekProvider : генерация решения
    HomeworkSolverService --> TelegramGateway : отправка docx студенту
    WopiAttendanceService --> RedisStateManager : валидация токенов
    WopiAttendanceService --> YandexOfficeProvider : синхронизация таблицы
```

### Принципы межсервисного взаимодействия

1. **Изоляция очередей и диспетчеризации**: Шлюз Telegram не производит тяжелых вычислений и не ждет генерации файлов, а атомарно регистрирует задачу в очереди Redis (`LPUSH`).
2. **L2-кэширование**: Сервис расписания изолирует сервер КТМУ, отдавая готовые структуры занятий из снимка Redis за `<2мс`.
3. **Автономность воркеров**: Воркер топика и воркер решений ДЗ функционируют как независимые демоны, взаимодействуя с ботом через контракты очереди и вызовы сообщений.

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

    DayScheduleResponse "1" *-- "many" Lesson : содержит
    ApiClient ..> DayScheduleResponse : возвращает
    ScheduleParser ..> Lesson : парсит
    ScheduleParser --> RedisCacheManager : сохраняет и читает снимок
    ScheduleParser ..> KTMUProvider : загружает при промахе
```

### Логика движения данных в модуле расписания

1. **Проверка L2-кэша**: При входящем вызове `get_day_schedule` парсер сначала проверяет ключ `sched:group:snapshot` в Redis. Если снимок существует и не просрочен, данные десериализуются за `<2мс` без сетевых вызовов.
2. **Холодный старт**: При отсутствии ключа парсер обращается к серверу КТМУ, скачивает общий JSON-файл расписания (размером 40 МБ), производит фильтрацию по группе и валидацию полей в типизированные объекты `Lesson`.
3. **Фиксация снимка**: Нормализованный JSON сохраняется в Redis с TTL 14400 секунд (4 часа), гарантируя мгновенные ответы для всех последующих обращений.

---

## 4. Сквозной процесс: Уведомления о парах и очистка топика

Цепочка ежеминутного контроля времени звонков, предотвращения повторов и автоудаления временных сообщений.

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

    TopicUpdater --> RedisCacheManager : флаги отправки и очередь ZSET
    TopicUpdater --> TelegramChat : отправка и удаление звонков
    TopicUpdater ..> CallNotification : формирует
```

### Логика мониторинга звонков и топика

1. **Идемпотентность отправки**: Каждую минуту воркер рассчитывает время до ближайшей пары. Если до звонка осталось ровно 10 минут, проверяется флаг `rem:sent:{group}:{date}:{period}:{type}`. При значении 0 выставляется ключ с TTL 2 часа, исключая повторные отправки при рестартах воркера.
2. **Регистрация на автоудаление**: После успешной отправки уведомления ID сообщения помещается в Redis Sorted Set `topic:cleanup_messages` со score, равным `timestamp + 900` (15 минут).
3. **Сборщик устаревших записей**: Раз в минуту выполняется `ZRANGEBYSCORE topic:cleanup_messages -inf {now}`, сообщения удаляются из чата через `deleteMessage`, а записи очищаются через `ZREM`.

---

## 5. Сквозной процесс: Надежная очередь решения домашних заданий

Паттерн **Reliable Queue**: исключает потерю задания студента при аварийном завершении воркера благодаря атомарному разделению очередей `queue` и `processing`.

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
        +pop_hw_task(timeout) str
        +ack_hw_task(raw_task) bool
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

    SolverWorker --> RedisCacheManager : BLMOVE и LREM очереди
    SolverWorker ..> HomeworkTask : извлекает из JSON
    SolverWorker --> DeepSeekClient : пошаговое решение
    SolverWorker --> DocxParser : собирает Word по ГОСТ
```

### Надежная обработка задач генерации решений

1. **Атомарный захват (`BLMOVE`)**: Воркер извлекает задачу из `hw:tasks:queue` и одновременно помещает в `hw:tasks:processing`. Если контейнер воркера перезапустится в момент генерации, задача не будет потеряна.
2. **Восстановление при старте**: Функция `recover_stale_hw_tasks` при инициализации сервиса возвращает зависшие задачи из `processing` обратно в `queue` через `RPOPLPUSH`.
3. **Генерация по ГОСТ**: Модуль генерации оформляет текст и формулы в `.docx` с соблюдением стандартов (шрифт Times New Roman 14, поля 30-15-20-20 мм, нумерация страниц). После отправки документа в Telegram воркер подтверждает выполнение вызовом `LREM`.

---

## 6. Сквозной процесс: Электронная ведомость посещаемости (WOPI)

Сквозная цепочка взаимодействия старосты, Telegram-бота, бэкенда и облачного редактора Яндекс Документов по стандарту WOPI.

```mermaid
classDiagram
    direction TB

    class AttendanceSession {
        +str session_id
        +str group_name
        +date target_date
        +int period
        +int admin_id
        +str file_path
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

    WopiController --> RedisCacheManager : валидация сессий
    WopiController --> YandexDiskClient : чтение и запись xlsx
    WopiController ..> AttendanceSession : парсит сессию
    YandexDocsEditor --> WopiController : WOPI REST протокол
```

### Жизненный цикл сессии ведомости

1. **Инициализация сессии**: При нажатии старостой кнопки бот создает токен доступа и сохраняет сессию в Redis `att:session:{id}` с TTL 3600с.
2. **Интеграция с редактором**: Яндекс Документы обращаются к эндпоинтам контроллера:
   - `CheckFileInfo`: подтверждение прав доступа и структуры файла;
   - `GetFile`: загрузка исходной таблицы `.xlsx` с Яндекс Диска;
   - `PutFile`: сохранение измененного бинарного файла обратно в хранилище.
3. **Фиксация отметки**: После успешного закрытия файла выставляется флаг `att:committed:{group}:{date}:{period}`, подтверждающий учет посещаемости за пару.

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
