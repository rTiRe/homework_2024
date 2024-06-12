"""Module with pydantic Coin modules."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CoinBase(BaseModel):
    """Base Coin model."""

    name: str


class CoinCreate(CoinBase):
    """Model for create coin (like CoinBase)."""


class CoinRead(CoinBase):
    """Model for return coin."""

    id: UUID


class CoinsRead(BaseModel):
    """Model for return list of coins."""

    coins: list[CoinRead]


class Price(BaseModel):
    """Model for return coin price."""

    price: float
    timedate: datetime


class CoinPriceRead(BaseModel):
    """Model for return coin with prices."""

    name: str
    alert_ids: list[UUID]
    prices: list[Price]
