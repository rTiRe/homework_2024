"""Module with pydantic Alert modules."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AlertBase(BaseModel):
    """Base alert model."""

    threshold_price: float
    email: str


class AlertCreate(AlertBase):
    """Model for create alert."""

    coin_id: UUID


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
    alert_type: Optional[str] = None
