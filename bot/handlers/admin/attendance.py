"""
Хэндлеры управления процессом отметки посещаемости.

Обрабатывает команду /attendance и все инлайн-кнопки (att:*)
исключительно для старосты (ALLOWED_USER_ID) и замстаросты (DEPUTY_USER_ID).
"""

import html
from datetime import date, datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.filters.auth import AttendanceAuthFilter
from bot.templates.admin.attendance import (
    format_partner_attendance_report,
    format_partner_cancel_report,
    format_partner_single_report,
    format_single_student_card,
    format_single_update_confirm,
    format_student_card,
    format_summary_text,
    get_days_select_kb,
    get_lesson_mode_kb,
    get_lesson_select_kb,
    get_single_mark_confirmed_kb,
    get_single_student_select_kb,
    get_student_mark_choice_kb,
    get_student_poll_kb,
)
from config import ADMIN_USER_IDS, ALLOWED_USER_ID, DEPUTY_USER_ID, TIMEZONE
from core.api_client import get_api_schedule_for_date
from core.background import spawn
from core.bot import bot
from core.logger import get_logger
from services.attendance_manager import (
    AttendanceSession,
    calculate_summary_stats,
    clear_session,
    commit_session_to_table,
    create_attendance_session,
    fetch_target_students,
    get_active_session,
    mark_all_remaining_present,
    record_student_mark,
    step_back,
)
from services.attendance_stats import apply_session_optimistic_update, get_saved_lesson_marks
from services.attendance_topic_updater import sync_attendance_topic_message

log = get_logger("attendance_handlers")

router = Router()
router.message.filter(AttendanceAuthFilter())
router.callback_query.filter(AttendanceAuthFilter())


async def _async_commit_and_update(message: Message | None, session, stats: dict[str, int]) -> None:
    """
    Выполняет фоновую фиксацию посещаемости в Яндекс Таблицу с обновлением сообщения.

    Не блокирует диалог со старостой во время сетевого запроса к Яндекс Документам.
    Дописывает бейдж успешного сохранения либо предупреждения о резерве в Redis.

    Ничего не возвращает.
    """

    success = await commit_session_to_table(session)
    if not message:
        return

    badge = (
        "\n\n✅ <i>Успешно сохранено в Яндекс Таблицу</i>"
        if success
        else "\n\n⚠️ <i>Не удалось сохранить в Яндекс. Данные сохранены в Redis (/attendance).</i>"
    )
    try:
        await message.edit_text(format_summary_text(session, stats) + badge)
    except Exception as e:
        log.debug("Не удалось обновить статус выгрузки посещаемости: %s", e)


async def _instant_topic_sync(session) -> None:
    """
    Мгновенно обновляет топик посещаемости в Telegram через оптимистичные метки.

    Применяет новые отметки в локальный кэш до завершения тяжелой записи в Яндекс.
    Обеспечивает мгновенный отклик закрепленного сообщения посещаемости в чате.

    Ничего не возвращает.
    """

    try:
        await apply_session_optimistic_update(session)
        await sync_attendance_topic_message(force_refresh=False)
        log.info("⚡️ Мгновенное обновление топика для пары %s выполнено", session.lesson_num)
    except Exception as e:
        log.error("Ошибка мгновенного обновления топика посещаемости: %s", e)


def get_partner_admin_id(current_user_id: int) -> int | None:
    """
    Определяет Telegram ID напарника по модерации (староста <-> замстаросты).

    Используется для взаимного уведомления старост о фиксации посещаемости.
    Возвращает None, если роли настроены на одного и того же пользователя.

    Возвращает Telegram ID второго администратора или None.
    """

    if current_user_id == ALLOWED_USER_ID:
        return DEPUTY_USER_ID if DEPUTY_USER_ID != ALLOWED_USER_ID else None

    if current_user_id == DEPUTY_USER_ID:
        return ALLOWED_USER_ID

    return None


async def notify_partner_about_attendance(session, stats: dict[str, int], user_full_name: str | None = None) -> None:
    """
    Отправляет полный отчет о завершении отметки пары второму администратору в ЛС.

    Включает имя заполнившего старосты, статистику посещения и список пропустивших.
    Защищает от дублирования усилий и держит старостат в едином информационном поле.

    Ничего не возвращает.
    """

    partner_id = get_partner_admin_id(session.initiator_id)
    if not partner_id:
        return

    title = get_initiator_title(session.initiator_id)
    if user_full_name:
        title = f"{title} ({user_full_name})"

    text = format_partner_attendance_report(session, stats, title)
    try:
        await bot.send_message(partner_id, text)
        log.info("Статистика пары %s отправлена партнеру %s", session.lesson_num, partner_id)
    except Exception as e:
        log.warning("Не удалось доставить статистику партнеру %s: %s", partner_id, e)


async def finish_and_notify(cb: CallbackQuery, session) -> None:
    """
    Мгновенно выводит сводку старосте и запускает асинхронные задачи сохранения.

    Формирует итоговый экран и запускает 3 параллельных background таска:
    1) Синхронизацию топика, 2) Запись в Яндекс, 3) Уведомление напарника.

    Ничего не возвращает.
    """

    stats = calculate_summary_stats(session.marks)
    text_saving = (
        format_summary_text(session, stats) + "\n\n⏳ <i>Синхронизация с Яндекс Таблицей и топиком в фоне...</i>"
    )
    if cb.message:
        try:
            await cb.message.edit_text(text_saving)
        except Exception as e:
            log.debug("Не удалось обновить статус сообщения посещаемости: %s", e)

    spawn(_instant_topic_sync(session))
    spawn(_async_commit_and_update(cb.message, session, stats))
    spawn(notify_partner_about_attendance(session, stats, cb.from_user.full_name))
    log.info("Сводка пары %s выдана, запущены оптимистичный апдейт и выгрузка", session.lesson_num)


@router.message(Command("attendance"))
@router.callback_query(F.data == "att:menu")
async def show_attendance_menu(event: Message | CallbackQuery) -> None:
    """
    Отображает интерактивное меню выбора учебного дня для отметки пар.

    Поддерживает вызов как через команду чата, так и через инлайн-кнопку.
    Редактирует текущее сообщение в callback либо шлет новое сообщение.

    Ничего не возвращает.
    """

    text = "📋 <b>Отметка посещаемости</b>\n\nВыберите учебный день для отметки пар:"
    kb = get_days_select_kb()
    if isinstance(event, CallbackQuery):
        if event.message:
            await event.message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("att:day:"))
async def cb_select_day(cb: CallbackQuery) -> None:
    """
    Формирует и отображает кнопки доступных пар на выбранную старостой дату.

    Запрашивает предметы расписания через API-клиент колледжа.
    Показывает кнопки выбора пар с названиями предметов.

    Ничего не возвращает.
    """

    day_str = cb.data.split(":")[2]
    target_date = date.fromisoformat(day_str)
    lessons = await get_api_schedule_for_date(target_date)
    kb = get_lesson_select_kb(lessons, target_date)
    text = f"📋 <b>Дата: {target_date.strftime('%d.%m.%Y')}</b>\nВыберите пару для отметки посещаемости:"
    if cb.message:
        await cb.message.edit_text(text, reply_markup=kb)

    await cb.answer()


def parse_start_callback(data: str):
    """
    Парсит целевую дату и номер пары из строки callback_data.

    Поддерживает как короткий формат 'att:start:N', так и полный 'att:start:DATE:N'.
    Для короткого формата использует сегодняшнюю дату по часовому поясу МСК.

    Возвращает кортеж (date, lesson_num).
    """

    parts = data.split(":")
    if len(parts) == 4:
        return date.fromisoformat(parts[2]), int(parts[3])

    return datetime.now(TIMEZONE).date(), int(parts[2])


def get_initiator_title(initiator_id: int) -> str:
    """
    Возвращает русскоязычное наименование роли старосты по его Telegram ID.

    Сверяет ID с ADMIN_USER_IDS, определяя Старосту или Замстаросты.
    Используется в журналах и уведомлениях напарника.

    Возвращает строку 'Староста' или 'Замстаросты'.
    """

    return "Староста" if initiator_id in ADMIN_USER_IDS else "Замстаросты"


async def check_session_ownership(cb: CallbackQuery, session) -> bool:
    """
    Проверяет, принадлежит ли активная сессия опроса текущему пользователю.

    Предотвращает одновременное вмешательство второго администратора в чужой опрос.
    Показывает информационный toast-alert в случае отклонения действия.

    Возвращает True, если действие разрешено, иначе False.
    """

    if not session:
        await cb.answer("Сессия завершена или не найдена", show_alert=True)
        return False

    if session.initiator_id != cb.from_user.id:
        title = get_initiator_title(session.initiator_id)
        await cb.answer(f"⚠️ Опрос сейчас заполняет {title}. Действие отклонено.", show_alert=True)
        return False

    return True


async def _resolve_lesson_title_for_start(target_date, lesson_num: int) -> str:
    """
    Определяет наименование дисциплины по номеру пары из расписания на дату.

    Ищет соответствие номеру пары в API расписания колледжа.
    В случае отсутствия или отмены возвращает резервную строку вида 'Пара N'.

    Возвращает строку с названием предмета или дефолтным обозначением.
    """

    lessons = await get_api_schedule_for_date(target_date)
    matched = [les for les in lessons if getattr(les, "number", getattr(les, "period", -1) + 1) == lesson_num]

    return matched[0].subject if matched else f"Пара {lesson_num}"


async def _ensure_session_available(cb: CallbackQuery) -> bool:
    """
    Проверяет доступность запуска нового опроса посещаемости.

    Предотвращает одновременный опрос группы двумя администраторами.
    Выводит alert пользователю, если опрос уже запущен напарником.

    Возвращает True, если опрос можно начинать, иначе False.
    """

    active = await get_active_session()
    if active and active.initiator_id != cb.from_user.id:
        title = get_initiator_title(active.initiator_id)
        await cb.answer(f"⚠️ Опрос уже проводит {title}! Дождитесь завершения.", show_alert=True)
        return False

    return True


async def _init_session_safe(cb: CallbackQuery, target_date, lesson_num: int, title: str):
    """
    Безопасно создает сессию посещаемости с обработкой ошибок API/таблицы.

    Изолирует сетевые исключения облачной таблицы от обработчика Telegram.
    При сбое выводит понятную ошибку пользователю в чат.

    Возвращает объект AttendanceSession или None при ошибке.
    """

    try:
        return await create_attendance_session(target_date, lesson_num, title, cb.from_user.id)
    except (PermissionError, ValueError) as e:
        # Доменные отказы (сессия занята, нет колонки) — их текст понятен старосте
        log.warning("⚠️ Сессия посещаемости не создана: %s", e)
        reason = html.escape(str(e))
    except Exception as e:
        # Сетевые и прочие сбои: детали только в лог, в HTML-сообщение их не пускаем
        log.error("Сбой инициализации сессии: %s", e)
        reason = "таблица недоступна, попробуйте позже"
    if cb.message:
        await cb.message.edit_text(f"❌ Не удалось открыть таблицу: {reason}")
    return None


async def notify_partner_about_single_update(
    session: AttendanceSession, fio: str, mark: str, user_id: int, user_full_name: str | None = None
) -> None:
    """
    Отправляет уведомление второму администратору о точечном изменении отметки.

    Формирует текст отчета с указанием ФИО студента и нового статуса.

    Ничего не возвращает.
    """
    partner_id = get_partner_admin_id(user_id)
    if not partner_id:
        return
    title = get_initiator_title(user_id)
    if user_full_name:
        title = f"{title} ({user_full_name})"
    text = format_partner_single_report(fio, session.target_date, session.lesson_num, session.lesson_title, mark, title)
    try:
        await bot.send_message(partner_id, text)
        log.info("Уведомление о смене отметки %s отправлено партнеру %s", fio, partner_id)
    except Exception as e:
        log.warning("Не удалось доставить уведомление партнеру %s: %s", partner_id, e)


async def _commit_single_attendance_background(
    session: AttendanceSession, message: Message | None, fio: str, mark: str
) -> None:
    """
    Выполняет фоновую фиксацию одиночной отметки в Яндекс Таблицу.

    Обновляет сообщение со статусом синхронизации по окончании попыток.

    Ничего не возвращает.
    """
    success = await commit_session_to_table(session)
    if not message:
        return
    note = (
        "\n\n✅ <i>Синхронизировано с Яндекс Таблицей!</i>"
        if success
        else "\n\n⚠️ <i>Не удалось сохранить в Яндекс. Ошибка синхронизации.</i>"
    )
    try:
        curr_text = message.text or message.html_text or ""
        await message.edit_text(curr_text + note, reply_markup=message.reply_markup)
    except Exception as e:
        log.debug("Не удалось обновить статус выгрузки одиночной отметки: %s", e)


@router.callback_query(F.data.startswith("att:mode:"))
async def cb_lesson_mode(cb: CallbackQuery) -> None:
    """
    Отображает выбор режима отметки пары: опрос всей группы или один студент.

    Показывает кнопки выбора сценария и возврат к выбору даты.

    Ничего не возвращает.
    """
    target_date, lesson_num = parse_start_callback(cb.data)
    title = await _resolve_lesson_title_for_start(target_date, lesson_num)
    d_str = target_date.isoformat()
    text = (
        f"📋 <b>Дата: {target_date.strftime('%d.%m.%Y')}</b>\n"
        f"📖 <b>Пара {lesson_num}: {html.escape(title)}</b>\n\n"
        "Выберите режим отметки:"
    )
    if cb.message:
        await cb.message.edit_text(text, reply_markup=get_lesson_mode_kb(d_str, lesson_num))
    await cb.answer()


@router.callback_query(F.data.startswith("att:sngl:"))
async def cb_single_student_menu(cb: CallbackQuery) -> None:
    """
    Отображает список студентов по два в ряд для точечной отметки.

    Загружает актуальные отметки из Redis и отображает их на кнопках.

    Ничего не возвращает.
    """
    target_date, lesson_num = parse_start_callback(cb.data)
    d_str = target_date.isoformat()
    students = await fetch_target_students(target_date)
    saved_marks = await get_saved_lesson_marks(d_str, lesson_num)
    text = (
        f"📋 <b>Дата: {target_date.strftime('%d.%m.%Y')} | Пара {lesson_num}</b>\n\n"
        "Выберите студента для изменения отметки:"
    )
    kb = get_single_student_select_kb(students, saved_marks, d_str, lesson_num)
    if cb.message:
        await cb.message.edit_text(text, reply_markup=kb)
    await cb.answer()


@router.callback_query(F.data.startswith("att:p:"))
async def cb_pick_student(cb: CallbackQuery) -> None:
    """
    Отображает карточку студента с кнопками установки новой отметки.

    Выводит текущую отметку студента за выбранную пару.

    Ничего не возвращает.
    """
    parts = cb.data.split(":")
    d_str, lesson_num, row_idx = parts[2], int(parts[3]), int(parts[4])
    target_date = date.fromisoformat(d_str)
    students = await fetch_target_students(target_date)
    fio = next((name for r, name in students if r == row_idx), f"Строка {row_idx}")
    title = await _resolve_lesson_title_for_start(target_date, lesson_num)
    saved_marks = await get_saved_lesson_marks(d_str, lesson_num)
    mark = saved_marks.get(str(row_idx))
    text = format_single_student_card(fio, d_str, lesson_num, title, mark)
    if cb.message:
        await cb.message.edit_text(text, reply_markup=get_student_mark_choice_kb(d_str, lesson_num, row_idx))
    await cb.answer()


def _build_single_session(
    d_str: str, lesson_num: int, title: str, students: list, row_idx: int, mark: str, user_id: int
) -> AttendanceSession:
    """
    Создает объект AttendanceSession с отметкой для одного студента.

    Используется для передачи в общие механизмы оптимистичного апдейта и выгрузки.

    Возвращает сформированный объект AttendanceSession.
    """
    return AttendanceSession(
        target_date=d_str,
        lesson_num=lesson_num,
        lesson_title=title,
        students=students,
        marks={str(row_idx): mark},
        initiator_id=user_id,
    )


@router.callback_query(F.data.startswith("att:set:"))
async def cb_set_single_mark(cb: CallbackQuery) -> None:
    """
    Устанавливает новую отметку выбранному студенту и запускает сохранение.

    Применяет оптимистичное обновление топика и фоновую запись в таблицу.

    Ничего не возвращает.
    """
    parts = cb.data.split(":")
    d_str, lesson_num, row_idx, raw_mark = parts[2], int(parts[3]), int(parts[4]), parts[5]
    mark = "" if raw_mark == "_" else raw_mark
    target_date = date.fromisoformat(d_str)
    students = await fetch_target_students(target_date)
    fio = next((name for r, name in students if r == row_idx), f"Строка {row_idx}")
    title = await _resolve_lesson_title_for_start(target_date, lesson_num)
    session = _build_single_session(d_str, lesson_num, title, students, row_idx, mark, cb.from_user.id)
    await apply_session_optimistic_update(session)
    spawn(sync_attendance_topic_message(force_refresh=False))
    spawn(_commit_single_attendance_background(session, cb.message, fio, mark))
    spawn(notify_partner_about_single_update(session, fio, mark, cb.from_user.id, cb.from_user.full_name))
    if cb.message:
        await cb.message.edit_text(
            format_single_update_confirm(fio, d_str, lesson_num, title, mark),
            reply_markup=get_single_mark_confirmed_kb(d_str, lesson_num),
        )
    await cb.answer("Отметка зафиксирована!")


@router.callback_query(F.data.startswith("att:start:"))
async def cb_start_attendance(cb: CallbackQuery) -> None:
    """
    Инициализирует интерактивную сессию опроса посещаемости и открывает карточку.

    Защищает от параллельного запуска опроса двумя администраторами.
    Загружает список студентов из облачной таблицы и выводит первого.

    Ничего не возвращает.
    """

    if not await _ensure_session_available(cb):
        return

    await cb.answer()
    target_date, lesson_num = parse_start_callback(cb.data)
    title = await _resolve_lesson_title_for_start(target_date, lesson_num)

    if cb.message:
        await cb.message.edit_text("⏳ <i>Загрузка списка группы из таблицы...</i>")

    session = await _init_session_safe(cb, target_date, lesson_num, title)
    if session and cb.message:
        await cb.message.edit_text(format_student_card(session), reply_markup=get_student_poll_kb(can_back=False))


@router.callback_query(F.data.startswith("att:mark:"))
async def cb_mark_student(cb: CallbackQuery) -> None:
    """
    Фиксирует статус студента и переходит к следующему шагу опроса.

    Проверяет права сессии, обновляет статус и выводит следующего студента.
    По завершении списка запускает финализацию и рассылку сводки.

    Ничего не возвращает.
    """

    session = await get_active_session()
    if not await check_session_ownership(cb, session):
        return

    session = await record_student_mark(cb.data.split(":")[2])
    if not session:
        await cb.answer("Сессия завершена или не найдена", show_alert=True)
        return

    await cb.answer()
    if session.current_idx < len(session.students) and cb.message:
        await cb.message.edit_text(format_student_card(session), reply_markup=get_student_poll_kb(can_back=True))
        return

    await finish_and_notify(cb, session)


@router.callback_query(F.data == "att:back")
async def cb_step_back(cb: CallbackQuery) -> None:
    """
    Возвращает старосту к предыдущему студенту для исправления отметки.

    Откатывает индекс сессии назад и повторно отображает карточку студента.
    Управляет доступностью кнопки возврата в клавиатуре.

    Ничего не возвращает.
    """

    session = await get_active_session()
    if not await check_session_ownership(cb, session):
        return

    session = await step_back()
    if not session:
        await cb.answer("Сессия не найдена", show_alert=True)
        return

    can_back = session.current_idx > 0
    if cb.message:
        await cb.message.edit_text(format_student_card(session), reply_markup=get_student_poll_kb(can_back=can_back))

    await cb.answer()


@router.callback_query(F.data == "att:all_p")
async def cb_all_present(cb: CallbackQuery) -> None:
    """
    Проставляет статус 'П' (Присутствует) всем оставшимся студентам группы.

    Ускоряет опрос, когда все оставшиеся студенты находятся в аудитории.
    Автоматически завершает сессию и рассылает отчеты.

    Ничего не возвращает.
    """

    session = await get_active_session()
    if not await check_session_ownership(cb, session):
        return

    session = await mark_all_remaining_present()
    if not session:
        await cb.answer("Сессия не найдена", show_alert=True)
        return

    await cb.answer()
    await finish_and_notify(cb, session)


async def notify_partner_about_cancellation(
    lesson_num: int | str, user_id: int, user_full_name: str | None = None
) -> None:
    """
    Оповещает второго администратора об отмене проведения пары.

    Формирует текст отчета и отправляет личное сообщение в Telegram напарнику.
    Логирует факт отправки или перехватывает сетевые ошибки отправки.

    Ничего не возвращает.
    """

    partner_id = get_partner_admin_id(user_id)
    if not partner_id:
        return

    title = get_initiator_title(user_id)
    if user_full_name:
        title = f"{title} ({user_full_name})"

    try:
        await bot.send_message(partner_id, format_partner_cancel_report(lesson_num, title))
        log.info("Уведомление об отмене пары %s отправлено партнеру %s", lesson_num, partner_id)
    except Exception as e:
        log.warning("Не удалось доставить уведомление об отмене партнеру %s: %s", partner_id, e)


@router.callback_query(F.data.startswith("att:cancel:"))
async def cb_cancel_lesson(cb: CallbackQuery) -> None:
    """
    Отменяет опрос для указанной пары и уведомляет напарника старосты.

    Сбрасывает сессию в Redis и асинхронно уведомляет второго старосту.
    Редактирует сообщение в чате, подтверждая отмену пары.

    Ничего не возвращает.
    """

    lesson_num = cb.data.split(":")[2]
    await clear_session()
    if cb.message:
        await cb.message.edit_text(f"❌ Отметка посещаемости за пару {lesson_num} отменена.")

    spawn(notify_partner_about_cancellation(lesson_num, cb.from_user.id, cb.from_user.full_name))
    await cb.answer()


@router.callback_query(F.data == "att:abort")
async def cb_abort_survey(cb: CallbackQuery) -> None:
    """
    Прерывает активный опрос посещаемости по запросу его инициатора.

    Защищает от прерывания чужого опроса вторым администратором.
    Очищает данные незавершенной сессии в Redis.

    Ничего не возвращает.
    """

    session = await get_active_session()
    if session and session.initiator_id != cb.from_user.id:
        title = get_initiator_title(session.initiator_id)
        await cb.answer(f"⚠️ Опрос проводит {title}. Отменить может только автор.", show_alert=True)
        return

    await clear_session()
    if cb.message:
        await cb.message.edit_text("❌ Опрос посещаемости прерван.")

    await cb.answer()


@router.callback_query(F.data == "att:close")
async def cb_close_menu(cb: CallbackQuery) -> None:
    """
    Удаляет сообщение с интерактивным меню посещаемости из чата.

    Используется для закрытия интерфейса выбора пар без сохранения данных.
    Предотвращает захламление чата устаревшими инлайн-сообщениями.

    Ничего не возвращает.
    """

    if cb.message:
        await cb.message.delete()

    await cb.answer()
