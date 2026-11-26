"""
Unit-тесты для модуля общего пинга /all (bot/handlers/admin/ping_all.py).

Проверяет:
  1. Форматирование тегов участников (@username, tg://user?id с видимым именем).
  2. Исключение автора сообщения из списка пинга (по ID и юзернейму).
  3. Разбиение на пачки по 5 участников (chunk_classmates) для соблюдения лимитов Telegram.
  4. Форматирование чистых постов и сервисных сообщений-упоминаний.
  5. Отправку главного поста, удаление триггера и отправку пачек реплаев.
  6. Поведение при вызове в ЛС и в топиках группы.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Chat, Message, PhotoSize, User

from bot.handlers.admin.ping_all import (
    build_broadcast_message,
    chunk_classmates,
    cmd_ping_all,
    compose_broadcast_content,
    dispatch_broadcast,
    dispatch_mention_batches,
    extract_broadcast_text,
    filter_classmates_to_ping,
    format_chunk_message,
    format_mention_tag,
    is_sender,
    load_classmates_list,
    safe_delete_command_message,
    send_broadcast_payload,
    send_mention_batch,
    validate_group_chat,
)


def test_format_mention_tag_with_username_and_tg_id() -> None:
    """Проверяет приоритет юзернейма при наличии и юзернейма, и tg_id."""
    person = {"full_name": "Мазур Арсений", "username": "Arseniymazur", "tg_id": 1859089085}
    assert format_mention_tag(person) == "@Arseniymazur"


@patch("bot.handlers.admin.ping_all.get_cached_user_id", return_value=None)
def test_format_mention_tag_only_username(mock_cache: MagicMock) -> None:
    """Проверяет возврат @username, если tg_id отсутствует."""
    person = {"full_name": "Калинкевич Арсений", "username": "etow0ndes", "tg_id": None}
    assert format_mention_tag(person) == "@etow0ndes"


def test_format_mention_tag_without_username_with_tg_id() -> None:
    """Проверяет формирование ссылки tg://user?id с видимым именем при отсутствии юзернейма."""
    person = {"full_name": "Куулар Алдын-Сай", "username": None, "tg_id": 7225258693}
    expected = '<a href="tg://user?id=7225258693">Куулар Алдын-Сай</a>'
    assert format_mention_tag(person) == expected


def test_format_mention_tag_escapes_html_in_name() -> None:
    """Проверяет экранирование HTML в имени студента без юзернейма."""
    person = {"full_name": "Студент <Тест & Символы>", "username": None, "tg_id": 12345}
    expected = '<a href="tg://user?id=12345">Студент &lt;Тест &amp; Символы&gt;</a>'
    assert format_mention_tag(person) == expected


def test_format_mention_tag_empty() -> None:
    """Проверяет возврат None при отсутствии и юзернейма, и tg_id."""
    person = {"full_name": "Неизвестный", "username": None, "tg_id": None}
    assert format_mention_tag(person) is None


def test_is_sender_match_by_tg_id() -> None:
    """Проверяет определение отправителя по совпадению tg_id."""
    person = {"full_name": "Тест", "username": "other", "tg_id": 100}
    assert is_sender(person, sender_id=100, sender_username="some_user") is True


def test_is_sender_match_by_username_case_insensitive() -> None:
    """Проверяет регистронезависимое определение отправителя по юзернейму."""
    person = {"full_name": "Тест", "username": "MyUser", "tg_id": None}
    assert is_sender(person, sender_id=999, sender_username="myuser") is True


def test_is_sender_no_match() -> None:
    """Проверяет результат проверки, когда отправитель не совпадает."""
    person = {"full_name": "Тест", "username": "user1", "tg_id": 100}
    assert is_sender(person, sender_id=200, sender_username="user2") is False


def test_filter_classmates_to_ping_excludes_sender() -> None:
    """Проверяет исключение автора команды из результирующего списка для пинга."""
    classmates = [
        {"full_name": "Студент 1", "username": "user1", "tg_id": 1},
        {"full_name": "Автор", "username": "author_user", "tg_id": 2},
        {"full_name": "Студент 3", "username": None, "tg_id": 3},
    ]
    sender = User(id=2, is_bot=False, first_name="Author", username="author_user")
    filtered = filter_classmates_to_ping(classmates, sender)
    assert len(filtered) == 2
    assert all(p["username"] != "author_user" for p in filtered)


def test_chunk_classmates_splits_correctly() -> None:
    """Проверяет разбиение на пачки по 5 участников."""
    sample = [{"tg_id": i} for i in range(12)]
    chunks = chunk_classmates(sample, chunk_size=5)
    assert len(chunks) == 3
    assert len(chunks[0]) == 5
    assert len(chunks[1]) == 5
    assert len(chunks[2]) == 2


def test_chunk_classmates_edge_cases() -> None:
    """Проверяет граничные случаи: пустой список и chunk_size <= 0."""
    assert chunk_classmates([]) == []
    assert chunk_classmates([{"tg_id": 1}], chunk_size=0) == [[{"tg_id": 1}]]


def test_format_chunk_message() -> None:
    """Проверяет сборку строки упоминаний пачки."""
    chunk = [
        {"full_name": "А", "username": "user_a", "tg_id": 1},
        {"full_name": "Б", "username": None, "tg_id": 2},
    ]
    formatted = format_chunk_message(chunk)
    assert formatted == '👥 @user_a <a href="tg://user?id=2">Б</a>'


def test_format_chunk_message_empty() -> None:
    """Проверяет возврат пустой строки при отсутствии валидных участников."""
    assert format_chunk_message([]) == ""


def test_extract_broadcast_text_various_prefixes() -> None:
    """Проверяет корректное отсечение команд /all, .all и mention бота."""
    assert extract_broadcast_text("/all Привет <b>мир</b>") == "Привет <b>мир</b>"
    assert extract_broadcast_text("/ALL@my_bot Важно!") == "Важно!"
    assert extract_broadcast_text(".all\nТекст с новой строки") == "Текст с новой строки"
    assert extract_broadcast_text("/all") == ""


def test_build_broadcast_message_with_text() -> None:
    """Проверяет сохранение авторского текста без добавления никнеймов."""
    msg = build_broadcast_message("<b>Важное объявление!</b>")
    assert msg == "<b>Важное объявление!</b>"


def test_build_broadcast_message_empty_with_reply() -> None:
    """Проверяет формирование сообщения-заглушки при ответе на сообщение."""
    msg = build_broadcast_message("", has_reply=True)
    assert msg == "📢 <b>Внимание к сообщению выше!</b>"


def test_build_broadcast_message_empty_without_reply() -> None:
    """Проверяет формирование сообщения по умолчанию при пустом тексте."""
    msg = build_broadcast_message("", has_reply=False)
    assert msg == "📢 <b>Общий сбор группы!</b>"


@pytest.mark.asyncio
async def test_safe_delete_command_message_success() -> None:
    """Проверяет успешное удаление сообщения команды."""
    msg = AsyncMock(spec=Message)
    msg.delete = AsyncMock()
    await safe_delete_command_message(msg)
    msg.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_safe_delete_command_message_handles_error() -> None:
    """Проверяет, что общая ошибка удаления сообщения безопасно перехватывается."""
    msg = AsyncMock(spec=Message)
    msg.delete = AsyncMock(side_effect=Exception("Telegram error: message can't be deleted"))
    await safe_delete_command_message(msg)
    msg.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_safe_delete_handles_message_not_found() -> None:
    """Проверяет тихое подавление ошибки, если сообщение уже удалено."""
    from aiogram.exceptions import TelegramBadRequest

    msg = AsyncMock(spec=Message)
    err = TelegramBadRequest(method=MagicMock(), message="Bad Request: message to delete not found")
    msg.delete = AsyncMock(side_effect=err)
    await safe_delete_command_message(msg)
    msg.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_broadcast_payload_text_message() -> None:
    """Проверяет отправку текстового поста в топик чата."""
    msg = AsyncMock(spec=Message)
    msg.photo = []
    msg.video = None
    msg.document = None
    msg.animation = None
    msg.chat = Chat(id=-100123, type="supergroup")
    msg.message_thread_id = 555
    msg.bot = AsyncMock()
    await send_broadcast_payload(msg, "<b>Тест</b>", reply_to_id=42)
    msg.bot.send_message.assert_awaited_once_with(
        chat_id=-100123,
        message_thread_id=555,
        text="<b>Тест</b>",
        parse_mode="HTML",
        reply_to_message_id=42,
    )


@pytest.mark.asyncio
async def test_send_broadcast_payload_media_message() -> None:
    """Проверяет отправку медиапоста через copy_to с новой подписью."""
    msg = AsyncMock(spec=Message)
    msg.photo = [MagicMock(spec=PhotoSize)]
    msg.chat = Chat(id=-100123, type="supergroup")
    msg.message_thread_id = 777
    msg.copy_to = AsyncMock()
    await send_broadcast_payload(msg, "<b>Подпись</b>", reply_to_id=10)
    msg.copy_to.assert_awaited_once_with(
        chat_id=-100123,
        message_thread_id=777,
        caption="<b>Подпись</b>",
        parse_mode="HTML",
        reply_to_message_id=10,
    )


@pytest.mark.asyncio
async def test_send_mention_batch() -> None:
    """Проверяет отправку пачки реплаев."""
    msg = AsyncMock(spec=Message)
    msg.bot = AsyncMock()
    await send_mention_batch(msg, chat_id=-100, thread_id=10, reply_to_id=99, batch_text="👥 @u1")
    msg.bot.send_message.assert_awaited_once_with(
        chat_id=-100,
        message_thread_id=10,
        text="👥 @u1",
        parse_mode="HTML",
        reply_to_message_id=99,
    )


@pytest.mark.asyncio
async def test_dispatch_mention_batches() -> None:
    """Проверяет отправку списка пачек упоминаний с микропаузой."""
    msg = AsyncMock(spec=Message, chat=Chat(id=-100, type="supergroup"), message_thread_id=5)
    msg.bot = AsyncMock()
    chunks = [
        [{"full_name": "A", "username": "u1", "tg_id": 1}],
        [{"full_name": "B", "username": "u2", "tg_id": 2}],
    ]
    with patch("asyncio.sleep", new_callable=AsyncMock) as m_sleep:
        await dispatch_mention_batches(msg, main_msg_id=77, chunks=chunks)
        assert msg.bot.send_message.await_count == 2
        assert m_sleep.await_count == 2


@pytest.mark.asyncio
async def test_cmd_ping_all_blocks_in_private_chat() -> None:
    """Проверяет, что вызов /all в личном чате возвращает предупреждение."""
    msg = AsyncMock(spec=Message)
    msg.chat = Chat(id=123, type="private")
    msg.answer = AsyncMock()
    await cmd_ping_all(msg)
    msg.answer.assert_awaited_once()
    assert "предназначена для вызова в топиках" in msg.answer.call_args[0][0]


def _create_mock_all_message() -> AsyncMock:
    """Создает мок сообщения команды /all со всеми необходимыми атрибутами."""
    msg = AsyncMock(spec=Message, chat=Chat(id=-100999, type="supergroup"), message_thread_id=6269)
    msg.html_text, msg.photo, msg.video, msg.document, msg.animation = "/all <b>Сбор!</b>", [], None, None, None
    msg.reply_to_message = None
    msg.from_user = User(id=1000965210, is_bot=False, first_name="Dima", username="rooting_dev")
    msg.bot, msg.delete = AsyncMock(), AsyncMock()
    sent_mock = MagicMock(message_id=4242)
    msg.bot.send_message.return_value = sent_mock
    return msg


@pytest.mark.asyncio
async def test_cmd_ping_all_success_flow() -> None:
    """Проверяет полный успешный цикл выполнения /all в топике группы."""
    msg = _create_mock_all_message()
    mock_data = [
        {"full_name": "Мазур Арсений", "username": "Arseniymazur", "tg_id": 1859089085},
        {"full_name": "Стрыгин Дмитрий", "username": "rooting_dev", "tg_id": 1000965210},
    ]
    with (
        patch("bot.handlers.admin.ping_all.load_classmates_list", new_callable=AsyncMock) as m_load,
        patch("bot.handlers.admin.ping_all.mark_ping_all", new_callable=AsyncMock) as m_mark,
        patch("asyncio.sleep", new_callable=AsyncMock),
    ):
        m_load.return_value = mock_data
        await cmd_ping_all(msg)
        # 1 вызов для основного сообщения + 1 вызов для пачки из 1 человека
        assert msg.bot.send_message.await_count == 2
        # Основной пост содержит только чистый текст автора
        primary_text = msg.bot.send_message.call_args_list[0][1]["text"]
        assert primary_text == "<b>Сбор!</b>"
        # Сервисный реплай содержит никнейм студента
        batch_text = msg.bot.send_message.call_args_list[1][1]["text"]
        assert "@Arseniymazur" in batch_text
        msg.delete.assert_awaited_once()
        m_mark.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_group_chat_handles_both_types() -> None:
    """Проверяет логику валидации для супергруппы и личного чата."""
    group_msg = AsyncMock(spec=Message, chat=Chat(id=-1001, type="supergroup"))
    private_msg = AsyncMock(spec=Message, chat=Chat(id=1001, type="private"))
    private_msg.answer = AsyncMock()
    assert await validate_group_chat(group_msg) is True
    assert await validate_group_chat(private_msg) is False
    private_msg.answer.assert_awaited_once()


def test_compose_broadcast_content() -> None:
    """Проверяет сборку текста сообщения и извлечение reply_id."""
    msg = AsyncMock(spec=Message, html_text="/all <b>Сбор</b>")
    msg.reply_to_message = MagicMock(message_id=99)
    final_text, reply_id = compose_broadcast_content(msg)
    assert final_text == "<b>Сбор</b>"
    assert reply_id == 99


@pytest.mark.asyncio
async def test_dispatch_broadcast_handles_failure() -> None:
    """Проверяет отправку уведомления об ошибке при сбое доставки сообщения."""
    msg = AsyncMock(spec=Message, chat=Chat(id=-1001, type="supergroup"), message_thread_id=1)
    msg.photo, msg.video, msg.document, msg.animation = [], None, None, None
    msg.bot = AsyncMock()
    msg.bot.send_message.side_effect = Exception("Telegram network error")
    msg.answer = AsyncMock()
    await dispatch_broadcast(msg, "текст", reply_id=None, classmates=[])
    msg.answer.assert_awaited_once()
    assert "Ошибка отправки" in msg.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_load_classmates_list() -> None:
    """Проверяет считывание реестра одногруппников через load_json."""
    sample = [
        {"full_name": "Мазур Арсений", "username": "Arseniymazur", "tg_id": 1859089085},
        {"full_name": "Иванов Иван", "username": "illimitation", "tg_id": 1000965210},
    ]
    with patch("bot.handlers.admin.ping_all.load_json", AsyncMock(return_value=sample)):
        classmates = await load_classmates_list()
        assert isinstance(classmates, list)
        assert len(classmates) == 2
        assert any(c.get("username") == "Arseniymazur" for c in classmates)
        assert any(c.get("username") == "illimitation" for c in classmates)
