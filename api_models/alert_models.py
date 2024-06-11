"""Module with pydantic Alert modules."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ValidationInfo, field_validator

from validators import validate_email

from models import Coin

from db_utils import get_session
from sqlalchemy import select

import asyncio


async def check_coin_id(coin_id: UUID) -> None:
    async with get_session() as session:
        coin = await session.execute(select(Coin).where(Coin.id == coin_id))
        if not coin.rowcount:
            raise ValueError('Такой монеты не существует')


class AlertBase(BaseModel):
    """Base alert model."""

    threshold_price: float
    email: str


class AlertCreate(AlertBase):
    """Model for create alert."""

    coin_id: UUID

    @field_validator('threshold_price')
    def validate_threshold_price(cls, price_value: float, fields_info: ValidationInfo) -> float:
        if price_value < 0:
            raise ValueError('threshold_price должен быть больше нуля.')
        return price_value

    @field_validator('email')
    def validate_email(cls, email_value: str, fields_info: ValidationInfo) -> str:
        return validate_email(email_value)


class AlertRead(AlertBase):
    """Model for return alert."""

    id: UUID
    alert_type: str
    coin_id: UUID


class AlertsRead(BaseModel):
    """Model for return list of alerts."""

    alerts: list[AlertRead]


class AlertUpdate(BaseModel):
    """Model for update alert."""

    threshold_price: Optional[float] = None
    email: Optional[str] = None
    coin_id: Optional[UUID] = None

    @field_validator('threshold_price')
    def validate_threshold_price(cls, price_value: float, fields_info: ValidationInfo) -> float:
        if price_value < 0:
            raise ValueError('threshold_price должен быть больше нуля.')
        return price_value

    @field_validator('email')
    def validate_email(cls, email_value: str, fields_info: ValidationInfo) -> str:
        return validate_email(email_value)

