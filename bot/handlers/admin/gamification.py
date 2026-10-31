"""
Хэндлеры раздела «Ачивки и очки» админ-панели (только для ALLOWED_USER_ID).

Староста вручную правит бонусные XP и очки гильдии и выдаёт или снимает ачивки.
Вся логика — в services.gamification_admin, здесь только навигация по экранам
и ввод произвольного числа для бонуса (FSM GameAdminState).
После каждого изменения экран перерисовывается из свежего рейтинга.
"""

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from bot.filters.auth import AuthFilter
from bot.templates.admin import gamification as tgame
from core.logger import get_logger
from services import gamification_admin as admin
from services.gamification_admin import StudentTarget

log = get_logger("admin_gamification")

router = Router()
router.callback_query.filter(AuthFilter(), F.message.chat.type == "private")
router.message.filter(AuthFilter(), F.chat.type == "private")


async def _render(call: CallbackQuery, text: str, markup: InlineKeyboardMarkup) -> None:
    """Перерисовывает экран, игнорируя «message is not modified»."""
    try:
        await call.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest as e:
        if "not modified" not in str(e).lower():
            log.warning("Не удалось обновить экран ачивок: %s", e)


async def _load_target(call: CallbackQuery, idx: int) -> StudentTarget | None:
    """Находит студента по индексу или сообщает, что список устарел."""
    target = await admin.get_student(idx)
    if not target:
        await call.answer(tgame.student_not_found_text, show_alert=True)
    return target


async def _show_card(call: CallbackQuery, idx: int) -> None:
    """Показывает карточку студента со свежими XP, очками и бонусами."""
    target = await _load_target(call, idx)
    if not target:
        return
    xp_bonus, guild_bonus = await admin.get_bonuses(target)
    text = tgame.student_card_text(target.profile, xp_bonus, guild_bonus)
    await _render(call, text, tgame.student_card_ikb(idx))


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "list"))
async def game_students(call: CallbackQuery) -> None:
    """
        Список студентов для управления ачивками и очками
    :param call: CallbackQuery
    :return:
    """
    await call.answer()
    students = await admin.list_students()
    await _render(call, tgame.students_text, tgame.students_ikb(students))


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "card"))
async def game_card(call: CallbackQuery, callback_data: tgame.GameAdminCallback, state: FSMContext) -> None:
    """
        Карточка студента (и отмена ввода числа — та же кнопка «Назад»)
    :param call: CallbackQuery
    :param callback_data: индекс студента
    :param state: FSMContext
    :return:
    """
    await call.answer()
    await state.clear()
    await _show_card(call, callback_data.idx)


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "ask"))
async def game_ask_amount(call: CallbackQuery, callback_data: tgame.GameAdminCallback, state: FSMContext) -> None:
    """
        Превращает карточку в запрос числа для бонуса XP или очков гильдии
    :param call: CallbackQuery
    :param callback_data: индекс студента и вид бонуса ('xp' / 'guild')
    :param state: FSMContext
    :return:
    """
    await call.answer()
    target = await _load_target(call, callback_data.idx)
    if not target or callback_data.value not in admin.BONUS_KINDS:
        return
    await state.set_state(tgame.GameAdminState.waiting_for_amount)
    # Запоминаем сообщение-карточку: после ввода оно же снова станет карточкой
    await state.update_data(idx=callback_data.idx, kind=callback_data.value, message_id=call.message.message_id)
    text = tgame.ask_amount_text(target.profile.short_fio, callback_data.value)
    await _render(call, text, tgame.ask_amount_ikb(callback_data.idx))


@router.message(tgame.GameAdminState.waiting_for_amount)
async def game_enter_amount(message: Message, state: FSMContext) -> None:
    """
        Применяет вписанное число и возвращает карточку на место запроса
    :param message: Message
    :param state: FSMContext
    :return:
    """
    await _delete_quietly(message)
    data = await state.get_data()
    parsed = tgame.parse_amount(message.text)
    if parsed is None:
        await _edit_panel(message, data["message_id"], tgame.incorrect_amount_text, tgame.ask_amount_ikb(data["idx"]))
        return
    await state.clear()
    target = await admin.get_student(data["idx"])
    if not target:
        await _edit_panel(message, data["message_id"], tgame.student_not_found_text, None)
        return
    await _apply_amount(message, target, data["kind"], parsed)
    await _edit_card(message, data["message_id"], data["idx"])


async def _delete_quietly(message: Message) -> None:
    """Удаляет введённое старостой сообщение, чтобы в чате оставалась только панель."""
    try:
        await message.delete()
    except TelegramBadRequest as e:
        log.debug("Не удалось удалить сообщение с числом: %s", e)


async def _edit_panel(message: Message, panel_id: int, text: str, markup: InlineKeyboardMarkup | None) -> None:
    """Меняет сообщение-панель по id, игнорируя «message is not modified»."""
    try:
        await message.bot.edit_message_text(text, chat_id=message.chat.id, message_id=panel_id, reply_markup=markup)
    except TelegramBadRequest as e:
        if "not modified" not in str(e).lower():
            log.warning("Не удалось обновить панель ачивок: %s", e)


async def _apply_amount(message: Message, target: StudentTarget, kind: str, parsed: tuple[bool, int]) -> None:
    """Выставляет или прибавляет бонус по разобранному вводу."""
    exact, value = parsed
    if exact:
        await admin.set_bonus(message.bot, target, kind, value)
    else:
        await admin.adjust_bonus(message.bot, target, kind, value)


async def _edit_card(message: Message, panel_id: int, idx: int) -> None:
    """Возвращает на место запроса свежую карточку студента."""
    target = await admin.get_student(idx)
    if target:
        text = tgame.student_card_text(target.profile, *await admin.get_bonuses(target))
        await _edit_panel(message, panel_id, text, tgame.student_card_ikb(idx))


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "bonus"))
async def game_bonus(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None:
    """
        Начисление или списание бонусных XP / очков гильдии
    :param call: CallbackQuery
    :param callback_data: индекс студента и 'xp|100' / 'guild|-10'
    :return:
    """
    kind, step = callback_data.value.split("|")
    target = await _load_target(call, callback_data.idx)
    if not target or kind not in admin.BONUS_KINDS:
        return
    value = await admin.adjust_bonus(call.bot, target, kind, int(step))
    await call.answer(f"{int(step):+d} → бонус {value:+d}")
    await _show_card(call, callback_data.idx)


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "reset"))
async def game_reset(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None:
    """
        Обнуление бонусов студента
    :param call: CallbackQuery
    :param callback_data: индекс студента
    :return:
    """
    target = await _load_target(call, callback_data.idx)
    if not target:
        return
    await admin.reset_bonuses(call.bot, target)
    await call.answer("Бонусы обнулены")
    await _show_card(call, callback_data.idx)


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "cats"))
async def game_categories(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None:
    """
        Категории ачивок студента
    :param call: CallbackQuery
    :param callback_data: индекс студента
    :return:
    """
    await call.answer()
    target = await _load_target(call, callback_data.idx)
    if not target:
        return
    text = tgame.student_card_text(target.profile, *await admin.get_bonuses(target))
    await _render(call, text, tgame.categories_ikb(callback_data.idx, target.profile.unlocked_achievements))


async def _show_category(call: CallbackQuery, idx: int, category: str) -> None:
    """Показывает ачивки категории с отметками выдано / не выдано."""
    target = await _load_target(call, idx)
    if not target or category not in tgame.CATEGORY_TITLES:
        return
    unlocked = target.profile.unlocked_achievements
    await _render(call, tgame.category_text(target.profile, category), tgame.category_ikb(idx, category, unlocked))


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "cat"))
async def game_category(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None:
    """
        Ачивки одной категории
    :param call: CallbackQuery
    :param callback_data: индекс студента и категория
    :return:
    """
    await call.answer()
    await _show_category(call, callback_data.idx, callback_data.value)


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "toggle"))
async def game_toggle(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None:
    """
        Выдать или снять ачивку
    :param call: CallbackQuery
    :param callback_data: индекс студента и 'категория|id_ачивки'
    :return:
    """
    category, achievement_id = callback_data.value.split("|", 1)
    target = await _load_target(call, callback_data.idx)
    if not target or achievement_id not in tgame.ACHIEVEMENTS_MAP:
        return
    granted = await admin.toggle_achievement(call.bot, target, achievement_id)
    await call.answer("✅ Выдана" if granted else "➖ Снята")
    await _show_category(call, callback_data.idx, category)
