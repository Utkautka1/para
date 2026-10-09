"""
Хэндлеры управления списком тестеров Swagger UI и запуск Mini App.

Позволяет администратору просматривать, добавлять и удалять Telegram ID
пользователей из белого списка тестеров через команды и инлайн-панель.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.filters.auth import AuthFilter
from bot.templates.admin.testers import (
    AddTesterState,
    format_testers_text,
    get_testers_management_kb,
)
from core.logger import get_logger
from services.testers_manager import (
    add_tester,
    generate_or_get_tester_key,
    get_all_testers,
    remove_tester,
)

log = get_logger("admin_testers")

router = Router()
router.message.filter(AuthFilter())
router.callback_query.filter(AuthFilter())


@router.message(Command("testers"))
async def cmd_list_testers(message: Message) -> None:
    """Отображает список всех зарегистрированных тестеров API."""
    testers = await get_all_testers()
    text = format_testers_text(testers)
    await message.answer(text, reply_markup=get_testers_management_kb(testers))


@router.message(Command("add_tester"))
async def cmd_add_tester(message: Message) -> None:
    """Добавляет тестера по команде /add_tester <id> с генерацией ключа."""
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("⚠️ Использование: <code>/add_tester &lt;telegram_id&gt;</code>")
        return
    uid = int(parts[1])
    await add_tester(uid)
    key = await generate_or_get_tester_key(uid)
    await message.answer(
        f"✅ Пользователь <code>{uid}</code> добавлен в тестеры API!\n"
        f"🔑 Персональный <b>API-ключ</b>:\n<code>{key}</code>"
    )


@router.message(Command("del_tester"))
async def cmd_del_tester(message: Message) -> None:
    """Удаляет тестера по команде /del_tester <id>."""
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("⚠️ Использование: <code>/del_tester &lt;telegram_id&gt;</code>")
        return
    uid = int(parts[1])
    ok = await remove_tester(uid)
    msg = f"🗑️ Пользователь <code>{uid}</code> удален." if ok else "⚠️ Нельзя удалить администратора."
    await message.answer(msg)


@router.message(Command("swagger"))
async def cmd_open_swagger(message: Message) -> None:
    """Отправляет клавиатуру запуска Swagger UI Mini App."""
    testers = await get_all_testers()
    await message.answer("🚀 <b>Swagger UI Портал para-api</b>", reply_markup=get_testers_management_kb(testers))


@router.callback_query(F.data == "admin:testers")
async def cb_admin_testers(callback: CallbackQuery) -> None:
    """Открывает меню управления тестерами из админ-панели."""
    testers = await get_all_testers()
    text = format_testers_text(testers)
    await callback.message.edit_text(text, reply_markup=get_testers_management_kb(testers))
    await callback.answer()


@router.callback_query(F.data == "admin:add_tester")
async def cb_start_add_tester(callback: CallbackQuery, state: FSMContext) -> None:
    """Запрашивает Telegram ID для добавления тестера."""
    await state.set_state(AddTesterState.waiting_for_user_id)
    await callback.message.answer("✏️ Введите Telegram ID пользователя для добавления в тестеры:")
    await callback.answer()


@router.message(AddTesterState.waiting_for_user_id)
async def process_tester_id_input(message: Message, state: FSMContext) -> None:
    """Обрабатывает введенный Telegram ID тестера."""
    text = (message.text or "").strip()
    if not text.isdigit():
        await message.answer("⚠️ Пожалуйста, введите корректный числовой Telegram ID.")
        return
    uid = int(text)
    await add_tester(uid)
    key = await generate_or_get_tester_key(uid)
    await state.clear()
    testers = await get_all_testers()
    msg = f"✅ Пользователь <code>{uid}</code> добавлен!\n🔑 Персональный <b>API-ключ</b>:\n<code>{key}</code>"
    await message.answer(msg, reply_markup=get_testers_management_kb(testers))


@router.callback_query(F.data.startswith("admin:del_tester:"))
async def cb_delete_tester(callback: CallbackQuery) -> None:
    """Удаляет тестера по клику на кнопку в списке."""
    raw_id = callback.data.split(":")[-1]
    if raw_id.isdigit():
        await remove_tester(int(raw_id))
    testers = await get_all_testers()
    text = format_testers_text(testers)
    await callback.message.edit_text(text, reply_markup=get_testers_management_kb(testers))
    await callback.answer("Тестер удален")
