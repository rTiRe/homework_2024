from sqlalchemy import String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column, validates
from uuid import UUID, uuid4
import re
from utils import check_coin_name
from utils import get_current_datetime
from datetime import datetime
from enum import Enum as PyEnum

class AlertType(PyEnum):
    INCREASE = "increase"
    DECREASE = "decrease"


class Base(DeclarativeBase):
    """Base Moodels class."""


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class Coin(UUIDMixin, Base):
    __tablename__ = 'coins'
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    prices: Mapped[list['CoinPrice']] = relationship(back_populates='coin')
    alerts: Mapped[list['Alert']] = relationship(back_populates='coin')

    @validates('name')
    def validate_name(self, field_key: str, field_value: str) -> str:
        if not check_coin_name(field_value):
            raise ValueError(f'{field_key} is not a valid coin name.')
        return field_value.upper()


class CoinPrice(UUIDMixin, Base):
    __tablename__ = 'coins_prices'
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timedate: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=get_current_datetime)
    coin_id: Mapped[UUID] = mapped_column(ForeignKey('coins.id'))
    coin: Mapped[Coin] = relationship(back_populates='prices')


class Alert(UUIDMixin, Base):
    __tablename__ = 'alerts'
    coin_id: Mapped[UUID] = mapped_column(ForeignKey('coins.id'))
    threshold_price: Mapped[float] = mapped_column(Float, nullable=False)
    email: Mapped[str] = mapped_column(String(50))
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False)
    coin: Mapped[Coin] = relationship(back_populates='alerts')

    @validates('email')
    def validate_email(self, field_key: str, field_value: str) -> str:
        if '@' not in field_value:
            raise ValueError(f'{field_key} must contain "@"')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", field_value):
            raise ValueError('Provided email is not a valid email address.')
        return field_value
