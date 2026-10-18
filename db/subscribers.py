"""
Модуль локального хранения подписчиков бота.

Сохраняет и считывает список Telegram chat_id из файла data/subscribers.json.
Обеспечивает атомарную запись через временный файл и fsync.
"""

from config import SUBSCRIBERS_FILE_PATH
from core.logger import get_logger
from utils.storage import sync_atomic_save_json, sync_load_json

log = get_logger("subscribers")


def load_subscribers() -> set[int]:
    """
    Загружает множество идентификаторов подписанных пользователей из локального файла.

    Использует защищенную загрузку JSON с дефолтным пустым списком, предотвращая
    сбои сервиса при повреждении или отсутствии файла на диске.

    Возвращает множество (set) целочисленных Telegram chat_id.
    """
    data = sync_load_json(SUBSCRIBERS_FILE_PATH, default=[])
    return set(data) if isinstance(data, list) else set()


def save_subscribers(subs: set[int]) -> bool:
    """
    Атомарно сохраняет актуальное множество подписчиков в JSON-файл.

    Записывает данные во временный файл с последующим атомарным переименованием
    через fsync во избежание порчи данных при внезапном отключении питания.

    Возвращает True в случае успешной записи на диск, иначе False.
    """
    ok = sync_atomic_save_json(SUBSCRIBERS_FILE_PATH, list(subs))
    if ok:
        log.debug(f"Сохранено {len(subs)} подписчиков в {SUBSCRIBERS_FILE_PATH}")
    return ok


def add_subscriber(chat_id: int) -> bool:
    """
    Добавляет новый идентификатор чата в список активных подписчиков.

    Проверяет наличие пользователя во множестве для исключения дубликатов
    и выполняет сохранение в файл только при реальном добавлении.

    Возвращает True, если подписчик был успешно добавлен, False если уже существовал.
    """
    subs = load_subscribers()
    if chat_id not in subs:
        subs.add(chat_id)
        save_subscribers(subs)
        log.info(f"Добавлен новый подписчик: {chat_id}")
        return True
    return False


def remove_subscriber(chat_id: int) -> bool:
    """
    Удаляет идентификатор чата из списка получателей рассылки.

    Безопасно исключает подписчика из множества и обновляет дисковый файл,
    прекращая отправку утренних и предпарных уведомлений.

    Возвращает True, если подписчик был найден и удален, иначе False.
    """
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        log.info(f"Удален подписчик: {chat_id}")
        return True
    return False


def is_subscribed(chat_id: int) -> bool:
    """
    Проверяет, подписан ли пользователь на персональные уведомления в ЛС.

    Используется фильтрами клавиатур и обработчиками для отображения
    актуального статуса колокольчика на кнопках меню.

    Возвращает True, если chat_id присутствует в списке подписчиков, иначе False.
    """
    return chat_id in load_subscribers()


def toggle_subscriber(chat_id: int) -> bool:
    """
    Переключает статус подписки пользователя на противоположный (Toggle).

    Атомарно инвертирует состояние подписки в файле и логирует пользовательское действие
    с информативным эмодзи статуса.

    Возвращает True, если подписка включена, False если отключена.
    """
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        log.info(f"🔕 Пользователь отключил напоминания: {chat_id}")
        return False
    subs.add(chat_id)
    save_subscribers(subs)
    log.info(f"🔔 Пользователь включил напоминания: {chat_id}")
    return True
