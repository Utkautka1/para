"""
Хэндлеры управления панелью администратора (только для ALLOWED_USER_ID).
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.filters.auth import AuthFilter
from services.docx_parser import get_teacher_links
from services.schedule_parser import fetch_schedule_data
from services.topic_updater import sync_topic_main_message
from bot.templates.admin.keyboards import get_admin_main_kb

router = Router()
router.message.filter(AuthFilter())
router.callback_query.filter(AuthFilter())


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
    text = format_admin_panel_text()
    kb = get_admin_main_kb()

    if isinstance(event, CallbackQuery):
        if event.message:
            await event.message.edit_text(text, reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb)


@router.callback_query(F.data == "admin:sync")
async def cb_admin_sync(callback: CallbackQuery) -> None:
    """
    Принудительно скачивает расписание КТМУ и таблицу Яндекс Диска.

    :param callback: CallbackQuery
    """
    await callback.answer("⏳ Синхронизация данных...", show_alert=False)
    links = await get_teacher_links(force_refresh=True)
    await fetch_schedule_data(force_refresh=True)
    await sync_topic_main_message()
    note = f"✅ Кэш очищен! Распаршено {len(links)} преподавателей docx и топик обновлен."
    text = format_admin_panel_text(note)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_main_kb())


@router.callback_query(F.data == "admin:status")
async def cb_admin_status(callback: CallbackQuery) -> None:
    """
    Показывает подробный статус сервисов и парсера.

    :param callback: CallbackQuery
    """
    links = await get_teacher_links(force_refresh=False)
    note = f"📊 В памяти загружено: {len(links)} контактов преподавателей."
    text = format_admin_panel_text(note)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_main_kb())
    await callback.answer()


@router.callback_query(F.data == "admin:force_topic")
async def cb_admin_force_topic(callback: CallbackQuery) -> None:
    """
    Принудительно публикует или обновляет сообщение в топике без утренних задержек.

    :param callback: CallbackQuery
    """
    await sync_topic_main_message(ignore_time_restriction=True)
    note = "📢 Сообщение в топике группы принудительно отправлено/обновлено!"
    text = format_admin_panel_text(note)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_main_kb())
    await callback.answer("Топик обновлен!")


from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.custom_teachers import load_custom_teachers, save_custom_teacher


class AddTeacherState(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_link_info = State()


@router.callback_query(F.data.startswith("admin:list_custom"))
async def cb_admin_list_custom(callback: CallbackQuery) -> None:
    """
    Выводит список кастомных преподавателей с кнопками ред/удал и навигацией.

    :param callback: CallbackQuery
    """
    custom = load_custom_teachers()
    if not custom:
        text = "👨‍🏫 <b>Ручных записей преподавателей пока нет.</b>"
        kb_rows = []
    else:
        text = "👨‍🏫 <b>Добавленные вручную контакты:</b>\n\n"
        kb_rows = []
        for key, val in custom.items():
            text += f"🔹 <b>{val['full_name']}</b> (код: <code>{key}</code>):\n<code>{val['link_info']}</code>\n\n"
            kb_rows.append([
                InlineKeyboardButton(text=f"✏️ {val['full_name'].split()[0]}", callback_data=f"admin:edit_t:{key}"),
                InlineKeyboardButton(text=f"🗑️ Удалить", callback_data=f"admin:del_t:{key}")
            ])

    kb_rows.append([InlineKeyboardButton(text="➕ Добавить нового", callback_data="admin:add_t:manual")])
    kb_rows.append([InlineKeyboardButton(text="◀️ В главную панель", callback_data="admin:menu")])

    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=kb)
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
    await get_teacher_links(force_refresh=True)
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
    if callback.message:
        await callback.message.edit_text(prompt)
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
    if callback.message:
        await callback.message.edit_text(prompt)
    await callback.answer()


@router.message(AddTeacherState.waiting_for_full_name)
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


@router.message(AddTeacherState.waiting_for_link_info)
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
    await get_teacher_links(force_refresh=True)
    await state.clear()

    res_text = (
        f"🎉 <b>Преподаватель успешно сохранён!</b>\n"
        f"👤 <b>ФИО:</b> {full_name}\n"
        f"🔗 <b>Контакты:</b> {link_info}\n\n"
        f"<i>Данные применены и будут использоваться во всех дистанционных парах.</i>"
    )
    await message.answer(res_text, reply_markup=get_admin_main_kb())

