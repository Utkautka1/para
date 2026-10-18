"""
Хэндлеры команд и Inline-кнопок пользователя.

Обрабатывает команды и инлайн-переходы sched:today, sched:tomorrow,
sched:week, sched:refresh с редактированием существующего сообщения.
"""

import json
from datetime import date, datetime, timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.filters.auth import ClassmateAuthFilter
from bot.templates.user.keyboards import (
    get_notice_settings_kb,
    get_schedule_inline_kb,
    get_tester_cabinet_kb,
)
from bot.templates.user.messages import (
    format_day_schedule,
    format_notice_settings_text,
    format_week_schedule,
)
from config import ALLOWED_ATTENDANCE_USER_IDS, ALLOWED_USER_ID, TIMEZONE
from core.api_client import (
    fetch_teachers,
    get_api_schedule_for_date,
    get_api_week_schedule,
)
from core.logger import get_logger
from core.redis_cache import cache_flush, cache_get, cache_set
from db.subscribers import is_subscribed, toggle_subscriber
from services.classmates_auth import is_authorized_user, process_user_auth
from services.models import Lesson
from services.testers_manager import generate_or_get_tester_key, is_tester_allowed

log = get_logger("user_schedule")

router = Router()
router.callback_query.filter(ClassmateAuthFilter())


async def get_day_schedule_cached(target_date: date) -> tuple[str, list[Lesson]]:
    """
    Возвращает отформатированный текст расписания и список пар с кэшированием в Redis.

    Кэширует сериализованный payload на 180 секунд для ускорения отклика инлайн-кнопок.
    При промахе кэша запрашивает расписание из API КТМУ и форматирует карточку.

    Возвращает кортеж (HTML-текст расписания, список объектов Lesson).
    """

    cache_key = f"sched:day_pack:{target_date.isoformat()}"
    cached = await cache_get(cache_key)
    if cached:
        try:
            data = json.loads(cached)
            lessons = [Lesson(**item) for item in data.get("lessons", [])]
            return data["text"], lessons
        except Exception as e:
            log.warning(f"Ошибка десериализации кэша дня ({cache_key}): {e}")

    lessons = await get_api_schedule_for_date(target_date)
    text = format_day_schedule(target_date, lessons)
    payload = json.dumps({"text": text, "lessons": [l.model_dump() for l in lessons]})
    await cache_set(cache_key, payload, ttl=180)

    return text, lessons


async def _ack_callback(callback: CallbackQuery, text: str | None = None) -> None:
    """
    Мгновенно подтверждает callback-запрос от инлайн-кнопок Telegram.

    Игнорирует ошибки устаревания callback ('query is too old'), предотвращая сбои.
    Логирует прочие ошибки связи с Telegram Bot API.

    Ничего не возвращает.
    """

    try:
        await callback.answer(text)
    except TelegramBadRequest as e:
        if "query is too old" in str(e).lower():
            log.debug("Callback устарел при ответе (query is too old)")
        else:
            log.warning(f"Ошибка подтверждения callback: {e}")


async def edit_or_answer(
    callback: CallbackQuery, text: str, lessons: list[Lesson] | None = None, week_offset: int = 0
) -> None:
    """
    Безопасно обновляет содержимое текущего сообщения расписания в чате.

    Учитывает персональные права пользователя (администратор, тестер, подписчик).
    Игнорирует TelegramBadRequest ('not modified'), если контент идентичен.

    Ничего не возвращает.
    """

    uid = callback.from_user.id if callback.from_user else 0
    kb = get_schedule_inline_kb(
        lessons,
        week_offset=week_offset,
        is_admin=(uid == ALLOWED_USER_ID),
        is_subscribed=is_subscribed(uid),
        is_attendance_admin=bool(uid in ALLOWED_ATTENDANCE_USER_IDS),
        is_tester=await is_tester_allowed(uid),
    )

    try:
        if callback.message:
            await callback.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest as e:
        log.debug(f"Обновление сообщения пропущено: {e}")


async def _greet_new_student(message: Message, student: dict) -> None:
    """
    Отправляет персональное приветственное сообщение новому студенту группы.

    Информирует об успешной авторизации и подсказывает способ включения рассылки.
    Использует официальное имя из реестра группы 1-КПД-3.

    Ничего не возвращает.
    """

    name = student.get("full_name", "Студент")
    text = (
        f"🎉 <b>Добро пожаловать, {name}!</b>\n"
        "Ты успешно авторизован(а) в боте группы 1-КПД-3.\n\n"
        "🔕 <i>Напоминания о парах в ЛС по умолчанию выключены. "
        "Включить их можно кнопкой под расписанием или через /notice.</i>"
    )

    await message.answer(text)


async def _show_access_denied(message: Message, uid: int) -> None:
    """
    Информирует неавторизованного пользователя об отказе в доступе к боту.

    Выводит персональный цифровой Telegram ID для передачи старосте.
    Защищает учебные материалы и сервисы группы от посторонних.

    Ничего не возвращает.
    """

    text = (
        "⛔ <b>Доступ ограничен.</b>\n"
        "Этот бот работает исключительно для студентов группы 1-КПД-3.\n\n"
        f"Ваш Telegram ID: <code>{uid}</code>\n"
        "<i>Если вы студент 1-КПД-3 — передайте ваш ID старосте для активации.</i>"
    )

    await message.answer(text)


async def _show_tester_cabinet(message: Message, uid: int) -> None:
    """
    Отправляет экран личного кабинета авторизованного тестировщика API.

    Генерирует или извлекает персональный API-ключ для авторизации в Swagger UI.
    Предоставляет инлайн-ссылки на интерактивную документацию API.

    Ничего не возвращает.
    """

    key = await generate_or_get_tester_key(uid)
    text = (
        "🧪 <b>Кабинет тестировщика para-api</b>\n\n"
        "Вы успешно авторизованы как тестировщик API!\n\n"
        f"🔑 Ваш персональный <b>API-ключ</b>:\n<code>{key}</code>\n\n"
        "💡 <i>Вставьте ключ в Swagger UI (Authorize -> ApiKeyAuth).</i>"
    )

    await message.answer(text, reply_markup=get_tester_cabinet_kb())


async def _send_today_schedule(message: Message, uid: int, is_tester: bool) -> None:
    """
    Отправляет пользователю карточку расписания на сегодня с клавиатурой.

    Запрашивает кэшированные данные и собирает инлайн-меню навигации.
    Учитывает статус подписки и административные привилегии.

    Ничего не возвращает.
    """

    now = datetime.now(TIMEZONE).date()
    text, lessons = await get_day_schedule_cached(now)
    kb = get_schedule_inline_kb(
        lessons,
        is_admin=(uid == ALLOWED_USER_ID),
        is_subscribed=is_subscribed(uid),
        is_attendance_admin=bool(uid in ALLOWED_ATTENDANCE_USER_IDS),
        is_tester=is_tester,
    )

    await message.answer(text, reply_markup=kb)


@router.message(CommandStart())
@router.message(Command("today"))
async def cmd_start(message: Message) -> None:
    """
    Авторизует пользователя, проверяет права тестера и отправляет меню расписания.

    Обрабатывает первичное знакомство, отправляет карточку на сегодня с кнопками.
    Тестерам без студенческого доступа открывает экран кабинета тестера.

    Ничего не возвращает.
    """

    is_auth, is_just_reg, student = process_user_auth(message.from_user)
    uid = message.from_user.id if message.from_user else 0
    is_tester = await is_tester_allowed(uid)

    if not is_auth and not is_tester:
        await _show_access_denied(message, uid)
        return

    if not is_auth and is_tester:
        await _show_tester_cabinet(message, uid)
        return

    if is_just_reg and student:
        await _greet_new_student(message, student)

    await _send_today_schedule(message, uid, is_tester)


@router.message(Command("swagger"))
@router.message(Command("api_key"))
async def cmd_my_api_key(message: Message) -> None:
    """
    Показывает персональный API-ключ и кнопки запуска Swagger UI.

    Проверяет наличие прав тестировщика в реестре разрешенных тестеров.
    Выводит ошибку доступа для неавторизованных пользователей.

    Ничего не возвращает.
    """

    uid = message.from_user.id if message.from_user else 0
    if not await is_tester_allowed(uid):
        await message.answer("⛔ Вы не являетесь авторизованным тестером.")
        return

    await _show_tester_cabinet(message, uid)


@router.callback_query(F.data == "tester:my_key")
async def cb_show_tester_key(callback: CallbackQuery) -> None:
    """
    Отправляет всплывающее уведомление с персональным ключом тестера.

    Позволяет быстро скопировать ключ из alert-окна мобильного клиента Telegram.
    Генерирует новый ключ при его первичном запросе пользователем.

    Ничего не возвращает.
    """

    uid = callback.from_user.id if callback.from_user else 0
    key = await generate_or_get_tester_key(uid)

    await callback.answer(f"Ваш ключ: {key}", show_alert=True)


@router.callback_query(F.data == "sched:toggle_notify")
async def cb_toggle_notify(callback: CallbackQuery) -> None:
    """
    Переключает статус подписки на 10-минутные напоминания о парах в ЛС.

    Инвертирует флаг подписки в базе данных и обновляет инлайн-клавиатуру.
    Выводит всплывающее подтверждение о включении/выключении рассылки.

    Ничего не возвращает.
    """

    uid = callback.from_user.id if callback.from_user else 0
    new_sub = toggle_subscriber(uid)
    ans_text = "🔔 Напоминания за 10 мин включены!" if new_sub else "🔕 Напоминания отключены."
    await _ack_callback(callback, ans_text)

    now = datetime.now(TIMEZONE).date()
    _, lessons = await get_day_schedule_cached(now)
    kb = get_schedule_inline_kb(
        lessons,
        is_admin=(uid == ALLOWED_USER_ID),
        is_subscribed=new_sub,
        is_attendance_admin=bool(uid in ALLOWED_ATTENDANCE_USER_IDS),
        is_tester=await is_tester_allowed(uid),
    )

    try:
        if callback.message:
            await callback.message.edit_reply_markup(reply_markup=kb)
    except TelegramBadRequest as e:
        log.debug(f"Клавиатура расписания не изменилась: {e}")


@router.message(Command("notice"))
async def cmd_notice(message: Message) -> None:
    """
    Отображает экран настроек персональных уведомлений о парах /notice.

    Проверяет принадлежность пользователя к группе 1-КПД-3.
    Показывает текущее состояние подписки и кнопку переключения.

    Ничего не возвращает.
    """

    if not is_authorized_user(message.from_user):
        await message.answer("⛔ <b>Доступ ограничен.</b>\nБот работает исключительно для студентов 1-КПД-3.")
        return

    uid = message.from_user.id if message.from_user else 0
    is_sub = is_subscribed(uid)
    text = format_notice_settings_text(is_sub)

    await message.answer(text, reply_markup=get_notice_settings_kb(is_sub))


@router.callback_query(F.data == "notice:toggle")
async def cb_notice_toggle(callback: CallbackQuery) -> None:
    """
    Переключает статус подписки в меню /notice с обновлением экрана.

    Инвертирует значение в хранилище подписчиков и перерисовывает текст карточки.
    Подтверждает действие всплывающим toast-сообщением.

    Ничего не возвращает.
    """

    uid = callback.from_user.id if callback.from_user else 0
    new_sub = toggle_subscriber(uid)
    ans = "🔔 Уведомления включены!" if new_sub else "🔕 Уведомления отключены."
    await _ack_callback(callback, ans)

    text = format_notice_settings_text(new_sub)
    try:
        if callback.message:
            await callback.message.edit_text(text, reply_markup=get_notice_settings_kb(new_sub))
    except TelegramBadRequest as e:
        log.debug(f"Экран /notice не изменился: {e}")


@router.callback_query(F.data == "sched:today")
async def cb_today(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на сегодня с Redis-кэшированием.

    Загружает актуальное расписание на текущую дату и перерисовывает сообщение.
    Позволяет быстро вернуться к сегодняшнему дню из других вкладок.

    Ничего не возвращает.
    """

    log.info("Нажата инлайн-кнопка: Сегодня")
    await _ack_callback(callback)
    now = datetime.now(TIMEZONE).date()
    text, lessons = await get_day_schedule_cached(now)

    await edit_or_answer(callback, text, lessons)


@router.callback_query(F.data == "sched:tomorrow")
async def cb_tomorrow(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на завтра с Redis-кэшированием.

    Рассчитывает дату завтрашнего дня и загружает расписание из кэша.
    Обновляет инлайн-клавиатуру и карточку пар.

    Ничего не возвращает.
    """

    log.info("Нажата инлайн-кнопка: Завтра")
    await _ack_callback(callback)
    tomorrow = datetime.now(TIMEZONE).date() + timedelta(days=1)
    text, lessons = await get_day_schedule_cached(tomorrow)

    await edit_or_answer(callback, text, lessons)


@router.callback_query(F.data == "sched:week")
async def cb_week(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на текущую неделю с Redis-кэшированием.

    Вычисляет дату понедельника текущей недели и кэширует сводку на 600 секунд.
    Отображает все учебные дни недели в одном компактном посте.

    Ничего не возвращает.
    """

    log.info("Нажата инлайн-кнопка: Эта неделя")
    await _ack_callback(callback)
    today = datetime.now(TIMEZONE).date()
    monday = today - timedelta(days=today.weekday())
    cache_key = f"sched:week:{monday.isoformat()}"
    cached_text = await cache_get(cache_key)

    if cached_text:
        await edit_or_answer(callback, cached_text, week_offset=0)
        return

    days_data = await get_api_week_schedule(monday)
    text = format_week_schedule(days_data)
    await cache_set(cache_key, text, ttl=600)
    await edit_or_answer(callback, text, week_offset=0)


@router.callback_query(F.data == "sched:week_next")
async def cb_week_next(callback: CallbackQuery) -> None:
    """
    Заменяет сообщение на расписание на следующую неделю с Redis-кэшированием.

    Рассчитывает дату понедельника следующей недели и загружает сетку занятий.
    Сохраняет отформатированный текст в кэш на 10 минут.

    Ничего не возвращает.
    """

    log.info("Нажата инлайн-кнопка: Следующая неделя")
    await _ack_callback(callback)
    today = datetime.now(TIMEZONE).date()
    next_monday = today - timedelta(days=today.weekday()) + timedelta(weeks=1)
    cache_key = f"sched:week_next:{next_monday.isoformat()}"
    cached_text = await cache_get(cache_key)

    if cached_text:
        await edit_or_answer(callback, cached_text, week_offset=1)
        return

    days_data = await get_api_week_schedule(next_monday)
    text = format_week_schedule(days_data)
    await cache_set(cache_key, text, ttl=600)
    await edit_or_answer(callback, text, week_offset=1)


async def _refresh_and_format_schedule(now: date) -> tuple[str, list[Lesson], int]:
    """
    Сбрасывает UI-кэш представлений и загружает свежее расписание из API.

    Очищает кэши дней и недель в Redis, принудительно запрашивая API колледжа.
    В случае сбоя сети откатывается на безопасное локальное кэшированное значение.

    Возвращает кортеж (текст расписания, список уроков, количество преподавателей).
    """

    await cache_flush("sched:day_pack*")
    await cache_flush("sched:week*")
    teachers_res = await fetch_teachers(force_refresh=False)
    count = teachers_res.get("count", 0)

    try:
        lessons = await get_api_schedule_for_date(now, force_refresh=True)
    except Exception as e:
        log.warning(f"Сбой принудительного обновления ({e}), возврат из кэша...")
        lessons = await get_api_schedule_for_date(now, force_refresh=False)

    text = format_day_schedule(now, lessons)
    payload = json.dumps({"text": text, "lessons": [l.model_dump() for l in lessons]})
    await cache_set(f"sched:day_pack:{now.isoformat()}", payload, ttl=180)

    return text, lessons, count


@router.callback_query(F.data == "sched:refresh")
async def cb_refresh(callback: CallbackQuery) -> None:
    """
    Принудительно скачивает расписание, очищает Redis-кэш и обновляет экран.

    Используется для ручного сброса кэша при оперативных изменениях в колледже.
    Выводит уведомление со статусом проверки расписания и преподавателей.

    Ничего не возвращает.
    """

    log.info("Нажата инлайн-кнопка: Обновить расписание (Сброс Redis)")
    await _ack_callback(callback, "Синхронизация с API КТМУ...")
    now = datetime.now(TIMEZONE).date()
    text, lessons, count = await _refresh_and_format_schedule(now)
    text += f"\n\n<i>✅ Расписание КТМУ и контакты ({count}) сверены, Redis обновлен!</i>"

    await edit_or_answer(callback, text, lessons)


def format_help_text(is_admin: bool) -> str:
    """
    Формирует справочное сообщение со списком команд бота.

    Включает общедоступные команды расписания, уведомлений и посещаемости.
    Для администратора добавляет привилегированные команды управления.

    Возвращает отформатированную HTML-строку справки.
    """

    base = (
        "🏛 <b>Помощник группы 1-КПД-3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Доступные команды:\n"
        "• /today — Расписание на сегодня\n"
        "• /notice — Уведомления за 10 мин до пар\n"
        "• /my_attendance — Журнал посещаемости\n"
        "• /help — Справка по функциям бота\n"
    )
    if is_admin:
        base += "• /admin — Панель управления старосты\n• /attendance — Отметка посещаемости\n"

    base += "\n<i>Для навигации по расписанию используйте кнопки под сообщением.</i>"
    return base


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """
    Выводит список доступных команд для авторизованного пользователя.

    Проверяет принадлежность отправителя к группе 1-КПД-3.
    Формирует список команд с учетом администраторских полномочий.

    Ничего не возвращает.
    """

    if not is_authorized_user(message.from_user):
        return

    uid = message.from_user.id if message.from_user else 0
    text = format_help_text(is_admin=(uid == ALLOWED_USER_ID))

    await message.answer(text)


@router.message(F.chat.type == "private")
async def handle_user_text_message(message: Message) -> None:
    """
    Отвечает на произвольный текст авторизованного пользователя расписанием.

    Ориентирует пользователя в интерфейсе при отправке неожиданных текстовых сообщений.
    Прикрепляет кнопки навигации по расписанию и переключения уведомлений.

    Ничего не возвращает.
    """

    if not is_authorized_user(message.from_user):
        return

    uid = message.from_user.id if message.from_user else 0
    text = format_help_text(is_admin=(uid == ALLOWED_USER_ID))
    now = datetime.now(TIMEZONE).date()
    _, lessons = await get_day_schedule_cached(now)
    kb = get_schedule_inline_kb(
        lessons,
        is_admin=(uid == ALLOWED_USER_ID),
        is_subscribed=is_subscribed(uid),
        is_attendance_admin=bool(uid in ALLOWED_ATTENDANCE_USER_IDS),
        is_tester=await is_tester_allowed(uid),
    )

    await message.answer(text, reply_markup=kb)
