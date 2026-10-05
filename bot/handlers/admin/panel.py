"""
Хэндлеры управления панелью администратора (только для ALLOWED_USER_ID).
"""

from typing import Optional
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.filters.auth import AuthFilter
from bot.templates.admin.keyboards import get_admin_main_kb
from core.api_client import fetch_day_schedule, fetch_teachers
from services.topic_updater import sync_topic_main_message

from core.logger import get_logger

log = get_logger("admin_panel")

router = Router()
router.message.filter(AuthFilter())
router.callback_query.filter(AuthFilter())


async def _ack_admin_callback(callback: CallbackQuery, text: Optional[str] = None) -> None:
    """Мгновенно подтверждает callback в админ-панели с обработкой устаревания."""
    try:
        await callback.answer(text, show_alert=False)
    except TelegramBadRequest as e:
        if "query is too old" in str(e).lower():
            log.debug("Callback админки устарел (query is too old)")
        else:
            log.warning(f"Ошибка ответа на callback админки: {e}")


async def _safe_edit_admin_message(
    message: Optional[Message], text: str, reply_markup: Optional[InlineKeyboardMarkup] = None
) -> None:
    """Безопасно обновляет сообщение админки, перехватывая 'not modified'."""
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
    Формирует текст главной панели управления.

    :param status_note: Дополнительное примечание
    :return: HTML текст
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
    Отображает главную панель управления с инлайн-кнопками.

    :param event: Message или CallbackQuery
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
    """Принудительно скачивает расписание КТМУ и таблицу Яндекс Диска."""
    await _ack_admin_callback(callback, "⏳ Синхронизация данных...")
    log.info("Запущена принудительная синхронизация данных из админки")
    res_t = await fetch_teachers(force_refresh=True)
    await fetch_day_schedule(force_refresh=True)
    await sync_topic_main_message()
    count = res_t.get("count", 0)
    note = f"✅ Кэш очищен! Распаршено {count} преподавателей docx и топик обновлен."
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())


async def _get_redis_memory_stat() -> str:
    """Безопасно извлекает объем используемой оперативной памяти Redis."""
    try:
        from services.redis_cache import init_redis
        r = await init_redis()
        if r:
            info = await r.info("memory")
            return info.get("used_memory_human", "OK")
    except Exception:
        pass
    return "N/A"


async def _collect_health_summary() -> str:
    """Собирает диагностические метрики всех компонентов системы."""
    from db.subscribers import load_subscribers
    from services.attendance_topic_updater import load_attendance_topic_state
    from services.classmates_auth import load_classmates_registry
    from services.yandex_docs import get_effective_yandex_cookie
    subs_cnt, class_cnt = len(load_subscribers()), len(load_classmates_registry())
    res_t = await fetch_teachers(force_refresh=False)
    teach_cnt = res_t.get("count", 0)
    has_cookie = bool(await get_effective_yandex_cookie())
    redis_mem = await _get_redis_memory_stat()
    cookie_badge = "✅ Активна" if has_cookie else "⚠️ Отсутствует"
    att_id = load_attendance_topic_state()
    att_badge = f"✅ MSG #{att_id}" if att_id else "⚠️ Не создан"
    return (
        f"📊 <b>ДИАГНОСТИКА СИСТЕМЫ:</b>\n"
        f"• <b>Redis (RAM):</b> <code>{redis_mem}</code>\n"
        f"• <b>Преподаватели:</b> <code>{teach_cnt}</code> контактов\n"
        f"• <b>Одногруппники:</b> <code>{class_cnt}</code> в реестре\n"
        f"• <b>Подписчики ЛС:</b> <code>{subs_cnt}</code> чел.\n"
        f"• <b>Сессия Яндекс:</b> {cookie_badge}\n"
        f"• <b>Топик посещаемости:</b> {att_badge}"
    )


@router.callback_query(F.data == "admin:status")
async def cb_admin_status(callback: CallbackQuery) -> None:
    """Показывает подробный дашборд статуса компонентов системы."""
    note = await _collect_health_summary()
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())
    await _ack_admin_callback(callback)


@router.callback_query(F.data == "admin:force_topic")
async def cb_admin_force_topic(callback: CallbackQuery) -> None:
    """Принудительно публикует или обновляет сообщение в топике."""
    await _ack_admin_callback(callback, "⏳ Обновляю топик...")
    success = await sync_topic_main_message(ignore_time_restriction=True)
    note = "📢 Топик обновлён!" if success else "⚠️ Не удалось обновить топик. Проверьте логи."
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())


@router.callback_query(F.data == "admin:recreate_topic")
async def cb_admin_recreate_topic(callback: CallbackQuery) -> None:
    """Удаляет текущее сообщение топика и создаёт новое с правильным MSG_ID."""
    await _ack_admin_callback(callback, "🔁 Пересоздаю сообщение...")
    from services.topic_updater import recreate_topic_message
    success = await recreate_topic_message()
    note = "🔁 Сообщение пересоздано!" if success else "⚠️ Ошибка пересоздания. Проверьте логи."
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())


@router.callback_query(F.data == "admin:force_exam")
async def cb_admin_force_exam(callback: CallbackQuery) -> None:
    """Принудительно обновляет сообщение экзаменов в топике."""
    await _ack_admin_callback(callback, "⏳ Обновляю экзамены...")
    from services.exam_topic_updater import sync_exam_topic_message
    success = await sync_exam_topic_message()
    note = "📑 Экзамены обновлены!" if success else "⚠️ Не удалось обновить экзамены."
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())


@router.callback_query(F.data == "admin:recreate_exam")
async def cb_admin_recreate_exam(callback: CallbackQuery) -> None:
    """Удаляет текущее сообщение экзаменов и создаёт новое (сброс MSG_ID)."""
    await _ack_admin_callback(callback, "🔁 Пересоздаю экзамены...")
    from services.exam_topic_updater import recreate_exam_topic_message
    success = await recreate_exam_topic_message()
    note = "🔁 Сообщение экзаменов пересоздано!" if success else "⚠️ Ошибка пересоздания."
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())


@router.callback_query(F.data == "admin:force_att_topic")
async def cb_admin_force_att_topic(callback: CallbackQuery) -> None:
    """Принудительно обновляет сводный реестр посещаемости в топике."""
    await _ack_admin_callback(callback, "⏳ Обновляю реестр посещаемости...")
    from services.attendance_topic_updater import sync_attendance_topic_message
    success = await sync_attendance_topic_message(force_refresh=True)
    note = "📊 Реестр посещаемости обновлён!" if success else "⚠️ Не удалось обновить реестр."
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())


@router.callback_query(F.data == "admin:recreate_att_topic")
async def cb_admin_recreate_att_topic(callback: CallbackQuery) -> None:
    """Удаляет старое сообщение реестра и создаёт новое в топике посещаемости."""
    await _ack_admin_callback(callback, "🔁 Пересоздаю сообщение посещаемости...")
    from services.attendance_topic_updater import recreate_attendance_topic_message
    success = await recreate_attendance_topic_message()
    note = "🔁 Реестр посещаемости пересоздан!" if success else "⚠️ Ошибка пересоздания."
    text = format_admin_panel_text(note)
    await _safe_edit_admin_message(callback.message, text, get_admin_main_kb())


from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.custom_teachers import load_custom_teachers, save_custom_teacher


class AddTeacherState(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_link_info = State()


def _build_custom_teachers_view(custom: dict) -> tuple[str, list]:
    """Формирует текст списка кастомных преподавателей и ряды кнопок."""
    if not custom:
        return "👨‍🏫 <b>Ручных записей преподавателей пока нет.</b>", []
    text = "👨‍🏫 <b>Добавленные вручную контакты:</b>\n\n"
    kb_rows = []
    for key, val in custom.items():
        text += f"🔹 <b>{val['full_name']}</b> (код: <code>{key}</code>):\n<code>{val['link_info']}</code>\n\n"
        kb_rows.append([
            InlineKeyboardButton(text=f"✏️ {val['full_name'].split()[0]}", callback_data=f"admin:edit_t:{key}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin:del_t:{key}")
        ])
    return text, kb_rows


@router.callback_query(F.data.startswith("admin:list_custom"))
async def cb_admin_list_custom(callback: CallbackQuery) -> None:
    """
    Выводит список кастомных преподавателей с кнопками ред/удал и навигацией.

    :param callback: CallbackQuery
    """
    custom = load_custom_teachers()
    text, kb_rows = _build_custom_teachers_view(custom)
    kb_rows.append([InlineKeyboardButton(text="➕ Добавить нового", callback_data="admin:add_t:manual")])
    kb_rows.append([InlineKeyboardButton(text="◀️ В главную панель", callback_data="admin:menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    await _safe_edit_admin_message(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:del_t:"))
async def cb_admin_delete_teacher(callback: CallbackQuery) -> None:
    """
    Удаляет преподавателя и обновляет список.

    :param callback: CallbackQuery
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
    Быстрое редактирование преподавателя.

    :param callback: CallbackQuery
    :param state: FSMContext
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
    Запускает FSM диалог ввода ФИО преподавателя.

    :param callback: CallbackQuery
    :param state: FSMContext
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
    Сохраняет ФИО и запрашивает ссылку на Zoom/Телемост.

    :param message: Message
    :param state: FSMContext
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
    Сохраняет преподавателя в custom_teachers.json и очищает FSM.

    :param message: Message
    :param state: FSMContext
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

