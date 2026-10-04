# 📋 Заметки по реализации (Implementation Notes)

## Задача
Переделка UML-диаграмм всей системы с использованием специализированного скилла **PlantUML** (`SpillwaveSolutions/plantuml`).

---

## План работ
1. **Подготовка и установка скилла**:
   - Установлен скилл `plantuml` из `https://github.com/SpillwaveSolutions/plantuml.git` в `~/.gemini/config/skills/plantuml` и локально в проект `.agents/skills/plantuml`.
   - Загрузка `plantuml.jar` для локальной генерации изображений / валидации синтаксиса.
2. **Проектирование диаграмм в нотации PlantUML**:
   - **Архитектура развертывания и компонентов (Deployment & Component Diagram)**: 5 контейнеров (`para-redis`, `para-api`, `para-bot`, `para-worker`, `para-solver`), взаимодействие через сеть `internal_bridge`, монтируемые тома, внешние API (Telegram, КТМУ, DeepSeek, Яндекс Диск/Документы WOPI).
   - **Диаграмма классов и структур данных (Class Diagram)**: Pydantic-модели (`Lesson`, `ExamItem`), схемы API (`DayScheduleResponse`, `WeekScheduleResponse`, etc.), клиенты `RedisClient`, `ApiClient`, контекстные менеджеры сессий WOPI.
   - **Диаграммы последовательностей (Sequence Diagrams)**:
     - Фоновая синхронизация расписания в топик и очистка уведомлений.
     - Надежная очередь решения домашних заданий через DeepSeek AI (`BLMOVE`, `ack_hw_task`, `recover_stale_hw_tasks`).
     - Сессия опроса посещаемости старостой и двухфазная фиксация в Яндекс Документах по протоколу WOPI.
   - **Диаграмма сущностей и схема данных (Entity-Relationship & Key Storage Diagram)**: Структуры данных и детальная карта ключей Redis с типами и TTL.
3. **Размещение файлов**:
   - Исходные `.puml` файлы в `docs/puml/`.
   - Единый сводный документ `docs/UML.md` со встроенными PlantUML-блоками `@startuml ... @enduml` и описанием.
   - Генерация SVG/PNG изображений диаграмм при наличии рантайма.
4. **Синхронизация**:
   - Коммит и пуш в git.
   - Синхронизация на сервере `ssh home`.

---

## Журнал изменений и решений
- Исходный вариант был сделан в формате Mermaid через `uml-project-diagrammer`.
- По запросу пользователя переключились на специализированный скилл PlantUML (`SpillwaveSolutions/plantuml`).
- Установлен `plantuml.jar` v1.2024.7 в домашнюю директорию `~/plantuml.jar`.
- Вся коллекция диаграмм переработана и сохранена в `docs/puml/`:
  - `01_deployment_and_containers.puml` (+ `.svg`)
  - `02_class_diagram.puml` (+ `.svg`)
  - `03_sequence_topic_updater.puml` (+ `.svg`)
  - `04_sequence_hw_solver.puml` (+ `.svg`)
  - `05_sequence_wopi_attendance.puml` (+ `.svg`)
  - `06_erd_data_models.puml` (+ `.svg`)
- Все 6 диаграмм успешно скомпилированы скриптом конвертации в векторный формат SVG.
- Обновлен центральный документ `docs/UML.md` со встроенными `@startuml` блоками и кликабельными ссылками на SVG и исходники.
- Все требования к стилю (cerulean theme, Unicode icons, round corners, shadow) соблюдены.

