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
    """Список всех активных подписчиков персональных напоминаний."""
    subs = sorted(load_subscribers())
    return SubscribersListResponse(count=len(subs), subscribers=subs)


@router.get("/count", response_model=SubscriberCountResponse)
async def count_subscribers() -> SubscriberCountResponse:
    """Общее количество пользователей с включёнными напоминаниями."""
    count = len(load_subscribers())
    return SubscriberCountResponse(count=count)


@router.get("/{chat_id}", response_model=SubscriberStatusResponse)
async def check_subscription(chat_id: int) -> SubscriberStatusResponse:
    """Проверка активности подписки для конкретного Telegram Chat ID."""
    active = is_subscribed(chat_id)
    return SubscriberStatusResponse(chat_id=chat_id, is_subscribed=active)


@router.post("/{chat_id}", response_model=SubscriberActionResponse, dependencies=[Depends(verify_admin_access)])
async def subscribe_user(chat_id: int) -> SubscriberActionResponse:
    """Включение подписки пользователя на уведомления (Admin only)."""
    added = add_subscriber(chat_id)
    msg = "Подписка успешно активирована" if added else "Пользователь уже подписан"
    return SubscriberActionResponse(chat_id=chat_id, is_subscribed=True, message=msg)


@router.delete("/{chat_id}", response_model=SubscriberActionResponse, dependencies=[Depends(verify_admin_access)])
async def unsubscribe_user(chat_id: int) -> SubscriberActionResponse:
    """Отключение подписки пользователя на уведомления (Admin only)."""
    removed = remove_subscriber(chat_id)
    msg = "Подписка отключена" if removed else "Пользователь не был подписан"
    return SubscriberActionResponse(chat_id=chat_id, is_subscribed=False, message=msg)
