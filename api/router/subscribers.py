"""
Роутер подписчиков — GET /subscribers, count, {chat_id}, POST/DELETE {chat_id}.

Управляет списком получателей утренних дайджестов и 10-минутных напоминаний.
"""

from fastapi import APIRouter, Depends

from api.deps import verify_admin_access, verify_api_or_tester
from api.schemas.subscribers import (
    SubscriberActionResponse,
    SubscriberCountResponse,
    SubscribersListResponse,
    SubscriberStatusResponse,
)
from db.subscribers import (
    add_subscriber,
    is_subscribed,
    load_subscribers,
    remove_subscriber,
)

router = APIRouter(tags=["Subscribers"], prefix="/subscribers", dependencies=[Depends(verify_api_or_tester)])


@router.get("", response_model=SubscribersListResponse)
async def list_subscribers() -> SubscribersListResponse:
    """
    Возвращает список всех активных подписчиков утренних дайджестов расписания.

    Считывает список Telegram chat_id из файла базы данных подписчиков.
    Сортирует идентификаторы по возрастанию для стабильности ответа API.

    Возвращает SubscribersListResponse со списком chat_id и их количеством.
    """

    subs = sorted(load_subscribers())

    return SubscribersListResponse(count=len(subs), subscribers=subs)


@router.get("/count", response_model=SubscriberCountResponse)
async def count_subscribers() -> SubscriberCountResponse:
    """
    Возвращает суммарное число активных подписчиков расписания.

    Позволяет быстро получить размер аудитории без загрузки полного списка ID.
    Используется в сводках статистики и дашбордах мониторинга.

    Возвращает SubscriberCountResponse с числом подписчиков.
    """

    count = len(load_subscribers())

    return SubscriberCountResponse(count=count)


@router.get("/{chat_id}", response_model=SubscriberStatusResponse)
async def check_subscription(chat_id: int) -> SubscriberStatusResponse:
    """
    Проверяет активность подписки для указанного Telegram Chat ID.

    Быстро сверяет chat_id с множеством в кэше/файле подписчиков.
    Используется клиентами для отрисовки переключателя уведомлений.

    Возвращает SubscriberStatusResponse с булевым статусом is_subscribed.
    """

    active = is_subscribed(chat_id)

    return SubscriberStatusResponse(chat_id=chat_id, is_subscribed=active)


@router.post("/{chat_id}", response_model=SubscriberActionResponse, dependencies=[Depends(verify_admin_access)])
async def subscribe_user(chat_id: int) -> SubscriberActionResponse:
    """
    Принудительно подписывает чат или пользователя на расписание (Admin only).

    Добавляет chat_id в файл базы данных подписчиков с защитой от дублей.
    Защищён verify_admin_access от несанкционированного изменения настроек.

    Возвращает SubscriberActionResponse со статусом операции.
    """

    added = add_subscriber(chat_id)
    msg = "Подписка успешно активирована" if added else "Пользователь уже подписан"

    return SubscriberActionResponse(chat_id=chat_id, is_subscribed=True, message=msg)


@router.delete("/{chat_id}", response_model=SubscriberActionResponse, dependencies=[Depends(verify_admin_access)])
async def unsubscribe_user(chat_id: int) -> SubscriberActionResponse:
    """
    Отключает автоматическую рассылку уведомлений для чата (Admin only).

    Удаляет идентификатор из базы данных подписчиков и сохраняет изменения на диск.
    Защищён verify_admin_access.

    Возвращает SubscriberActionResponse с подтверждением отключения.
    """

    removed = remove_subscriber(chat_id)
    msg = "Подписка отключена" if removed else "Пользователь не был подписан"

    return SubscriberActionResponse(chat_id=chat_id, is_subscribed=False, message=msg)

