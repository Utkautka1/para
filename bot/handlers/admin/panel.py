"""
Хэндлеры управления панелью администратора (только для ALLOWED_USER_ID).

Предоставляет старосте интерактивный дашборд для управления топиками,
синхронизации кэша расписания и преподавателей, привязки Telegram ID
студентов группы и ручного добавления ссылок дистанционных пар.
"""

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.filters.auth import AuthFilter
from bot.templates.admin.keyboards import get_admin_main_kb
from core.api_client import fetch_day_schedule, fetch_teachers
from core.logger import get_logger
from services.custom_teachers import load_custom_teachers, save_custom_teacher
from services.topic_updater import sync_topic_main_message

log = get_logger("admin_panel")

router = Router()
router.message.filter(AuthFilter())
router.callback_query.filter(AuthFilter())


class AddTeacherState(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_link_info = State()


class BindStudentState(StatesGroup):
    waiting_for_tg_id = State()


async def _ack_admin_callback(callback: CallbackQuery, text: str | None = None) -> None:
    """
    Мгновенно подтверждает callback в админ-панели с обработкой устаревания.

    Игнорирует ошибки устаревания Telegram (query is too old), чтобы бот не падал.
    Логирует неожиданные ошибки ответа на callback.

    Ничего не возвращает.
    """

    try:
        await callback.answer(text, show_alert=False)
    except TelegramBadRequest as e:
        if "query is too old" in str(e).lower():
            log.debug("Callback админки устарел (query is too old)")
        else:
            log.warning(f"Ошибка ответа на callback админки: {e}")


async def _safe_edit_admin_message(
    message: Message | None, text: str, reply_markup: InlineKeyboardMarkup | None = None
) -> None:
    """
    Безопасно обновляет сообщение админки, перехватывая 'not modified'.

    Предотвращает исключения Telegram, если текст и разметка идентичны текущим.
    Логирует прочие ошибки изменения интерфейса.

    Ничего не возвращает.
    """

    if not message:
        return

    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "not modified" in str(e).lower():
            log.debug("Сообщение админки не изменилось ('not modified')")
            return

        log.warning(f"Не удалось обновить сообщение админки: {e}")


def format_admin_panel_text(status_note: str = "") -> str:
    """
    Формирует приветственный HTML-текст главной панели управления администратора.

    Включает системный статус, параметры синхронизации топика и диагностическую сводку.
    Используется как единый шаблон отображения админ-панели.

    Возвращает отформатированную HTML-строку.
    """

    text = (
        "⚙️ <b>ПАНЕЛЬ АДМИНИСТРАТОРА КТМУ (1-КПД-3)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👤 <b>Статус доступа:</b> Вы Главный Администратор\n"
        "📢 <b>Синхронизация топика:</b> За 1 час до 1-й пары + каждые 60 сек\n"
    )
    if status_note:
        text += f"\n<i>{status_note}</i>\n"

    return text


@router.message(Command("admin"))
@router.callback_query(F.data == "admin:menu")
async def cb_admin_menu(event: Message | CallbackQuery) -> None:
    """
    Отображает главную панель управления старосты с инлайн-кнопками.

    Поддерживает вызов через команду /admin и через инлайн-кнопку возврата.
    Редактирует сообщение при callback или отправляет новое при команде.

    Ничего не возвращает.
    """

    log.info("Открыто меню админ-панели")
    text = format_admin_panel_text()
    kb = get_admin_main_kb()

    if isinstance(event, CallbackQuery):
        await _safe_edit_admin_message(event.message, text, kb)
        await _ack_admin_callback(event)
    else:
        await event.answer(text, reply_markup=kb)


@router.callback_query(F.data == "admin:sync")
async def cb_admin_sync(callback: CallbackQuery) -> None:
    """
    Принудительно скачивает расписание КТМУ и таблицу преподавателей.

    Сбрасывает кэш расписания и контактов преподавателей, обновляет топик.
    Выводит уведомление об успешной синхронизации данных в админ-панель.

    Ничего не возвращает.
    """

    await _ack_admin_callback(callback, "⏳ Синхронизация данных...")
    log.info("Запущена принудительная синхронизация данных из админки")

    res_t = await fetch_teachers(force_refresh=True)
    await fetch_day_schedule(force_refresh=True)
    await sync_topic_main_message()

    count = res_t.get("count", 0)
    note = f"✅ Кэш очищен! Распаршено {count} преподавателей docx и топик обновлен."
    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())


async def _get_redis_memory_stat() -> str:
    """
    Безопасно извлекает объем используемой оперативной памяти Redis.

    Запрашивает системную секцию info('memory') из активного соединения Redis.
    При сбое соединения возвращает безопасный маркер 'N/A'.

    Возвращает строку с объемом памяти (например, '1.2M') или 'N/A'.
    """

    try:
        from core.redis_cache import init_redis

        r = await init_redis()
        if r:
            info = await r.info("memory")
            return info.get("used_memory_human", "OK")
    except Exception as e:
        log.debug(f"Не удалось получить статистику памяти Redis: {e}")

    return "N/A"


async def _collect_health_summary() -> str:
    """
    Собирает диагностические метрики всех компонентов и сервисов системы.

    Проверяет память Redis, контакты преподавателей, реестр группы и сессию Яндекса.
    Формирует структурированный сводный блок текста для панели управления.

    Возвращает строку с метриками компонентов.
    """

    from db.subscribers import load_subscribers
    from integrations.yandex_docs import get_effective_yandex_cookie
    from services.attendance_topic_updater import load_attendance_topic_state
    from services.classmates_auth import load_classmates_registry

    subs_cnt, class_cnt = len(load_subscribers()), len(load_classmates_registry())
    res_t = await fetch_teachers(force_refresh=False)
    has_cookie = bool(await get_effective_yandex_cookie())
    redis_mem = await _get_redis_memory_stat()

    cookie_badge = "✅ Активна" if has_cookie else "⚠️ Отсутствует"
    att_id = load_attendance_topic_state()
    att_badge = f"✅ MSG #{att_id}" if att_id else "⚠️ Не создан"

    return (
        f"📊 <b>ДИАГНОСТИКА СИСТЕМЫ:</b>\n"
        f"• <b>Redis (RAM):</b> <code>{redis_mem}</code>\n"
        f"• <b>Преподаватели:</b> <code>{res_t.get('count', 0)}</code> контактов\n"
        f"• <b>Одногруппники:</b> <code>{class_cnt}</code> в реестре\n"
        f"• <b>Подписчики ЛС:</b> <code>{subs_cnt}</code> чел.\n"
        f"• <b>Сессия Яндекс:</b> {cookie_badge}\n"
        f"• <b>Топик посещаемости:</b> {att_badge}"
    )


@router.callback_query(F.data == "admin:status")
async def cb_admin_status(callback: CallbackQuery) -> None:
    """
    Отображает подробный дашборд состояния компонентов и сервисов бота.

    Собирает актуальную системную телеметрию и обновляет сообщение админки.
    Подтверждает callback без всплывающего уведомления.

    Ничего не возвращает.
    """

    note = await _collect_health_summary()
    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())
    await _ack_admin_callback(callback)


@router.callback_query(F.data == "admin:force_topic")
async def cb_admin_force_topic(callback: CallbackQuery) -> None:
    """
    Принудительно публикует или обновляет сообщение расписания в топике.

    Игнорирует временные ограничения и синхронизирует топик немедленно.
    Отображает статус успешности операции в главной панели.

    Ничего не возвращает.
    """

    await _ack_admin_callback(callback, "⏳ Обновляю топик...")
    success = await sync_topic_main_message(ignore_time_restriction=True)
    note = "📢 Топик обновлён!" if success else "⚠️ Не удалось обновить топик. Проверьте логи."

    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())


@router.callback_query(F.data == "admin:recreate_topic")
async def cb_admin_recreate_topic(callback: CallbackQuery) -> None:
    """
    Удаляет старое сообщение топика и создает новое с фиксацией message_id.

    Используется при повреждении или случайном удалении закрепленного сообщения.
    Сохраняет новый идентификатор сообщения в локальное состояние.

    Ничего не возвращает.
    """

    await _ack_admin_callback(callback, "🔁 Пересоздаю сообщение...")
    from services.topic_updater import recreate_topic_message

    success = await recreate_topic_message()
    note = "🔁 Сообщение пересоздано!" if success else "⚠️ Ошибка пересоздания. Проверьте логи."

    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())


@router.callback_query(F.data == "admin:force_exam")
async def cb_admin_force_exam(callback: CallbackQuery) -> None:
    """
    Принудительно обновляет сообщение сессии и экзаменов в топике.

    Загружает актуальные данные экзаменов и редактирует закрепленный пост.
    Отображает результат выполнения в панели управления.

    Ничего не возвращает.
    """

    await _ack_admin_callback(callback, "⏳ Обновляю экзамены...")
    from services.exam_topic_updater import sync_exam_topic_message

    success = await sync_exam_topic_message()
    note = "📑 Экзамены обновлены!" if success else "⚠️ Не удалось обновить экзамены."

    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())


@router.callback_query(F.data == "admin:recreate_exam")
async def cb_admin_recreate_exam(callback: CallbackQuery) -> None:
    """
    Удаляет закрепленное сообщение экзаменов и создает новое в топике.

    Восстанавливает правильный message_id при нарушении синхронизации в Telegram.
    Выводит статус завершения в текст админ-панели.

    Ничего не возвращает.
    """

    await _ack_admin_callback(callback, "🔁 Пересоздаю экзамены...")
    from services.exam_topic_updater import recreate_exam_topic_message

    success = await recreate_exam_topic_message()
    note = "🔁 Сообщение экзаменов пересоздано!" if success else "⚠️ Ошибка пересоздания."

    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())


@router.callback_query(F.data == "admin:force_att_topic")
async def cb_admin_force_att_topic(callback: CallbackQuery) -> None:
    """
    Принудительно обновляет сводный реестр посещаемости в топике Telegram.

    Сбрасывает кэш Яндекс Таблицы и синхронизирует актуальные пропуски.
    Отображает статус выполнения в админке.

    Ничего не возвращает.
    """

    await _ack_admin_callback(callback, "⏳ Обновляю реестр посещаемости...")
    from services.attendance_topic_updater import sync_attendance_topic_message

    success = await sync_attendance_topic_message(force_refresh=True)
    note = "📊 Реестр посещаемости обновлён!" if success else "⚠️ Не удалось обновить реестр."

    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())


@router.callback_query(F.data == "admin:recreate_att_topic")
async def cb_admin_recreate_att_topic(callback: CallbackQuery) -> None:
    """
    Удаляет старое сообщение реестра и создает новое в топике посещаемости.

    Сбрасывает и пересохраняет message_id топика в локальном хранилище.
    Позволяет восстановить публикацию при случайном удалении поста.

    Ничего не возвращает.
    """

    await _ack_admin_callback(callback, "🔁 Пересоздаю сообщение посещаемости...")
    from services.attendance_topic_updater import recreate_attendance_topic_message

    success = await recreate_attendance_topic_message()
    note = "🔁 Реестр посещаемости пересоздан!" if success else "⚠️ Ошибка пересоздания."

    await _safe_edit_admin_message(callback.message, format_admin_panel_text(note), get_admin_main_kb())


def _build_custom_teachers_view(custom: dict) -> tuple[str, list]:
    """
    Формирует текст списка кастомных преподавателей и ряды кнопок управления.

    Строит клавиатуру с кнопками редактирования и удаления для каждой записи.
    Обрабатывает случай пустого словаря сохраненных контактов.

    Возвращает кортеж (текст описания, список рядов инлайн-кнопок).
    """

    if not custom:
        return "👨‍🏫 <b>Ручных записей преподавателей пока нет.</b>", []

    text = "👨‍🏫 <b>Добавленные вручную контакты:</b>\n\n"
    kb_rows = []
    for key, val in custom.items():
        text += f"🔹 <b>{val['full_name']}</b> (код: <code>{key}</code>):\n<code>{val['link_info']}</code>\n\n"
        kb_rows.append([
            InlineKeyboardButton(text=f"✏️ {val['full_name'].split()[0]}", callback_data=f"admin:edit_t:{key}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin:del_t:{key}"),
        ])

    return text, kb_rows


@router.callback_query(F.data.startswith("admin:list_custom"))
async def cb_admin_list_custom(callback: CallbackQuery) -> None:
    """
    Отображает список кастомных преподавателей с кнопками добавления и удаления.

    Загружает актуальный словарь контактов и строит инлайн-меню управления.
    Добавляет навигационные кнопки создания нового контакта и возврата в меню.

    Ничего не возвращает.
    """

    custom = load_custom_teachers()
    text, kb_rows = _build_custom_teachers_view(custom)
    kb_rows.append([InlineKeyboardButton(text="➕ Добавить нового", callback_data="admin:add_t:manual")])
    kb_rows.append([InlineKeyboardButton(text="◀️ В главную панель", callback_data="admin:menu")])

    await _safe_edit_admin_message(callback.message, text, InlineKeyboardMarkup(inline_keyboard=kb_rows))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:del_t:"))
async def cb_admin_delete_teacher(callback: CallbackQuery) -> None:
    """
    Удаляет запись преподавателя из пользовательского реестра и обновляет меню.

    Очищает кэш преподавателей, чтобы изменения мгновенно отразились в расписании.
    Отображает toast-уведомление об успешном удалении.

    Ничего не возвращает.
    """

    from services.custom_teachers import delete_custom_teacher

    last_name = callback.data.split(":")[-1]
    delete_custom_teacher(last_name)
    await fetch_teachers(force_refresh=True)

    await callback.answer("❌ Запись удалена!")
    await cb_admin_list_custom(callback)


@router.callback_query(F.data.startswith("admin:edit_t:"))
async def cb_admin_edit_teacher(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Запускает сценарий FSM для редактирования ссылки встречи преподавателя.

    Загружает текущую информацию о преподавателе и переводит стейт на ввод ссылки.
    Отображает подсказку с текущим ФИО преподавателя.

    Ничего не возвращает.
    """

    last_name = callback.data.split(":")[-1]
    custom = load_custom_teachers()
    t_info = custom.get(last_name, {})
    full_name = t_info.get("full_name", last_name.capitalize())

    await state.set_state(AddTeacherState.waiting_for_link_info)
    await state.update_data(full_name=full_name, suggested_key=last_name)

    prompt = (
        f"✏️ <b>Редактирование ссылок преподавателя</b>\n"
        f"👤 <b>ФИО:</b> {full_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Отправьте НОВУЮ ссылку на Zoom/Телемост или полные реквизиты встречи:"
    )
    await _safe_edit_admin_message(callback.message, prompt)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:add_t:"))
async def cb_admin_start_add_teacher(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Инициирует пошаговый диалог FSM для добавления нового преподавателя.

    Устанавливает начальный стейт ожидания ФИО преподавателя.
    Выводит форму с примером корректного ввода.

    Ничего не возвращает.
    """

    suggested_key = callback.data.split(":")[-1]
    await state.set_state(AddTeacherState.waiting_for_full_name)
    await state.update_data(suggested_key=suggested_key)

    prompt = (
        "👨‍🏫 <b>Ввод данных преподавателя</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Шаг 1/2: Отправьте полные ФИО преподавателя (например, <code>Валуев Константин Владимирович</code>):"
    )
    await _safe_edit_admin_message(callback.message, prompt)
    await callback.answer()


@router.message(AddTeacherState.waiting_for_full_name, F.chat.type == "private")
async def msg_admin_got_teacher_name(message: Message, state: FSMContext) -> None:
    """
    Принимает ФИО преподавателя и переключает FSM на ожидание ссылки подключения.

    Валидирует и сохраняет переданное ФИО в контексте FSM.
    Выводит инструкцию второго шага со сбором Zoom/Телемост ссылки.

    Ничего не возвращает.
    """

    full_name = message.text.strip() if message.text else ""
    await state.update_data(full_name=full_name)
    await state.set_state(AddTeacherState.waiting_for_link_info)

    prompt = (
        f"✅ ФИО: <b>{full_name}</b>\n\n"
        "Шаг 2/2: Отправьте ссылку на Zoom/Телемост или полные реквизиты встречи "
        "(включая Идентификатор и Пароль, если есть):"
    )
    await message.answer(prompt)


@router.message(AddTeacherState.waiting_for_link_info, F.chat.type == "private")
async def msg_admin_got_teacher_link(message: Message, state: FSMContext) -> None:
    """
    Сохраняет преподавателя в пользовательский реестр и сбрасывает стейт FSM.

    Автоматически определяет ключ по фамилии, форсирует обновление кэша.
    Отправляет подтверждение старосте с возвратом в главную панель.

    Ничего не возвращает.
    """

    data = await state.get_data()
    full_name = data.get("full_name", "")
    link_info = message.text.strip() if message.text else ""
    last_name = full_name.split()[0].lower() if full_name else data.get("suggested_key", "custom")

    save_custom_teacher(last_name, full_name, link_info)
    await fetch_teachers(force_refresh=True)
    await state.clear()

    res_text = (
        f"🎉 <b>Преподаватель успешно сохранён!</b>\n"
        f"👤 <b>ФИО:</b> {full_name}\n"
        f"🔗 <b>Контакты:</b> {link_info}\n\n"
        f"<i>Данные применены и будут использоваться во всех дистанционных парах.</i>"
    )
    await message.answer(res_text, reply_markup=get_admin_main_kb())


def _build_unbound_students_kb() -> InlineKeyboardMarkup:
    """
    Формирует клавиатуру со списком студентов группы для привязки Telegram ID.

    Маркирует студентов с уже привязанным ID зеленым значком, остальных — предупреждением.
    Добавляет кнопку возврата в главное меню админки.

    Возвращает объект InlineKeyboardMarkup.
    """

    from services.classmates_auth import load_classmates_registry

    registry = load_classmates_registry()
    kb_rows = []
    for idx, student in enumerate(registry):
        fio = student.get("full_name", f"Студент {idx}")
        tg_id = student.get("tg_id")
        status = "✅" if tg_id else "⚠️"
        btn_text = f"{status} {fio.split()[0]} {fio.split()[1][:1]}."
        kb_rows.append([InlineKeyboardButton(text=btn_text, callback_data=f"admin:bind_user:{idx}")])

    kb_rows.append([InlineKeyboardButton(text="◀️ В главную панель", callback_data="admin:menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb_rows)


@router.callback_query(F.data == "admin:bind_student")
async def cb_admin_list_students_for_binding(callback: CallbackQuery) -> None:
    """
    Отображает интерактивный список студентов группы для привязки Telegram ID.

    Проверяет реестр на наполненность и выдает предупреждение при пустом списке.
    Отрисовывает кнопки с индикаторами привязки каждого студента.

    Ничего не возвращает.
    """

    from services.classmates_auth import load_classmates_registry

    registry = load_classmates_registry()
    if not registry:
        text = "👥 <b>Привязка Telegram ID</b>\n\n⚠️ <i>Реестр студентов пуст.</i>"
        back_kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="◀️ В панель", callback_data="admin:menu")]]
        )
        await _safe_edit_admin_message(callback.message, text, back_kb)
        await callback.answer()
        return

    text = (
        "👥 <b>Привязка Telegram ID студентов</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Выберите студента, чтобы привязать или изменить его цифровой Telegram ID:\n"
        "<i>(⚠️ — ID не привязан, ✅ — ID привязан)</i>"
    )
    await _safe_edit_admin_message(callback.message, text, _build_unbound_students_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("admin:bind_user:"))
async def cb_admin_select_student(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Запрашивает числовой Telegram ID для выбранного из реестра студента.

    Переводит FSM в стейт ожидания ID и сохраняет ФИО студента.
    Защищает от выхода индекса за пределы реестра одногруппников.

    Ничего не возвращает.
    """

    from services.classmates_auth import load_classmates_registry

    idx = int(callback.data.split(":")[-1])
    registry = load_classmates_registry()
    if idx >= len(registry):
        await callback.answer("Студент не найден", show_alert=True)
        return

    fio = registry[idx].get("full_name", "")
    await state.set_state(BindStudentState.waiting_for_tg_id)
    await state.update_data(student_name=fio)

    prompt = f"👤 <b>Привязка ID: {fio}</b>\nОтправьте числовой Telegram ID (например, <code>1834107464</code>):"
    await _safe_edit_admin_message(callback.message, prompt)
    await callback.answer()


@router.message(BindStudentState.waiting_for_tg_id, F.chat.type == "private")
async def msg_admin_got_student_id(message: Message, state: FSMContext) -> None:
    """
    Фиксирует Telegram ID студента в реестре одногруппников и сбрасывает FSM.

    Валидирует числовой формат Telegram ID перед сохранением в постоянную базу.
    При успехе авторизует доступ студента ко всем закрытым сервисам группы.

    Ничего не возвращает.
    """

    raw_id = (message.text or "").strip()
    if not raw_id.isdigit():
        await message.answer("⚠️ Ошибка: Telegram ID должен состоять только из цифр. Повторите ввод:")
        return

    data = await state.get_data()
    fio = data.get("student_name", "")
    from services.classmates_auth import bind_student_tg_id

    updated = bind_student_tg_id(fio, int(raw_id))
    await state.clear()
    if not updated:
        await message.answer(f"❌ Не удалось привязать ID для {fio}.", reply_markup=get_admin_main_kb())
        return

    text = f"🎉 <b>Студент авторизован!</b>\n👤 {fio}\n🆔 <code>{raw_id}</code>\n<i>Доступ открыт.</i>"
    await message.answer(text, reply_markup=get_admin_main_kb())
