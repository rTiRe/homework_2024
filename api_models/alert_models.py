"""Module with pydantic Alert modules."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ValidationInfo, field_validator

from utils.validators import validate_email


class AlertBase(BaseModel):
    """Base alert model."""

    threshold_price: float
    email: str


class AlertCreate(AlertBase):
    """Model for create alert."""

    coin_id: UUID

    @field_validator('threshold_price')
    @classmethod
    def validate_threshold_price(cls, price_value: float, fields_info: ValidationInfo) -> float:
        """Threshold price validator.

        Args:
            price_value: float - threshold price.
            fields_info: ValidationInfo - model fields information.

        Raises:
            ValueError: if value less than zero.

        Returns:
            float: threshold price.
        """
        if price_value < 0:
            raise ValueError('threshold_price должен быть больше нуля.')
        return price_value

    @field_validator('email')
    @classmethod
    def validate_email(cls, email_value: str, fields_info: ValidationInfo) -> str:
        """Email validator.

        Args:
            email_value: str - email.
            fields_info: ValidationInfo - model fields information.

        Returns:
            str: email
        """
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
    @classmethod
    def validate_threshold_price(cls, price_value: float, fields_info: ValidationInfo) -> float:
        """Threshold price validator.

        Args:
            price_value: float - threshold price.
            fields_info: ValidationInfo - model fields information.

        Raises:
            ValueError: if value less than zero.

        Returns:
            float: threshold price.
        """
        if price_value < 0:
            raise ValueError('threshold_price должен быть больше нуля.')
        return price_value

    @field_validator('email')
    @classmethod
    def validate_email(cls, email_value: str, fields_info: ValidationInfo) -> str:
        """Email validator.

        Args:
            email_value: str - email.
            fields_info: ValidationInfo - model fields information.

        Returns:
            str: email
        """
        return validate_email(email_value)
