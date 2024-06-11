"""SQLAlchemy models."""

import re
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column,
                            relationship, validates)

from time_utils import get_current_datetime
from validators import check_coin_name

NAME_FIELD_LENGTH = 50
ALERT_FIELD_LENGTH = 3


class Base(DeclarativeBase):
    """Base Moodels class."""


class UUIDMixin:
    """Mixin for create UUID field."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class Coin(UUIDMixin, Base):
    """Model for Coins table."""

    __tablename__ = 'coins'
    name: Mapped[str] = mapped_column(String(NAME_FIELD_LENGTH), unique=True, nullable=False)
    prices: Mapped[list['CoinPrice']] = relationship(back_populates='coin')
    alerts: Mapped[list['Alert']] = relationship(back_populates='coin')

    @validates('name')
    def validate_name(self, field_key: str, field_value: str) -> str:
        """Coin name validator.

        Args:
            field_key: str - column name.
            field_value: str - column value.

        Raises:
            ValueError: raises if coin name is not valid.

        Returns:
            str: upper cased coin name.
        """
        if not check_coin_name(field_value):
            raise ValueError(f'{field_key} is not a valid coin name.')
        return field_value.upper()


class CoinPrice(UUIDMixin, Base):
    """Model for table with Coin Prices."""

    __tablename__ = 'coins_prices'
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timedate: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=get_current_datetime,
        index=True,
    )
    coin_id: Mapped[UUID] = mapped_column(ForeignKey('coins.id'))
    coin: Mapped[Coin] = relationship(back_populates='prices')


class Alert(UUIDMixin, Base):
    """Model for Alerts."""

    __tablename__ = 'alerts'
    coin_id: Mapped[UUID] = mapped_column(ForeignKey('coins.id'))
    threshold_price: Mapped[float] = mapped_column(Float, nullable=False)
    email: Mapped[str] = mapped_column(String(NAME_FIELD_LENGTH), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(ALERT_FIELD_LENGTH), nullable=False)
    coin: Mapped[Coin] = relationship(back_populates='alerts')
    __table_args__ = (
        UniqueConstraint(
            'email',
            'coin_id',
            'alert_type',
            'threshold_price',
            name='coin_alert_type',
        ),
    )

    @validates('email')
    def validate_email(self, field_key: str, field_value: str) -> str:
        """Email validator.

        Args:
            field_key: str - column name.
            field_value: str - column value.

        Raises:
            ValueError: if email is not valid.

        Returns:
            str: email if correct.
        """
        if '@' not in field_value:
            raise ValueError('email must contain "@"')
        if not re.match(r'[^@]+@[^@]+\.[^@]+', field_value):
            raise ValueError('Provided email is not a valid email address.')
        return field_value
