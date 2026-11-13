"""
Скрипт скачивания скриншотов посещаемости и сопроводительного текста из Избранного (Saved Messages).

Позволяет старосте в один запуск:
  1. Авторизоваться в Telegram через QR-код (Settings -> Devices -> Link Device)
  2. Выгрузить последние медиа (фото) из диалога 'Избранное' ('me')
  3. Сохранить изображения и текст подписей в data/saved_photos/
  4. Сформировать index.json со списком пар и файлов для автоматической отметки
"""

import asyncio
import getpass
import json
import os
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для корректных импортов при запуске из любой папки
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import qrcode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from core.logger import get_logger

log = get_logger("saved_photos_downloader")

# API credentials пользователя
DEFAULT_API_ID = int(os.getenv("TELEGRAM_API_ID", "20206975"))
DEFAULT_API_HASH = os.getenv("TELEGRAM_API_HASH", "8c07a87842578d965994135946e64392")
SESSION_NAME = "data/telegram_user_session"


def get_output_dir() -> Path:
    """
    Создаёт и возвращает путь к папке сохранения выгруженных скриншотов.

    Используем data/saved_photos внутри проекта для надёжной изоляции.

    Возвращает валидный объект Path директории.
    """
    out_dir = Path("data/saved_photos")
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def format_file_stem(msg_id: int, dt_iso: str) -> str:
    """
    Формирует уникальное имя файла на основе ID сообщения и времени.

    Обеспечивает хронологическую сортировку файлов при просмотре.

    Возвращает строку префикса имени файла.
    """
    clean_dt = dt_iso.replace(":", "-").replace(" ", "_")[:19]
    return f"{clean_dt}_msg_{msg_id}"


def save_message_meta(meta_path: Path, meta_data: dict) -> None:
    """
    Сохраняет текстовую подпись и метаданные сообщения в JSON файл.

    Позволяет сопоставить скриншот с названием пары и датой.

    Ничего не возвращает; записывает файл в кодировке UTF-8.
    """
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)


async def download_photo_message(
    client: TelegramClient, message, out_dir: Path
) -> dict | None:
    """
    Скачивает изображение и текст одного сообщения из Избранного.

    Пропускает сообщения без фото или графических вложений.

    Возвращает словарь с описанием файла или None если вложение отсутствует.
    """
    if not (message.photo or (message.document and "image" in (message.file.mime_type or ""))):
        return None

    stem = format_file_stem(message.id, str(message.date))
    photo_path = out_dir / f"{stem}.jpg"
    meta_path = out_dir / f"{stem}.json"

    log.info("Скачивание фото к сообщению ID %s...", message.id)
    await client.download_media(message, file=str(photo_path))

    text = message.text or message.message or ""
    meta = {
        "msg_id": message.id,
        "date": str(message.date),
        "text": text,
        "photo_file": photo_path.name,
    }
    save_message_meta(meta_path, meta)
    return meta


async def fetch_saved_photos(
    client: TelegramClient, limit: int = 40
) -> list[dict]:
    """
    Итерирует по диалогу 'me' и последовательно загружает все медиа.

    Ограничивает глубину выборки параметром limit для экономии трафика.

    Возвращает список словарей с метаданными скачанных скриншотов.
    """
    out_dir = get_output_dir()
    downloaded: list[dict] = []
    log.info("Поиск последних %s сообщений в 'Избранном'...", limit)

    async for msg in client.iter_messages("me", limit=limit):
        item = await download_photo_message(client, msg, out_dir)
        if item:
            downloaded.append(item)

    index_path = out_dir / "index.json"
    save_message_meta(index_path, {"total": len(downloaded), "items": downloaded})
    return downloaded


async def perform_auth(client: TelegramClient) -> None:
    """
    Авторизует пользователя через QR-код с поддержкой 2FA-пароля.

    Запрашивает пароль двухэтапной аутентификации при наличии защиты.

    Ничего не возвращает; ожидает подтверждения авторизации на устройстве.
    """
    await client.connect()
    if await client.is_user_authorized():
        return

    qr = await client.qr_login()
    print("\n" + "=" * 55)
    print("📲 Отсканируйте QR-код в Telegram на телефоне:")
    print("   Настройки ➔ Устройства ➔ Подключить устройство")
    print("=" * 55 + "\n")

    qr_gen = qrcode.QRCode()
    qr_gen.add_data(qr.url)
    qr_gen.print_ascii(invert=True)

    print(f"\nТокен входа: {qr.url}\nОжидание сканирования...")
    try:
        await qr.wait(timeout=120)
    except SessionPasswordNeededError:
        pwd = getpass.getpass("🔒 Введите пароль двухфакторной аутентификации (2FA): ")
        await client.sign_in(password=pwd)

    print("✅ Авторизация успешно подтверждена!")


async def run_downloader(limit: int = 40) -> None:
    """
    Координирует авторизацию и запуск пакетной выгрузки медиа.

    Создает безопасный сессионный файл в data/ для повторных запусков.

    Ничего не возвращает; выводит итоговое количество файлов.
    """
    client = TelegramClient(SESSION_NAME, DEFAULT_API_ID, DEFAULT_API_HASH)
    await perform_auth(client)
    items = await fetch_saved_photos(client, limit=limit)
    log.info("✅ Успешно выгружено %s скриншотов в %s", len(items), get_output_dir())
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(run_downloader())
