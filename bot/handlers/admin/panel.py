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
    Принудительно обновляет сообщение в топике.

    :param callback: CallbackQuery
    """
    await sync_topic_main_message()
    note = "📢 Сообщение в топике группы принудительно обновлено!"
    text = format_admin_panel_text(note)
    if callback.message:
        await callback.message.edit_text(text, reply_markup=get_admin_main_kb())
    await callback.answer("Топик обновлен!")
