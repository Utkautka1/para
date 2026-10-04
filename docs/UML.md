# 🏛️ Архитектурная UML-документация проекта «para» (PlantUML)

Документация архитектуры, структуры классов, очередей сообщений и сценариев взаимодействия Telegram-бота расписания КТМУ, REST API и сервисов обработки на базе стандарта **PlantUML** с использованием специализированного скилла `plantuml` ([SpillwaveSolutions/plantuml](https://github.com/SpillwaveSolutions/plantuml)).

---

## 📑 Содержание

1. [Архитектура развертывания и компонентов (Deployment & Containers)](#1-архитектура-развертывания-и-компонентов)
2. [Диаграмма классов и контрактов данных (Class Diagram)](#2-диаграмма-классов-и-контрактов-данных)
3. [Сценарий: Синхронизация топика и автоочистка уведомлений (Sequence)](#3-сценарий-синхронизация-топика-и-автоочистка-уведомлений)
4. [Сценарий: Надежная очередь решения ДЗ на DeepSeek (Sequence)](#4-сценарий-надежная-очередь-решения-дз-на-deepseek)
5. [Сценарий: Фиксация посещаемости через WOPI Яндекс Документов (Sequence)](#5-сценарий-фиксация-посещаемости-через-wopi)
6. [Модели данных и структура ключей Redis (ERD & Key Storage)](#6-модели-данных-и-структура-ключей-redis)

---

## 1. Архитектура развертывания и компонентов

> 📄 **Исходный файл:** [`docs/puml/01_deployment_and_containers.puml`](file:///home/u/Рабочий%20стол/para/docs/puml/01_deployment_and_containers.puml)  
> 🖼️ **SVG векторная диаграмма:** [`docs/puml/01_deployment_and_containers.svg`](file:///home/u/Рабочий%20стол/para/docs/puml/01_deployment_and_containers.svg)

Диаграмма иллюстрирует 5 микросервисов в составе Docker Compose, постоянные тома данных и внешние облачные интеграции.

```plantuml
@startuml 01_deployment_and_containers
!theme cerulean

skinparam defaultFontName "sans-serif"
skinparam roundCorner 10
skinparam shadowing true
skinparam packageTitleAlignment left

title 🐳 Архитектура развертывания и компонентов проекта «para» (PlantUML)

cloud "🌐 Внешние сервисы и платформы" as external_cloud {
  actor "👤 Пользователь / Студент" as user
  actor "👑 Староста / Администратор" as admin
  node "✈️ Telegram Bot API" as tg_api
  node "🏫 API расписания КТМУ\n(timetable-ktmu.ru)" as ktmu_api
  node "📂 Яндекс Диск API" as yd_api
  node "📊 Яндекс Документы (WOPI)" as yd_wopi
  node "🧠 DeepSeek API (LLM/Vision)" as deepseek_api
}

node "🖥️ Продакшн сервер (ssh home)" as host_server {
  
  folder "📁 Монтируемые тома (Host Volumes)" as host_storage {
    storage "./data\n(Расписания, ДЗ, конфиги)" as vol_data
    storage "./data/redis\n(AOF/RDB персистентность)" as vol_redis
    storage "./logs\n(Логи сервисов)" as vol_logs
  }

  package "🐳 Docker Compose Стек (сеть: internal_bridge)" as docker_network {
    
    database "⚡ para-redis\n(Redis 7 Alpine)" as c_redis {
      component "Кэш снимков расписания\n(sched:group:snapshot)" as r_snap
      component "Надежная очередь ДЗ\n(hw:tasks:queue / processing)" as r_queue
      component "ZSET очистки топика\n(topic:cleanup_messages)" as r_zset
      component "Сессии посещаемости\n(att:session:*)" as r_sess
      component "Идемпотентные флаги\n(rem:sent:*, topic:*)" as r_flags
    }

    node "🚀 para-api\n(FastAPI + Uvicorn :8000)" as c_api {
      component "Schedule Router\n(/api/v1/schedule)" as api_sched
      component "Teachers Router\n(/api/v1/teachers)" as api_teach
      component "Exams Router\n(/api/v1/exams)" as api_exams
      component "WOPI Controller\n(/wopi/files/*)" as api_wopi
      component "HTTP Client Pool\n(Keepalive=10, Max=20)" as api_pool
    }

    node "🤖 para-bot\n(Aiogram 3 Dispatcher)" as c_bot {
      component "SOCKS5 Proxy Client" as bot_proxy
      component "User Handlers\n(Команды, inline-кнопки)" as bot_user
      component "Admin Handlers\n(Опросы, отметки пар)" as bot_admin
      component "FSM & Local States" as bot_fsm
    }

    node "⏱️ para-worker\n(APScheduler Tasks)" as c_worker {
      component "Topic Sync Task (каждые 60с)\n(Расписание и таймеры пар)" as worker_topic
      component "ZSET Cleaner Task (каждые 60с)\n(Удаление 15-мин уведомлений)" as worker_clean
      component "Yandex Keepalive (каждые 6ч)\n(Обновление токенов диска)" as worker_yd
    }

    node "🧠 para-solver\n(DeepSeek Solver Worker)" as c_solver {
      component "Queue Consumer\n(BLMOVE hw:tasks:queue)" as solver_worker
      component "Vision & Text Prompting" as solver_prompt
      component "Docx GOST Generator\n(asyncio.to_thread)" as solver_docx
    }
  }
}

' Связи пользователей
user --> tg_api : Telegram чат
admin --> tg_api : Управление ботом

' Внешние взаимодействия
tg_api <--> bot_proxy : Polling / Ответы
c_api --> ktmu_api : Загрузка расписания
c_api <--> yd_wopi : WOPI REST протокол
c_api --> yd_api : Чтение таблиц
c_solver --> deepseek_api : Решение задач (AI)

' Внутреннее взаимодействие Docker Compose
c_bot --> c_api : HTTP REST (внутренний порт 8000)
c_bot --> c_redis : Состояния, сессии, очередь ДЗ
c_worker --> c_api : Запрос актуального дня
c_worker --> c_redis : ZSET таймеры, идемпотентность
c_worker --> tg_api : Обновление топика и звонков
c_solver --> c_redis : BLMOVE / ACK задач
c_solver --> tg_api : Отправка готового решения docx

' Связи с хранилищем
c_redis ..> vol_redis : Сохранение данных
c_api ..> vol_data : Чтение шаблонов
c_solver ..> vol_data : Запись сгенерированных .docx
c_bot ..> vol_logs : Запись логов
c_worker ..> vol_logs : Запись логов

@enduml
```

---

## 2. Диаграмма классов и контрактов данных

> 📄 **Исходный файл:** [`docs/puml/02_class_diagram.puml`](file:///home/u/Рабочий%20стол/para/docs/puml/02_class_diagram.puml)  
> 🖼️ **SVG векторная диаграмма:** [`docs/puml/02_class_diagram.svg`](file:///home/u/Рабочий%20стол/para/docs/puml/02_class_diagram.svg)

Диаграмма описывает строгую типизацию моделей Pydantic, схем FastAPI, синглтонов пулов соединений и сервисов.

```plantuml
@startuml 02_class_diagram
!theme cerulean

skinparam defaultFontName "sans-serif"
skinparam classAttributeIconSize 0
skinparam roundCorner 8
skinparam shadowing true

title 🏛️ Диаграмма классов, моделей и сервисных контрактов (PlantUML)

package "services.models (Общие Pydantic-модели)" <<Rectangle>> {
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
    +Optional[str] remote_link
    +Optional[str] remote_passcode
    +Optional[str] remote_meeting_id
    +int number() : property
  }

  class ExamItem {
    +str subject
    +str exam_type
    +str teacher
    +str room
    +str address
    +List[int] weeks
    +int subgroup
    +str format_str
  }
}

package "api.schemas (Схемы REST API)" <<Rectangle>> {
  class DayScheduleResponse {
    +str date
    +str weekday
    +List[Lesson] lessons
  }

  class WeekScheduleResponse {
    +int week_number
    +List[DayScheduleResponse] days
  }

  class TeachersResponse {
    +List[str] teachers
    +int total_count
  }

  class ExamsResponse {
    +str group_name
    +List[ExamItem] exams
  }
}

package "core (Инфраструктурные синглтоны)" <<Rectangle>> {
  class RedisPool {
    -{static} ConnectionPool _pool
    +{static} get_pool() : ConnectionPool
    +{static} get_redis_client() : Redis
  }

  class ApiClient {
    -httpx.AsyncClient _client
    -str base_url
    -httpx.Limits limits
    +get_day_schedule(group, date) : DayScheduleResponse
    +get_week_schedule(group, week) : WeekScheduleResponse
    +get_teachers() : TeachersResponse
    +get_exams(group) : ExamsResponse
    +close() : None
  }
}

package "services (Бизнес-логика и парсеры)" <<Rectangle>> {
  class ScheduleParser {
    -dict _in_memory_cache
    -float _cache_timestamp
    +fetch_schedule(group) : dict
    +get_day(group, target_date) : List[Lesson]
    +get_week(group, week_num) : dict
    +load_schedule_snapshot(group) : Optional[dict]
    +save_schedule_snapshot(group, data) : None
  }

  class RedisCacheManager {
    +save_snapshot(group, payload) : bool
    +load_snapshot(group) : Optional[dict]
    +pop_hw_task(timeout) : Optional[str]
    +ack_hw_task(raw_task) : bool
    +recover_stale_hw_tasks() : int
    +is_reminder_sent(key) : bool
    +mark_reminder_sent(key, ttl) : None
    +register_message_for_cleanup(chat_id, msg_id, delay) : None
    +get_expired_messages_for_cleanup() : List[tuple]
  }

  class TopicUpdater {
    -int chat_id
    -int topic_id
    +sync_topic_schedule() : None
    +send_call_reminder(lesson, call_type) : None
    +cleanup_expired_messages() : None
    -calculate_current_call(now_time) : Optional[dict]
  }

  class DocxParserService {
    +parse_docx_teachers(file_path) : List[str]
    +create_solution_docx(task_text, solution_text, output_path) : str
  }

  class WopiSessionManager {
    +create_attendance_session(group, date, period) : str
    +get_session_status(session_id) : dict
    +commit_attendance(session_id, marks_data) : bool
  }
}

' Отношения между моделями и схемами
DayScheduleResponse "1" *-- "many" Lesson : содержит
WeekScheduleResponse "1" *-- "many" DayScheduleResponse : содержит
ExamsResponse "1" *-- "many" ExamItem : содержит

' Отношения между сервисами и клиентами
ApiClient ..> DayScheduleResponse : возвращает
ApiClient ..> WeekScheduleResponse : возвращает
ApiClient ..> TeachersResponse : возвращает
ApiClient ..> ExamsResponse : возвращает

ScheduleParser ..> Lesson : парсит и создает
ScheduleParser ..> RedisPool : использует кэш L2
ScheduleParser ..> RedisCacheManager : снимки расписания

TopicUpdater --> ApiClient : запрашивает расписание
TopicUpdater --> RedisCacheManager : флаги и ZSET очистки
TopicUpdater ..> Lesson : отображает в топике

RedisCacheManager --> RedisPool : берет соединение

WopiSessionManager --> RedisCacheManager : хранит состояние сессии
@enduml
```

---

## 3. Сценарий: Синхронизация топика и автоочистка уведомлений

> 📄 **Исходный файл:** [`docs/puml/03_sequence_topic_updater.puml`](file:///home/u/Рабочий%20стол/para/docs/puml/03_sequence_topic_updater.puml)  
> 🖼️ **SVG векторная диаграмма:** [`docs/puml/03_sequence_topic_updater.svg`](file:///home/u/Рабочий%20стол/para/docs/puml/03_sequence_topic_updater.svg)

Отображает процесс ежеминутной синхронизации топика группы:
1. Запрос расписания из L2-кэша Redis (`<2мс`).
2. Определение текущей пары и расписания звонков.
3. Проверка идемпотентного ключа в Redis (`rem:sent:...`).
4. Отправка временного напоминания и регистрация в `Redis ZSET` (`topic:cleanup_messages`).
5. Автоудаление истекших временных сообщений через 15 минут.

```plantuml
@startuml 03_sequence_topic_updater
!theme cerulean

skinparam defaultFontName "sans-serif"
skinparam roundCorner 8
skinparam shadowing true
autonumber

title ⏱️ Последовательность: Синхронизация топика и автоочистка уведомлений (PlantUML)

actor "⏱️ APScheduler\n(para-worker)" as scheduler
participant "🔄 TopicUpdater\n(сервис)" as updater
participant "🚀 para-api\n(FastAPI)" as api
database "⚡ para-redis\n(Redis 7)" as redis
participant "🤖 Aiogram Bot\n(Telegram API)" as bot
actor "👥 Чат группы\n(Telegram Topic)" as telegram

loop Каждые 60 секунд
  scheduler -> updater : trigger_topic_sync()
  activate updater

  updater -> api : GET /api/v1/schedule/day?group=...&date=today
  activate api
  
  api -> redis : GET sched:group:snapshot
  activate redis
  alt Снимок найден в Redis (<2мс)
    redis --> api : JSON снимка расписания
  else Снимок отсутствует (Cold start)
    api -> api : fetch_remote_schedule() (API КТМУ)
    api -> redis : SET sched:group:snapshot (TTL 4ч)
  end
  deactivate redis
  
  api --> updater : 200 OK (DayScheduleResponse)
  deactivate api

  updater -> updater : calculate_current_call(now)
  note right of updater
    Определение статуса:
    - До начала занятий
    - Идёт пара (осталось N минут)
    - Перемена (до следующей пары M минут)
  end note

  opt Наступило время напоминания (за 10 мин до звонка)
    updater -> redis : EXISTS rem:sent:{group}:{date}:{period}:{type}
    activate redis
    redis --> updater : 0 (ещё не отправлялось)
    deactivate redis

    updater -> redis : SET rem:sent:{group}:{date}:{period}:{type} 1 EX 7200
    activate redis
    redis --> updater : OK (идемпотентный флаг установлен)
    deactivate redis

    updater -> bot : send_message(chat_id, text, message_thread_id)
    activate bot
    bot -> telegram : Отправка временного уведомления в топик
    telegram --> bot : Message(message_id=9872)
    bot --> updater : message_id = 9872
    deactivate bot

    updater -> redis : ZADD topic:cleanup_messages (now + 900) "chat_id:9872"
    activate redis
    redis --> updater : 1 (зарегистрировано на удаление через 15 мин)
    deactivate redis
  end

  group Очистка устаревших эфемерных сообщений (ZSET Garbage Collection)
    updater -> redis : ZRANGEBYSCORE topic:cleanup_messages -inf {now_timestamp}
    activate redis
    redis --> updater : ["chat_id:9872", ...]
    deactivate redis

    loop Для каждого истекшего сообщения
      updater -> bot : delete_message(chat_id, 9872)
      activate bot
      bot -> telegram : Удаление сообщения из топика
      telegram --> bot : OK
      bot --> updater : Удалено
      deactivate bot

      updater -> redis : ZREM topic:cleanup_messages "chat_id:9872"
      activate redis
      redis --> updater : 1
      deactivate redis
    end
  end

  deactivate updater
end

@enduml
```

---

## 4. Сценарий: Надежная очередь решения ДЗ на DeepSeek

> 📄 **Исходный файл:** [`docs/puml/04_sequence_hw_solver.puml`](file:///home/u/Рабочий%20стол/para/docs/puml/04_sequence_hw_solver.puml)  
> 🖼️ **SVG векторная диаграмма:** [`docs/puml/04_sequence_hw_solver.svg`](file:///home/u/Рабочий%20стол/para/docs/puml/04_sequence_hw_solver.svg)

Реализация паттерна **Reliable Queue**:
1. Атомарный перенос задач из очереди ожидания в очередь обработки через `BLMOVE`.
2. Автоматическое восстановление зависших задач при перезапуске сервиса (`recover_stale_hw_tasks`).
3. Асинхронное обращение к DeepSeek AI и генерация `.docx` по ГОСТу в пуле потоков `asyncio.to_thread`.
4. Подтверждение выполнения через `ack_hw_task`.

```plantuml
@startuml 04_sequence_hw_solver
!theme cerulean

skinparam defaultFontName "sans-serif"
skinparam roundCorner 8
skinparam shadowing true
autonumber

title 🧠 Последовательность: Надежная очередь решения ДЗ на DeepSeek (PlantUML)

actor "👤 Студент" as user
participant "🤖 para-bot\n(Telegram Handlers)" as bot
database "⚡ para-redis\n(Reliable Queue)" as redis
participant "⚙️ para-solver\n(Worker Service)" as solver
participant "🧠 DeepSeek API\n(LLM & Vision)" as deepseek
participant "📄 Docx Service\n(asyncio.to_thread)" as docx

== Фаза 1: Crash Recovery при запуске контейнера para-solver ==

solver -> redis : recover_stale_hw_tasks()
activate solver
activate redis
note over solver, redis
  Если контейнер упал во время обработки задачи,
  она осталась в списке hw:tasks:processing.
  При старте воркер атомарно возвращает её в очередь.
end note
redis -> redis : RPOPLPUSH hw:tasks:processing hw:tasks:queue
redis --> solver : Число восстановленных задач (N)
deactivate redis
deactivate solver

== Фаза 2: Постановка задачи студентом ==

user -> bot : Загрузка задания (текст / фото ДЗ)
activate bot
bot -> bot : Валидация файла и генерация task_id
bot -> redis : LPUSH hw:tasks:queue JSON(task_id, user_id, payload)
activate redis
redis --> bot : Длина очереди
deactivate redis
bot --> user : ⏳ Задание принято в очередь! Решаем...
deactivate bot

== Фаза 3: Атомарный захват и решение (Reliable Queue Pattern) ==

loop Бесконечный цикл обработки очереди
  solver -> redis : BLMOVE hw:tasks:queue hw:tasks:processing 2 LEFT RIGHT
  activate solver
  activate redis
  note over solver, redis
    Атомарный перенос задачи:
    Задача извлекается из queue и мгновенно помещается
    в processing. Потеря при сбое воркера исключена!
  end note
  redis --> solver : raw_task (JSON данные задачи)
  deactivate redis

  solver -> solver : parse_file_payload(raw_task)

  solver -> deepseek : chat.completions.create(prompt, images)
  activate deepseek
  deepseek --> solver : Решение задачи (Markdown / формулы / шаги)
  deactivate deepseek

  solver -> docx : asyncio.to_thread(create_solution_docx)
  activate docx
  note right of docx
    Тяжелая генерация Word-документа
    по ГОСТ вынесена в отдельный системный
    поток, чтобы не блокировать asyncio event loop.
  end note
  docx --> solver : Сформированный файл solution.docx
  deactivate docx

  solver -> user : Отправка solution.docx студенту в Telegram
  
  solver -> redis : ack_hw_task(raw_task) -> LREM hw:tasks:processing 1 raw_task
  activate redis
  redis --> solver : 1 (Задача успешно завершена и удалена)
  deactivate redis
  deactivate solver
end

@enduml
```

---

## 5. Сценарий: Фиксация посещаемости через WOPI

> 📄 **Исходный файл:** [`docs/puml/05_sequence_wopi_attendance.puml`](file:///home/u/Рабочий%20стол/para/docs/puml/05_sequence_wopi_attendance.puml)  
> 🖼️ **SVG векторная диаграмма:** [`docs/puml/05_sequence_wopi_attendance.svg`](file:///home/u/Рабочий%20стол/para/docs/puml/05_sequence_wopi_attendance.svg)

Сценарий работы старосты с ведомостью через протокол WOPI (Web Application Open Platform Interface) и облачный редактор Яндекс Документов.

```plantuml
@startuml 05_sequence_wopi_attendance
!theme cerulean

skinparam defaultFontName "sans-serif"
skinparam roundCorner 8
skinparam shadowing true
autonumber

title 📊 Последовательность: Фиксация посещаемости старостой через WOPI (PlantUML)

actor "👑 Староста" as admin
participant "🤖 para-bot\n(Telegram Handlers)" as bot
participant "🚀 para-api\n(WOPI Host)" as api
database "⚡ para-redis\n(Сессии и токены)" as redis
participant "📊 Яндекс Документы\n(WOPI Client / Cloud Editor)" as yandex_docs

== Шаг 1: Инициализация сессии отметки ==

admin -> bot : Нажатие кнопки «Отметить пару»
activate bot
bot -> api : POST /api/v1/attendance/init (group, date, period)
activate api

api -> redis : SET att:session:{session_id} JSON(user_id, file_id) EX 3600
activate redis
redis --> api : OK (токен сессии активен 1 час)
deactivate redis

api --> bot : 200 OK (wopi_client_url, access_token)
deactivate api

bot --> admin : Inline-кнопка: «Открыть электронную ведомость» 📝
deactivate bot

== Шаг 2: Рукопожатие по протоколу WOPI (Handshake) ==

admin -> yandex_docs : Переход по ссылке ведомости
activate yandex_docs

yandex_docs -> api : GET /wopi/files/{file_id}?access_token={token}
activate api
note over yandex_docs, api
  WOPI протокол: Запрос метаданных файла (CheckFileInfo).
  Проверяются права на чтение/запись и имя файла.
end note

api -> redis : GET att:session:{session_id}
activate redis
redis --> api : Данные авторизованной сессии
deactivate redis

api --> yandex_docs : 200 OK JSON { BaseFileName, Size, UserCanWrite: true }
deactivate api

yandex_docs -> api : GET /wopi/files/{file_id}/contents?access_token={token}
activate api
api --> yandex_docs : 200 OK (бинарный поток таблицы посещаемости .xlsx)
deactivate api

yandex_docs --> admin : Отображение интерфейса таблицы Excel в браузере

== Шаг 3: Редактирование и сохранение изменений (Save / PutFile) ==

admin -> yandex_docs : Проставление отметок (Н - отсутствовал, Б - болен)

yandex_docs -> api : POST /wopi/files/{file_id}/contents (X-WOPI-Override: PUT)
activate api
note over yandex_docs, api
  Яндекс Документы передают обновлённый файл
  на сервер бэкенда para-api.
end note

api -> api : Валидация структуры OpenXML и запись на диск
api -> redis : SET att:committed:{group}:{date}:{period} 1
activate redis
redis --> api : OK
deactivate redis

api --> yandex_docs : 200 OK (Зафиксировано успешно)
deactivate api

api -> bot : Внутреннее уведомление: отметки зафиксированы
activate bot
bot --> admin : ✅ Ведомость успешно обновлена и сохранена на Яндекс Диске!
deactivate bot
deactivate yandex_docs

@enduml
```

---

## 6. Модели данных и структура ключей Redis

> 📄 **Исходный файл:** [`docs/puml/06_erd_data_models.puml`](file:///home/u/Рабочий%20стол/para/docs/puml/06_erd_data_models.puml)  
> 🖼️ **SVG векторная диаграмма:** [`docs/puml/06_erd_data_models.svg`](file:///home/u/Рабочий%20стол/para/docs/puml/06_erd_data_models.svg)

Схема сущностей предметной области и карта ключей Redis с типами данных и политиками устаревания (TTL).

```plantuml
@startuml 06_erd_data_models
!theme cerulean

skinparam defaultFontName "sans-serif"
skinparam roundCorner 8
skinparam shadowing true

title 🗄️ Диаграмма сущностей (ERD) и схема хранилища Redis (PlantUML)

' Описание моделей данных
entity "LESSON" as lesson {
  * period : int <<PK>>
  --
  * time_str : varchar(32)
  * subject : varchar(255)
  * lesson_type : varchar(64)
  * teacher : varchar(128)
  * is_remote : boolean
  * room : varchar(64)
  * address : varchar(255)
  subgroup : int
  is_stream : boolean
  remote_link : text
  remote_passcode : varchar(64)
  remote_meeting_id : varchar(64)
}

entity "EXAM_ITEM" as exam {
  * id : int <<PK>>
  --
  * subject : varchar(255)
  * exam_type : varchar(64)
  * teacher : varchar(128)
  * room : varchar(64)
  * address : varchar(255)
  * weeks : json_array
  subgroup : int
  format_str : varchar(32)
}

entity "DAY_SCHEDULE" as day_sched {
  * date : date <<PK>>
  --
  * weekday : varchar(32)
  * group_name : varchar(64)
}

entity "ATTENDANCE_RECORD" as attendance {
  * id : int <<PK>>
  --
  * student_name : varchar(128)
  * date : date
  * period : int
  * status : varchar(16) 'Н, Б, У, П
  updated_at : timestamp
}

entity "BIRTHDAY_RECORD" as birthday {
  * student_name : varchar(128) <<PK>>
  --
  * birthdate : varchar(10) 'DD.MM
  tg_id : bigint
  is_celebrated : boolean
}

' Связи между сущностями
day_sched ||--|{ lesson : "содержит пары дня"
day_sched ||--o{ attendance : "фиксирует отметки"

' Реестр структур данных в Redis
package "⚡ Redis Key Schema (In-Memory Datastore)" <<Database>> {
  class "sched:group:snapshot" as r_sched {
    Тип: STRING (JSON)
    TTL: 4 часа
    Назначение: Полный снимок расписания группы для быстрого холодного старта (<2мс)
  }

  class "hw:tasks:queue" as r_hw_q {
    Тип: LIST (FIFO)
    TTL: Бессрочно
    Назначение: Очередь задач ДЗ для воркера DeepSeek AI
  }

  class "hw:tasks:processing" as r_hw_p {
    Тип: LIST
    TTL: Бессрочно
    Назначение: Задачи в обработке (Reliable Queue BLMOVE). Авто-восстановление при краше
  }

  class "topic:cleanup_messages" as r_zset {
    Тип: ZSET (Sorted Set)
    TTL: Динамический
    Score: Unix timestamp истечения (now + 900)
    Member: "chat_id:message_id"
    Назначение: Фоновая очистка временных сообщений звонков через 15 минут
  }

  class "rem:sent:{group}:{date}:{period}:{type}" as r_rem {
    Тип: STRING
    TTL: 2 часа
    Назначение: Идемпотентный флаг защиты от дублирования звонков в топик
  }

  class "att:session:{session_id}" as r_att {
    Тип: STRING (JSON)
    TTL: 1 час
    Назначение: Авторизованная сессия старосты для редактирования ведомости по WOPI
  }
}

@enduml
```
