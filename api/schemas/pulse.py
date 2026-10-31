"""Схемы диагностики «пульса группы» в Mini App."""

from pydantic import BaseModel, Field


class PulseTraceRequest(BaseModel):
    """Запрос записи кардиограммы: кто смотрит на пульс."""

    init_data: str | None = Field(None, description="Сырая строка Telegram.WebApp.initData")


class PulseTraceResponse(BaseModel):
    """Одноразовый идентификатор записи кардиограммы."""

    trace: str


class PulseReadingRequest(BaseModel):
    """Итог записи кардиограммы."""

    # Порог 100 000 — далеко за пределами честной игры, отсекает мусорные значения
    score: int = Field(..., ge=0, le=100_000)


class PulseReadingResponse(BaseModel):
    """Результат расшифровки кардиограммы."""

    accepted: bool
    unlocked: bool = False
    title: str | None = None
    icon: str | None = None
    xp: int = 0
