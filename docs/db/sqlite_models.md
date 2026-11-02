# Component Reference: `db/sqlite/models.py`
> **File Path**: [`db/sqlite/models.py`](../../db/sqlite/models.py)
> **Subsystem**: `SQLite Domain Models`

## 1. Purpose
Модели реляционной базы данных SQLite (SQLAlchemy 2.0).


---
## 2. Public API & Symbol Inventory
| Symbol | Nature | Line Range | Return Contract | Summary |
| :--- | :--- | :--- | :--- | :--- |

---

## 3. Comprehensive Function Specifications

## Class Model: `Base`

Базовый класс для всех реляционных моделей проекта.

## Class Model: `IncidentSeverity`

Уровни критичности инцидентов системы.

## Class Model: `Subscriber`

Таблица активных подписчиков утренней рассылки и уведомлений.

## Class Model: `AttendanceSnapshot`

Таблица исторических снимков посещаемости студентов из Яндекс Документов.

## Class Model: `SystemIncident`

Таблица журнала системных сбоев, сетевых аномалий и срабатываний защиты.

## Class Model: `StudentAchievement`

Таблица открытых студентами достижений с фиксацией времени получения.

## Class Model: `StudentCounter`

Таблица счётчиков действий студента (сообщения, задания ДЗ, активные дни).

## Class Model: `AchievementBaseline`

Снимок журнала студента на момент сброса ачивок — журнальные ачивки считаются от него.
