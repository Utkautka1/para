"""
Модуль аккуратных Inline-клавиатур навигации.

Создает компактные кнопки управления и ссылки для подключения к парам.
Ссылки группируются максимум по 2 в ряд для аккуратного отображения в топике.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import MINIAPP_URL, SWAGGER_URL
from services.models import Lesson


def format_lesson_button_text(lesson: Lesson) -> str:
    """
    Формирует лаконичный текст кнопки подключения к дистанционной паре.

    Указывает порядковый номер пары и подгруппу (если применимо).
    Используется в инлайн-кнопках со ссылками на видеоконференции.

    Возвращает строку вида '🔗 1-я пара (П/Г 2)'.
    """

    sg = f" (П/Г {lesson.subgroup})" if lesson.subgroup > 0 else ""

    return f"🔗 {lesson.period + 1}-я пара{sg}"


def chunk_link_buttons(lessons: list[Lesson]) -> list[list[InlineKeyboardButton]]:
    """
    Разбивает кнопки ссылок на дистанционные занятия по 2 штуки в ряд.

    Фильтрует только пары с признаком is_remote и валидным HTTP URL.
    Защищает интерфейс от перегрузки широкими одноколоночными рядами.

    Возвращает двумерный список InlineKeyboardButton.
    """

    btns = []
    for l in lessons:
        if l.is_remote and l.remote_link:
            url = next((w for w in l.remote_link.split() if w.startswith("http")), None)
            if url:
                btns.append(InlineKeyboardButton(text=format_lesson_button_text(l), url=url, style="success"))

    return [btns[i : i + 2] for i in range(0, len(btns), 2)]


def _build_admin_nav_rows(is_admin: bool, is_attendance_admin: bool) -> list[list[InlineKeyboardButton]]:
    """
    Формирует дополнительные служебные кнопки старосты и администратора.

    Добавляет быстрый переход в опрос посещаемости и общую панель управления.
    Отображается только у пользователей с подтвержденными правами.

    Возвращает список рядов кнопок для добавления в меню.
    """

    rows = []
    if is_attendance_admin or is_admin:
        rows.append([InlineKeyboardButton(text="📝 Отметить посещаемость", callback_data="att:menu", style="success")])

    if is_admin:
        rows.append(
            [InlineKeyboardButton(text="⚙️ Панель управления (Админ)", callback_data="admin:menu", style="danger")]
        )

    return rows


def _build_calendar_rows(week_offset: int, is_subscribed: bool) -> list[list[InlineKeyboardButton]]:
    """Формирует базовые ряды кнопок календаря (сегодня, завтра, смена недели, пуши)."""
    w_text = "⏭ Неделя (След.)" if week_offset == 0 else "⏮ Неделя (Тек.)"
    w_data = "sched:week_next" if week_offset == 0 else "sched:week"
    n_text = "🔔 Напоминания: Вкл" if is_subscribed else "🔕 Напоминания: Выкл"
    return [
        [
            InlineKeyboardButton(text="📅 Сегодня", callback_data="sched:today", style="success"),
            InlineKeyboardButton(text="📆 Завтра", callback_data="sched:tomorrow", style="success"),
        ],
        [
            InlineKeyboardButton(text=w_text, callback_data=w_data, style="primary"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="sched:refresh", style="primary"),
        ],
        [
            InlineKeyboardButton(
                text=n_text, callback_data="sched:toggle_notify", style="success" if is_subscribed else "danger"
            )
        ],
    ]


def _build_nav_rows(
    week_offset: int,
    is_admin: bool = False,
    is_subscribed: bool = True,
    is_attendance_admin: bool = False,
    is_tester: bool = False,
) -> list[list[InlineKeyboardButton]]:
    """Формирует основные кнопки навигации по календарю и переключатели настроек."""
    rows = _build_calendar_rows(week_offset, is_subscribed)
    rows.append([InlineKeyboardButton(text="🎮 Рейтинг и Квесты (Mini App)", web_app=WebAppInfo(url=MINIAPP_URL))])
    if is_tester:
        rows.append([InlineKeyboardButton(text="🧪 Веб-портал API (Swagger UI)", web_app=WebAppInfo(url=MINIAPP_URL))])
    rows.extend(_build_admin_nav_rows(is_admin, is_attendance_admin))
    return rows


def get_schedule_inline_kb(
    lessons: list[Lesson] | None = None,
    week_offset: int = 0,
    is_admin: bool = False,
    is_subscribed: bool = True,
    is_attendance_admin: bool = False,
    is_tester: bool = False,
) -> InlineKeyboardMarkup:
    """Генерирует полную навигационную клавиатуру для экрана расписания в ЛС."""
    rows = list(chunk_link_buttons(lessons)) if lessons else []
    rows.extend(_build_nav_rows(week_offset, is_admin, is_subscribed, is_attendance_admin, is_tester))
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_tester_cabinet_kb(tester_key: str | None = None) -> InlineKeyboardMarkup:
    """
    Формирует инлайн-клавиатуру персонального кабинета тестера API.

    Предоставляет ссылки на веб-портал в формате Telegram Web App и в браузере.
    Включает кнопку получения личного API-ключа.

    Возвращает объект InlineKeyboardMarkup.
    """
    swagger_url = f"{SWAGGER_URL}?key={tester_key}" if tester_key and SWAGGER_URL else SWAGGER_URL

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Запустить веб-портал (Mini App)", web_app=WebAppInfo(url=MINIAPP_URL))],
            [InlineKeyboardButton(text="🌐 Открыть веб-портал в браузере", url=swagger_url)],
            [InlineKeyboardButton(text="🔑 Показать мой API-ключ", callback_data="tester:my_key", style="primary")],
        ]
    )


def get_topic_inline_kb(lessons: list[Lesson] | None = None) -> InlineKeyboardMarkup | None:
    """
    Генерирует лаконичную клавиатуру со ссылками на пары для топика группы.

    Содержит только прямые кнопки видеоконференций без элементов навигации ЛС.
    Возвращает None, если на сегодня нет дистанционных занятий со ссылками.

    Возвращает InlineKeyboardMarkup или None при отсутствии кнопок.
    """

    if not lessons:
        return None

    rows = chunk_link_buttons(lessons)

    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


def get_notice_settings_kb(is_subscribed: bool) -> InlineKeyboardMarkup:
    """
    Генерирует интерактивную клавиатуру управления уведомлениями для /notice.

    Содержит кнопку-переключатель статуса подписки и возврат к расписанию.
    Цвет кнопки изменяется в зависимости от текущего состояния (зеленый/красный).

    Возвращает объект InlineKeyboardMarkup.
    """

    toggle_text = "🔕 Отключить уведомления" if is_subscribed else "🔔 Включить уведомления"
    toggle_style = "danger" if is_subscribed else "success"
    rows = [
        [InlineKeyboardButton(text=toggle_text, callback_data="notice:toggle", style=toggle_style)],
        [InlineKeyboardButton(text="📅 К расписанию", callback_data="sched:today", style="primary")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=rows)
