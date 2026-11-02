"""
Хэндлер перехвата новых ДЗ в целевом топике (ID 405).

Отлавливает фото, документы (.docx, .pdf, .txt, код) и текстовые задачи,
валидирует их, проверяет антиспам и ставит задачу в очередь Redis для para-solver.

Уточнения реплаем на собственное задание:
  1. Новое задание HW_CLARIFY_WINDOW_SECONDS ждёт в отложенной очереди
  2. Реплай автора в это окно склеивается с заданием — решение будет одно
  3. Реплай после того, как задание ушло в solver, решается сразу как
     «исправленное решение» к исходному заданию (revision_of), а не как новая задача
"""

import hashlib

from aiogram import Bot, F, Router
from aiogram.types import Message, ReactionTypeEmoji

import config
from core.background import spawn
from core.hw_queue import push_hw_task, schedule_hw_task, take_pending_hw_task
from core.logger import get_logger
from core.redis_cache import (
    check_user_rate_limit,
    is_hash_processed,
    is_message_processed,
    mark_hash_processed,
    mark_message_processed,
)
from services.achievement_events import on_homework_task
from services.achievement_triggers import HomeworkTask, homework_kind

log = get_logger("hw_handler")
router = Router()

# Максимальный размер файла — ограничение Telegram Bot API
MAX_HW_FILE_SIZE = config.HW_MAX_FILE_SIZE

# Короткие реплики чата, которые точно не задание
_FLOOD_WORDS = frozenset({"привет", "хай", "как дела", "спасибо", "спасбо", "спсибо", "ок", "понял", "ку"})

# Маркеры учебного задания; текст длиннее 25 символов считается заданием и без них
_HOMEWORK_KEYWORDS = (
    "реши",
    "вычисли",
    "найди",
    "доказать",
    "дз",
    "вариант",
    "задача",
    "задание",
    "номер",
    "№",
    "=",
    "+",
    "-",
    "?",
    "ответ",
)


def combine_prompt_and_instructions(msg: Message, target: Message) -> str:
    """
    Объединяет инструкцию из подписи/текста реплая и основное задание.

    Если студент ответил на фото заданием 'реши 2 вариант', объединяет тексты.
    Позволяет модели видеть и условие задачи, и конкретные пожелания студента.

    Возвращает объединённую строку промпта или пустую строку.
    """

    u_text = msg.text or msg.caption or ""
    t_text = target.caption or target.text or ""

    if u_text and t_text and u_text != t_text:
        return f"Инструкция: {u_text}\nЗадание: {t_text}"

    return u_text or t_text or ""


def is_valid_homework_prompt(text: str | None, has_media: bool) -> bool:
    """
    Проверяет, содержит ли сообщение запрос на решение учебной задачи.

    Отсекает флуд и короткие приветствия, проверяет наличие ключевых слов ДЗ.
    'Голые' медиафайлы без промпта не берутся, чтобы не решать случайные картинки.

    Возвращает True, если текст похож на учебное задание, иначе False.
    """
    if not text:
        return False
    t = text.lower().strip()
    if t in _FLOOD_WORDS or len(t) < 4:
        return False
    return any(kw in t for kw in _HOMEWORK_KEYWORDS) or len(t) >= 25


def extract_media_meta(msg: Message, target: Message) -> tuple[str | None, str | None, str | None, str | None, int]:
    """
    Извлекает идентификаторы и метаданные медиафайла (фото или документа).

    Проверяет сначала текущее сообщение, затем целевое (при реплае).
    Для фотографий берет последнее изображение списка с максимальным разрешением.

    Возвращает кортеж: (file_id, unique_id, file_name, mime_type, file_size).
    """

    m = msg if (msg.photo or msg.document) else target

    if m.photo:
        p = m.photo[-1]
        return p.file_id, p.file_unique_id, "image.jpg", "image/jpeg", p.file_size or 0

    if m.document:
        d = m.document
        return d.file_id, d.file_unique_id, d.file_name or "doc", d.mime_type, d.file_size or 0

    return None, None, None, None, 0


def _describe_task(msg: Message, target: Message, prompt: str, is_followup: bool) -> HomeworkTask:
    """
    Описывает принятое сообщение для ачивок топика ДЗ.

    Возвращает HomeworkTask.
    """
    _, _, f_name, mime, _ = extract_media_meta(msg, target)
    kind = homework_kind(mime, f_name is not None)
    return HomeworkTask(prompt=prompt, kind=kind, file_name=f_name, is_followup=is_followup)


def _sender_name(msg: Message) -> str | None:
    """Имя автора сообщения для fallback-ФИО ачивок."""
    return msg.from_user.full_name if msg.from_user else None


def compute_content_hash(text: str | None, unique_id: str | None) -> str:
    """
    Вычисляет SHA256 хэш промпта и уникального ID файла для дедупликации.

    Используется для исключения повторной обработки одного и того же задания,
    если несколько студентов пересылают одно условие.

    Возвращает hex-строку 64-символьного SHA256 хэша.
    """

    hasher = hashlib.sha256()
    if text:
        hasher.update(text.encode("utf-8"))

    if unique_id:
        hasher.update(unique_id.encode("utf-8"))

    return hasher.hexdigest()


async def is_hw_allowed(msg: Message, target: Message, user_id: int) -> bool:
    """
    Комплексно проверяет право пользователя и валидность задачи на решение.

    Проверяет Rate Limit в Redis, статус обработки текущего message_id
    и наличие маркеров задания в тексте.

    Возвращает True, если задачу разрешено принять в работу, иначе False.
    """

    if user_id != config.ALLOWED_USER_ID and not await check_user_rate_limit(user_id):
        log.warning("⚠️ Превышен rate-limit для пользователя %s.", user_id)
        return False

    if await is_message_processed(msg.message_id):
        log.debug("Сообщение %s уже обработано. Пропуск.", msg.message_id)
        return False

    has_media = bool(msg.photo or msg.document or target.photo or target.document)
    prompt = combine_prompt_and_instructions(msg, target)
    if not is_valid_homework_prompt(prompt, has_media):
        log.info("ℹ️ Пропуск сообщения без задания (msg_id=%s): '%s'", msg.message_id, prompt)
        return False

    return True


async def acknowledge_hw_task(bot: Bot, msg: Message) -> None:
    """
    Ставит реакцию 👀 на сообщение студента для мгновенной обратной связи.

    Информирует пользователя, что задача принята и поставлена в очередь.
    Ошибки установки реакции подавляются без прерывания пайплайна.

    Ничего не возвращает.
    """

    try:
        await bot.set_message_reaction(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reaction=[ReactionTypeEmoji(emoji="👀")],
        )
    except Exception as e:
        log.debug("Не удалось поставить реакцию на msg_id=%s: %s", msg.message_id, e)


def build_hw_task(
    msg: Message,
    user_id: int,
    prompt: str,
    meta: tuple[str | None, str | None, str | None, int],
    revision_of: int | None = None,
) -> dict:
    """
    Собирает payload задания для очереди solver.

    revision_of — id исходного задания, если это уточнение к уже решаемому.

    Возвращает словарь задания.
    """
    f_id, f_name, mime, f_size = meta
    return {
        "chat_id": msg.chat.id,
        "message_id": msg.message_id,
        "message_thread_id": msg.message_thread_id,
        "user_id": user_id,
        "prompt": prompt,
        "file_id": f_id,
        "file_name": f_name,
        "mime_type": mime,
        "file_size": f_size,
        "revision_of": revision_of,
    }


async def dispatch_hw_task(bot: Bot, msg: Message, task: dict, c_hash: str) -> None:
    """
    Ставит задание в очередь и подтверждает приём реакцией.

    Новое задание откладывается на окно уточнений; исправление к уже
    решаемому заданию ждать нечего — оно уходит в solver сразу.

    Ничего не возвращает.
    """
    if task.get("revision_of"):
        await push_hw_task(task)
    else:
        await schedule_hw_task(task, config.HW_CLARIFY_WINDOW_SECONDS)
    await mark_hash_processed(c_hash)
    await mark_message_processed(msg.message_id)
    await acknowledge_hw_task(bot, msg)


async def is_own_task_reply(msg: Message, target: Message, user_id: int) -> bool:
    """
    Проверяет, что сообщение — реплай автора на его же принятое задание.

    Реплай на чужое задание («реши 2 вариант» под чужим фото) остаётся
    самостоятельной задачей другого студента.

    Возвращает True для уточнения своего задания.
    """
    if target is msg or not target.from_user or target.from_user.id != user_id:
        return False
    return await is_message_processed(target.message_id)


async def merge_into_pending(bot: Bot, msg: Message, target: Message) -> bool:
    """
    Дописывает уточнение к заданию, которое ещё ждёт в окне уточнений.

    Окно перезапускается: можно прислать несколько уточнений подряд.

    Возвращает True, если уточнение склеено с отложенным заданием.
    """
    pending = await take_pending_hw_task(target.message_id)
    if not pending:
        return False
    pending["prompt"] = f"{pending.get('prompt', '')}\nУточнение: {msg.text or msg.caption or ''}".strip()
    await schedule_hw_task(pending, config.HW_CLARIFY_WINDOW_SECONDS)
    await mark_message_processed(msg.message_id)
    await acknowledge_hw_task(bot, msg)
    log.info("✍️ Уточнение msg_id=%s склеено с заданием msg_id=%s", msg.message_id, target.message_id)
    return True


async def validate_hw_file_size(bot: Bot, msg: Message, f_size: int, f_name: str | None) -> bool:
    """
    Проверяет размер медиафайла для защиты сервиса от исчерпания памяти.

    При превышении лимита ставит реакцию 🤷‍♂️ и возвращает отказ.
    Защищает воркер от загрузки неподдерживаемых тяжелых файлов.

    Возвращает True, если файл укладывается в лимит, иначе False.
    """

    if f_size <= MAX_HW_FILE_SIZE:
        return True

    log.warning("⚠️ Файл '%s' превышает лимит (%s байт). Отклонено.", f_name, f_size)
    try:
        await bot.set_message_reaction(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            reaction=[ReactionTypeEmoji(emoji="🤷‍♂️")],
        )
    except Exception as e:
        log.debug("Не удалось выставить реакцию на тяжелый файл: %s", e)

    return False


@router.message((F.chat.id == config.TOPIC_CHAT_ID) & (F.message_thread_id == config.HW_INPUT_TOPIC_THREAD_ID))
async def handle_new_homework(msg: Message, bot: Bot) -> None:
    """
    Перехватывает сообщение с ДЗ в топике и передает в очередь solver.

    Фильтрует чат/топик, проверяет размер файла и дедуплицирует по SHA256.
    Ставит задачу в фоновую очередь для нейросетевого решения.

    Ничего не возвращает.
    """

    user_id = msg.from_user.id if msg.from_user else 0
    target = msg.reply_to_message if msg.reply_to_message else msg
    if not await is_hw_allowed(msg, target, user_id):
        return
    own_reply = await is_own_task_reply(msg, target, user_id)
    merged = own_reply and await merge_into_pending(bot, msg, target)
    if merged or await _accept_new_task(bot, msg, target, user_id, own_reply):
        task_info = _describe_task(msg, target, combine_prompt_and_instructions(msg, target), own_reply)
        spawn(on_homework_task(user_id, _sender_name(msg), bot, task_info))


async def _accept_new_task(bot: Bot, msg: Message, target: Message, user_id: int, own_reply: bool) -> bool:
    """
    Проверяет файл и дубликаты и ставит задание (или исправление) в очередь.

    Возвращает True, если задание принято.
    """
    prompt = combine_prompt_and_instructions(msg, target)
    f_id, u_id, f_name, mime, f_size = extract_media_meta(msg, target)
    if not await validate_hw_file_size(bot, msg, f_size, f_name):
        return False
    c_hash = compute_content_hash(prompt, u_id)
    if await is_hash_processed(c_hash):
        log.warning("⚠️ Повтор ДЗ по SHA256 (msg_id=%s). Пропуск.", msg.message_id)
        return False
    revision_of = target.message_id if own_reply else None
    task = build_hw_task(msg, user_id, prompt, (f_id, f_name, mime, f_size), revision_of)
    await dispatch_hw_task(bot, msg, task, c_hash)
    return True
