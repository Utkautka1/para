"""
Модуль синхронизации и авто-обновления расписания в Telegram-топике группы.

Сохраняет состояние _TOPIC_MAIN_MSG_ID в data/topic_state.json для устойчивости к перезапускам.
Синхронизирует расписание каждые 60 секунд и отправляет временные 10-минутные уведомления.
"""

import asyncio
from datetime import date, datetime, timedelta
from typing import Any

from aiogram.exceptions import TelegramBadRequest

from bot.templates.user.keyboards import get_topic_inline_kb
from bot.templates.user.messages import format_day_schedule, format_reminder_text
from config import TIMEZONE, TOPIC_CHAT_ID, TOPIC_STATE_FILE, TOPIC_THREAD_ID
from core.api_client import get_api_schedule_for_date
from core.bot import bot
from core.logger import get_logger
from services.models import Lesson
from services.notifier import parse_lesson_end_time, parse_lesson_start_time

log = get_logger("topic_updater")
STATE_FILE = TOPIC_STATE_FILE

_TOPIC_MAIN_MSG_ID: int | None = None
_SENT_REMINDERS: set = set()


from utils.storage import sync_atomic_save_json, sync_load_json


def load_topic_state() -> int | None:
    """
    Загружает сохраненный ID главного сообщения расписания из локального JSON.

    Обеспечивает сохранение привязки к закрепленному посту в топике между
    рестартами контейнера или процесса бота.

    Возвращает числовой message_id или None при отсутствии файла состояния.
    """
    data = sync_load_json(STATE_FILE, default={})
    return data.get("main_msg_id") if isinstance(data, dict) else None


def save_topic_state(msg_id: int | None) -> None:
    """
    Атомарно сохраняет ID главного сообщения в файл состояния и Redis.

    Обеспечивает двухстороннюю персистентность (диск + in-memory хранилище)
    для мгновенной синхронизации состояния между сервисами.

    Ничего не возвращает.
    """
    import asyncio

    sync_atomic_save_json(STATE_FILE, {"main_msg_id": msg_id})
    if msg_id:
        from core.redis_cache import set_topic_state_redis

        asyncio.create_task(set_topic_state_redis(msg_id))


async def cleanup_expired_messages() -> None:
    """
    Удаляет временные сервисные уведомления из топика с истекшим сроком жизни.

    Опрашивает Redis-очередь просроченных сообщений и вызывает bot.delete_message,
    предотвращая захламление ленты чата устаревшими напоминаниями.

    Ничего не возвращает.
    """
    from core.redis_cache import get_expired_messages_for_cleanup

    expired = await get_expired_messages_for_cleanup()
    for chat_id, msg_id in expired:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
            log.info("Временное уведомление MSG_ID=%s гарантированно удалено.", msg_id)
        except TelegramBadRequest as e:
            if "not found" in str(e).lower():
                log.debug("Временное сообщение MSG_ID=%s уже было удалено: %s", msg_id, e)
            else:
                log.warning("Не удалось удалить временное сообщение MSG_ID=%s: %s", msg_id, e)
        except Exception as e:
            log.error("Ошибка удаления временного сообщения %s: %s", msg_id, e)


async def send_temp_topic_reminder(lesson: Lesson) -> None:
    """
    Отправляет всплывающее уведомление за 10 минут до начала пары с кнопками.

    Регистрирует отправленное сообщение в Redis со сроком жизни 15 минут (900 сек),
    после чего сообщение автоматически удаляется воркером очистки.

    Ничего не возвращает.
    """
    from core.redis_cache import register_message_for_cleanup

    try:
        text = format_reminder_text(lesson)
        kb = get_topic_inline_kb([lesson])
        msg = await bot.send_message(
            chat_id=TOPIC_CHAT_ID, message_thread_id=TOPIC_THREAD_ID, text=text, reply_markup=kb
        )
        log.info("Временное уведомление о паре %s отправлено. MSG_ID=%s", lesson.period + 1, msg.message_id)
        await register_message_for_cleanup(TOPIC_CHAT_ID, msg.message_id, delay_sec=900)
    except TelegramBadRequest as e:
        log.warning("⚠️ Ошибка Telegram при отправке временного напоминания в топик: %s", e)
    except Exception as e:
        log.error("Ошибка отправки временного уведомления: %s", e)


async def check_and_trigger_reminder(lesson: Lesson, now_dt: datetime, today: date) -> None:
    """
    Проверяет приближение времени начала пары и запускает отправку напоминания.

    Использует комбинированный фильтр (память процесса + распределенный Redis),
    предотвращая отправку дубликатов напоминания при частых циклах проверки.

    Ничего не возвращает.
    """
    rem_key = f"{today.isoformat()}_{lesson.period}_{lesson.subgroup}_{lesson.subject}"
    if rem_key in _SENT_REMINDERS:
        return
    from core.redis_cache import is_reminder_sent, mark_reminder_sent

    if await is_reminder_sent(rem_key):
        _SENT_REMINDERS.add(rem_key)
        return
    start_t = parse_lesson_start_time(lesson.time_str)
    if not start_t:
        return
    pair_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE)
    diff_sec = (pair_dt - now_dt).total_seconds()
    if 0 < diff_sec <= 600:
        _SENT_REMINDERS.add(rem_key)
        await mark_reminder_sent(rem_key)
        asyncio.create_task(send_temp_topic_reminder(lesson))


def get_next_working_day(target_date: date) -> date:
    """
    Определяет дату следующего учебного дня с автоматическим пропуском воскресенья.

    Сдвигает субботу на понедельник, обеспечивая публикацию расписания сразу
    на рабочий день недели.

    Возвращает объект datetime.date следующего рабочего дня.
    """
    next_d = target_date + timedelta(days=1)
    if next_d.weekday() == 6:
        return next_d + timedelta(days=1)
    return next_d


def _should_switch_to_next_day(today_lessons: list[Lesson], today: date, now_dt: datetime) -> bool:
    """
    Проверяет, завершились ли все учебные пары сегодняшнего дня по времени звонков.

    Сравнивает текущее время с моментом окончания последней пары в расписании.

    Возвращает True, если все пары завершены и пора переключаться на завтра.
    """
    if not today_lessons:
        return False
    last_lesson = max(today_lessons, key=lambda x: x.period)
    end_t = parse_lesson_end_time(last_lesson.time_str)
    if end_t:
        last_end_dt = datetime.combine(today, end_t, tzinfo=TIMEZONE)
        return now_dt >= last_end_dt
    return False


async def resolve_target_date(now_dt: datetime, ignore_restriction: bool) -> date | None:
    """
    Рассчитывает целевую дату отображения расписания для закрепленного сообщения.

    Учитывает воскресный фильтр (публикация расписания на понедельник с 18:00)
    и переключает отображение на следующий рабочий день после завершения пар.

    Возвращает целевую дату или None при запрете публикации в воскресенье днем.
    """
    today = now_dt.date()
    if today.weekday() == 6:
        if now_dt.hour < 18 and not ignore_restriction:
            return None
        return today + timedelta(days=1)
    today_lessons = await get_api_schedule_for_date(today)
    if _should_switch_to_next_day(today_lessons, today, now_dt):
        return get_next_working_day(today)
    return today


def is_too_early_to_publish(lessons: list[Lesson], now_dt: datetime, today: date, ignore_restriction: bool) -> bool:
    """
    Проверяет, не наступило ли слишком раннее утреннее время до первой пары.

    Предотвращает преждевременную смену закрепленного сообщения до интервала
    за 1 час до первой пары при первичном создании поста.

    Возвращает True, если публикацию следует отложить, иначе False.
    """
    if today.weekday() == 6 or ignore_restriction or _TOPIC_MAIN_MSG_ID is not None:
        return False
    first_lesson = min(lessons, key=lambda x: x.period)
    start_t = parse_lesson_start_time(first_lesson.time_str)
    if start_t:
        first_pair_dt = datetime.combine(today, start_t, tzinfo=TIMEZONE)
        if now_dt < first_pair_dt - timedelta(minutes=60):
            return True
    return False


async def _edit_topic_message(text: str, kb: Any) -> bool:
    """
    Редактирует текст и клавиатуру активного сообщения в топике Telegram.

    Возвращает True в случае успешного редактирования.
    """
    await bot.edit_message_text(
        chat_id=TOPIC_CHAT_ID,
        message_id=_TOPIC_MAIN_MSG_ID,
        text=text,
        reply_markup=kb,
    )
    log.info("✅ Сообщение топика ОТРЕДАКТИРОВАНО: MSG_ID=%s, chat=%s", _TOPIC_MAIN_MSG_ID, TOPIC_CHAT_ID)
    return True


async def update_topic_message_payload(text: str, kb: Any, _retry: bool = False) -> bool:
    """
    Атомарно отправляет новое или редактирует закрепленное сообщение в топике.

    При повреждении сообщения или ошибке Bad Request пересоздает сообщение с нуля.

    Возвращает True в случае успешной публикации/редактирования, иначе False.
    """
    try:
        if _TOPIC_MAIN_MSG_ID is None:
            return await _send_new_topic_message(text, kb)

        return await _edit_topic_message(text, kb)
    except TelegramBadRequest as e:
        return await _handle_edit_failure(e, text, kb, _retry)
    except Exception as e:
        log.error("❌ Ошибка обновления топика: %s: %s", type(e).__name__, e)
        return False


async def _send_new_topic_message(text: str, kb: Any) -> bool:
    """
    Создает новое сообщение расписания в топике и закрепляет его без звука.

    Сохраняет присвоенный message_id в локальный стейт-файл для переживания перезагрузок.

    Возвращает True при успешной отправке.
    """
    global _TOPIC_MAIN_MSG_ID

    msg = await bot.send_message(
        chat_id=TOPIC_CHAT_ID,
        message_thread_id=TOPIC_THREAD_ID,
        text=text,
        reply_markup=kb,
    )
    _TOPIC_MAIN_MSG_ID = msg.message_id
    save_topic_state(_TOPIC_MAIN_MSG_ID)
    await _pin_silently(TOPIC_CHAT_ID, _TOPIC_MAIN_MSG_ID)

    log.info("Главное сообщение создано и закреплено: MSG_ID=%s", _TOPIC_MAIN_MSG_ID)
    return True


async def _pin_silently(chat_id: int, message_id: int) -> None:
    """
    Закрепляет сообщение в супергруппе без отправки системного пуш-уведомления.

    Использует disable_notification=True, чтобы не спамить студентам в чате.

    Ничего не возвращает.
    """
    try:
        await bot.pin_chat_message(
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=True,
        )
    except Exception as e:
        log.warning("Не удалось закрепить MSG_ID=%s: %s", message_id, e)


async def _try_delete_old_topic_msg(old_id: int | None) -> None:
    """
    Пытается удалить старое призрачное сообщение из топика Telegram.

    Игнорирует ошибки отсутствия доступа или если сообщение уже удалено вручную.

    Ничего не возвращает.
    """
    if not old_id:
        return

    try:
        await bot.delete_message(chat_id=TOPIC_CHAT_ID, message_id=old_id)
        log.info("Старое сообщение MSG_ID=%s удалено", old_id)
    except Exception as e:
        log.warning("Не удалось удалить MSG_ID=%s: %s", old_id, e)


async def recreate_topic_message() -> bool:
    """
    Сбрасывает сохраненный ID сообщения и принудительно пересоздает пост с нуля.

    Используется администратором для устранения рассинхронизации или удаления призраков.

    Возвращает True в случае успешного пересоздания поста.
    """
    global _TOPIC_MAIN_MSG_ID

    old_id = _TOPIC_MAIN_MSG_ID or load_topic_state()
    await _try_delete_old_topic_msg(old_id)

    _TOPIC_MAIN_MSG_ID = None
    save_topic_state(None)
    log.info("State сброшен — следующий sync создаст новое сообщение")

    return await sync_topic_main_message(ignore_time_restriction=True)


async def _recreate_after_edit_failure(text: str, kb: Any) -> bool:
    """
    Сбрасывает ID закрепленного сообщения и пытается отправить новое.

    Возвращает True в случае успешной повторной отправки.
    """
    global _TOPIC_MAIN_MSG_ID

    _TOPIC_MAIN_MSG_ID = None
    save_topic_state(None)

    return await update_topic_message_payload(text, kb, _retry=True)


async def _handle_edit_failure(
    e: TelegramBadRequest,
    text: str,
    kb: Any,
    is_retry: bool,
) -> bool:
    """
    Обрабатывает исключения редактирования сообщения Telegram API.

    Ошибку 'not modified' считает штатной, а при других сбоях инициирует пересоздание.

    Возвращает True при успешном восстановлении или неизменности, иначе False.
    """
    if "not modified" in str(e).lower():
        log.debug("sync_topic: 'not modified' (MSG_ID=%s)", _TOPIC_MAIN_MSG_ID)
        return True

    if is_retry:
        log.error("❌ Повторная ошибка создания сообщения топика: %s", e)
        return False

    log.warning("⚠️ Ошибка редактирования MSG_ID=%s (%s), пересоздаём...", _TOPIC_MAIN_MSG_ID, e)
    return await _recreate_after_edit_failure(text, kb)


def should_skip_topic_update(
    lessons: list[Lesson],
    now_dt: datetime,
    target_date: date,
    ignore_time_restriction: bool,
) -> bool:
    """
    Определяет необходимость отложить публикацию расписания до утреннего окна.

    Предотвращает раннюю смену закрепленного поста глухой ночью до 1 часа до первой пары.

    Возвращает True, если публикацию необходимо пропустить, иначе False.
    """
    if lessons and is_too_early_to_publish(lessons, now_dt, target_date, ignore_time_restriction):
        log.info("sync_topic: too_early_to_publish, пропуск")
        return True

    return False


async def process_today_reminders(lessons: list[Lesson], now_dt: datetime, target_date: date) -> None:
    """
    Запускает проверку и отправку персональных напоминаний о парах текущего дня.

    Опрашивает зарегистрированные пары и триггерит таймеры за REMINDER_OFFSET_MINUTES.

    Ничего не возвращает.
    """
    if lessons and now_dt.date() == target_date:
        for lesson in lessons:
            await check_and_trigger_reminder(lesson, now_dt, now_dt.date())


async def _prepare_target_schedule(
    ignore_restriction: bool,
) -> tuple[date | None, list[Lesson] | None]:
    """
    Вычисляет целевую дату и запрашивает список уроков для обновления топика.

    Возвращает кортеж (target_date, lessons) или (None, None) при пропуске.
    """
    now_dt = datetime.now(TIMEZONE)
    target_date = await resolve_target_date(now_dt, ignore_restriction)

    if not target_date:
        log.info("sync_topic: target_date=None, пропуск")
        return None, None

    lessons = await get_api_schedule_for_date(target_date)
    if should_skip_topic_update(lessons, now_dt, target_date, ignore_restriction):
        return None, None

    return target_date, lessons


def _ensure_topic_main_msg_id() -> None:
    """
    Загружает сохраненный ID сообщения из файла состояния при первом вызове.

    Ничего не возвращает.
    """
    global _TOPIC_MAIN_MSG_ID

    if _TOPIC_MAIN_MSG_ID is None:
        _TOPIC_MAIN_MSG_ID = load_topic_state()


async def sync_topic_main_message(ignore_time_restriction: bool = False) -> bool:
    """
    Атомарно синхронизирует главное закрепленное сообщение расписания в топике.

    Вычисляет целевую дату, получает расписание из API, форматирует текст
    и обновляет инлайн-кнопки преподавателей.

    Возвращает True в случае успешной синхронизации, иначе False.
    """
    _ensure_topic_main_msg_id()

    target_date, lessons = await _prepare_target_schedule(ignore_time_restriction)
    if not target_date or lessons is None:
        return False

    now_dt = datetime.now(TIMEZONE)
    await process_today_reminders(lessons, now_dt, target_date)
    await cleanup_expired_messages()

    text = format_day_schedule(target_date, lessons)
    kb = get_topic_inline_kb(lessons) if lessons else None

    return await update_topic_message_payload(text, kb)


_API_FAIL_START_TIME: datetime | None = None
_API_ALERT_SENT: bool = False


async def notify_admin_about_api_down() -> None:
    """
    Отправляет экстренное оповещение старосте в ЛС при падении внешних API > 30 минут.

    Защищает от молчаливых падений upstream-сервисов КТМУ и Яндекс Документов.

    Ничего не возвращает.
    """
    global _API_ALERT_SENT

    if _API_ALERT_SENT:
        return

    try:
        from config import ALLOWED_USER_ID

        msg = "⚠️ <b>ВНИМАНИЕ:</b> Внешний сервис расписания КТМУ или Яндекс Диск недоступен более 30 минут!"
        await bot.send_message(chat_id=ALLOWED_USER_ID, text=msg)
        _API_ALERT_SENT = True
        log.warning("Отправлено экстренное уведомление администратору о сбое API > 30 мин")
    except Exception as e:
        log.error("Не удалось отправить алерт администратору: %s", e)


async def _track_api_failure(now: datetime) -> None:
    """
    Отслеживает длительность сбоя внешних API и отправляет алерт при превышении порога.

    Ничего не возвращает.
    """
    global _API_FAIL_START_TIME

    if _API_FAIL_START_TIME is None:
        _API_FAIL_START_TIME = now
    elif (now - _API_FAIL_START_TIME).total_seconds() >= 1800:
        await notify_admin_about_api_down()


def _reset_api_failure_tracker() -> None:
    """
    Сбрасывает таймер и флаг аварийного оповещения при успешном ответе сервисов.

    Ничего не возвращает.
    """
    global _API_FAIL_START_TIME, _API_ALERT_SENT

    if _API_FAIL_START_TIME is not None:
        _API_FAIL_START_TIME = None
        _API_ALERT_SENT = False
        log.info("Соединение с внешними сервисами восстановлено.")


async def topic_sync_loop() -> None:
    """
    Фоновый непрерывный рабочий цикл обновления расписания в топике группы.

    Выполняет итерацию синхронизации каждые 60 секунд с перехватом любых сбоев.

    Никогда не завершается штатно при нормальной работе сервиса.
    """
    log.info("Запущен фоновый сервис авто-обновления расписания в топике Telegram (60 сек)")

    while True:
        try:
            await sync_topic_main_message()
            _reset_api_failure_tracker()
        except Exception as e:
            log.error("Ошибка в цикле topic_sync_loop: %s", e)
            await _track_api_failure(datetime.now(TIMEZONE))

        await asyncio.sleep(60)
