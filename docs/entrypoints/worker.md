# Module Specification: `worker.py`
> **Path**: [`worker.py`](file:///home/u/Рабочий стол/para/worker.py)  
> **Subsystem**: `Background Daemon`  
> **Architecture Role**: Enterprise Core Service / Domain Logic Handler

## 1. Architectural Overview
Фоновый сервис синхронизации расписания, экзаменов и оповещений. Запускает: 1. Синхронизацию главного расписания КТМУ (topic_sync_loop, раз в 60 сек) 2. Синхронизацию расписания экзаменов (exam_topic_sync_loop, раз в 10 мин) 3. Мониторинг и публикацию поздравлений с ДР (birthday_sync_loop, в 07:00) 4. APScheduler для утренних дайджестов (06:00) и напоминаний за 10 мин до пар 5. Фоновый Keep-Alive сессии Яндекс Документов (раз в 6 часов)

## 2. Function & Method Inventory
| Symbol | Type | Line Range | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| [`schedule_today_reminders`](#schedule_today_reminders) | Function | L35–L43 | `None` | Планирует напоминания на остаток сегодняшнего дня при старте |
| [`shutdown_worker`](#shutdown_worker) | Function | L46–L54 | `None` | Освобождает сетевые ресурсы и останавливает шедулер при выкл |
| [`_start_worker_loops`](#_start_worker_loops) | Function | L57–L65 | `None` | Запускает все фоновые циклы синхронизации сервиса. |
| [`main`](#main) | Function | L68–L83 | `None` | Точка входа фонового сервиса-синхронизатора. |

---

## 3. Exhaustive Function Specifications

### `schedule_today_reminders`
- **Signature**: `async def schedule_today_reminders() -> None`
- **Source Reference**: [worker.py#L35-L43](file:///home/u/Рабочий стол/para/worker.py#L35-L43)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Планирует напоминания на остаток сегодняшнего дня при старте воркера.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `now_dt = datetime.now(TIMEZONE)`
2. `today = now_dt.date()`
3. `log.info(f"Проверка сегодняшних пар на момент запуска воркера: {now_dt.strftime('%H:%`
4. `lessons = await get_api_schedule_for_date(today)`
5. `for lesson in lessons:`

---

### `shutdown_worker`
- **Signature**: `async def shutdown_worker() -> None`
- **Source Reference**: [worker.py#L46-L54](file:///home/u/Рабочий стол/para/worker.py#L46-L54)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Освобождает сетевые ресурсы и останавливает шедулер при выключении.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("Остановка воркера: освобождение сетевых ресурсов...")`
2. `if scheduler.running:`
3. `await close_redis()`
4. `await close_api_client()`
5. `await bot.session.close()`
6. `log.info("Воркер para-worker успешно остановлен.")`

---

### `_start_worker_loops`
- **Signature**: `async def _start_worker_loops() -> None`
- **Source Reference**: [worker.py#L57-L65](file:///home/u/Рабочий стол/para/worker.py#L57-L65)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Запускает все фоновые циклы синхронизации сервиса.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `await asyncio.gather(`

---

### `main`
- **Signature**: `async def main() -> None`
- **Source Reference**: [worker.py#L68-L83](file:///home/u/Рабочий стол/para/worker.py#L68-L83)
- **Async**: `Yes`
- **Return Type**: `None`

#### Purpose & Architectural Intent
Точка входа фонового сервиса-синхронизатора.

#### Parameters Contract
*None (takes no arguments)*

#### Step-by-Step Logic Execution
1. `log.info("=" * 60)`
2. `log.info("ЗАПУСК Фонового Воркера Расписания (para-worker)")`
3. `log.info("=" * 60)`
4. `await init_redis()`
5. `setup_scheduler()`
6. `await schedule_today_reminders()`

---
