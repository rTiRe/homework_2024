"""Module with pydantic Coin modules."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationInfo, field_validator

from time_utils import (get_current_datetime, get_delta_timestamp,
                        get_now_timestamp)


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


class CoinQuery(BaseModel):
    """Model for get coin queries."""

    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None

    @field_validator('start_timestamp', 'end_timestamp')
    def validate_not_future(
        cls,
        timestamp_value: float,
        fields_info: ValidationInfo,
    ) -> float:
        """Validate that the given timestamp not in futue.

        Args:
            timestamp_value: float - timestamp.
            fields_info: ValidationInfo - information about model fields.

        Raises:
            HTTPException: if given timestamp in future.

        Returns:
            float: given timestamp value.
        """
        if timestamp_value is not None:
            current_time = get_current_datetime().timestamp()
            if timestamp_value > current_time:
                raise ValueError(f'{fields_info.field_name} must not be in the future')
        return timestamp_value

    @field_validator('end_timestamp')
    def validate_end_after_start(
        cls,
        timestamp_value: int,
        fields_info: ValidationInfo,
    ) -> int:
        """Validate end_timestamp value less than start_timestamp value.

        Args:
            timestamp_value: int - end_timestamp value.
            fields_info: ValidationInfo - information about model fields.

        Raises:
            HTTPException: if end_timestamp value bigger than start_timestamp value.

        Returns:
            int: end_timestamp value.
        """
        start_value = fields_info.data.get('start_timestamp')
        if start_value is not None and timestamp_value is not None:
            if timestamp_value < start_value:
                raise ValueError('end_timestamp must be after start_timestamp')
        return timestamp_value

    async def convert_to_datetime(self):
        """Convert timestamp integers to datetime objects, or set default for last 5 minutes."""
        if self.end_timestamp is not None:
            self.end_timestamp = datetime.fromtimestamp(self.end_timestamp)
        else:
            self.end_timestamp = datetime.fromtimestamp(await get_now_timestamp())
        if self.start_timestamp is not None:
            self.start_timestamp = datetime.fromtimestamp(self.start_timestamp)
        else:
            self.start_timestamp = datetime.fromtimestamp(await get_delta_timestamp())
