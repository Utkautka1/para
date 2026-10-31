"""
Хэндлеры раздела «Ачивки и очки» админ-панели (только для ALLOWED_USER_ID).

Староста вручную правит бонусные XP и очки гильдии и выдаёт или снимает ачивки.
Вся логика — в services.gamification_admin, здесь только навигация по экранам.
После каждого изменения экран перерисовывается из свежего рейтинга.
"""

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from bot.filters.auth import AuthFilter
from bot.templates.admin import gamification as tgame
from core.logger import get_logger
from services import gamification_admin as admin
from services.gamification_admin import StudentTarget

log = get_logger("admin_gamification")

router = Router()
router.callback_query.filter(AuthFilter(), F.message.chat.type == "private")


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
async def game_card(call: CallbackQuery, callback_data: tgame.GameAdminCallback) -> None:
    """
        Карточка студента
    :param call: CallbackQuery
    :param callback_data: индекс студента
    :return:
    """
    await call.answer()
    await _show_card(call, callback_data.idx)


@router.callback_query(tgame.GameAdminCallback.filter(F.action == "noop"))
async def game_noop(call: CallbackQuery) -> None:
    """
        Заголовок ряда кнопок — ничего не делает
    :param call: CallbackQuery
    :return:
    """
    await call.answer()


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
