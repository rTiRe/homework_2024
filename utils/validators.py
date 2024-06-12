"""Module with validation methods."""

import re
from datetime import datetime

from fastapi import HTTPException, status

from api.coin_utils import get_coin_data
from utils.time_utils import get_delta_timestamp, get_now_timestamp


def positive_number_validator(number: int | float) -> None:
    """Check if a positive number.

    Args:
        number: int | float - number for check.

    Raises:
        HTTPException: if number is not positive.
    """
    if number < 0:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f'Число {number} не может быть меньше нуля!',
        )


def validate_email(email: str) -> str:
    """Validate email.

    Args:
        email: str - email for validate.

    Raises:
        HTTPException: If email is not valid.

    Returns:
        str: email.
    """
    if '@' not in email:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            'Email должен содержать @',
        )
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            'Переданный email не валидный.',
        )
    return email


async def check_coin_name(name: str) -> bool:
    """Check coin name for exists.

    Args:
        name: str - Coin name.

    Returns:
        bool: True if coin name exists.
    """
    coin_data = await get_coin_data(name)
    return coin_data and coin_data['code'] == '0' and coin_data['data']


async def _validate_not_future(timestamp: float) -> None:
    """Validate that the given timestamp not in futue.

    Args:
        timestamp: float - timestamp value.

    Raises:
        HTTPException: if given timestamp in future.
    """
    if timestamp is not None:
        current_time = await get_now_timestamp()
        if timestamp > current_time:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f'timestamp {timestamp} не может быть в будущем!',
            )


async def _validate_end_after_start(start_timestamp: float, end_timestamp: float) -> None:
    """Validate end_timestamp value less than start_timestamp value.

    Args:
        start_timestamp: float - timestamp start value.
        end_timestamp: float - timestamp end value.

    Raises:
        HTTPException: if end_timestamp value bigger than start_timestamp value.
    """
    if start_timestamp is not None and end_timestamp is not None:
        if end_timestamp < start_timestamp:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                'end_timestamp должен быть меньше start_timestamp',
            )


async def validate_timestamps(start_timestamp: float, end_timestamp: float) -> tuple[float, float]:
    """Validate timestamps.

    Args:
        start_timestamp: float - timestamp start value.
        end_timestamp: float - timestamp end value.

    Returns:
        tuple[float, float]: validated and changed timestamps to datetime.
    """
    await _validate_not_future(start_timestamp)
    await _validate_not_future(end_timestamp)
    await _validate_end_after_start(start_timestamp, end_timestamp)
    if end_timestamp is not None:
        end_datetime = datetime.fromtimestamp(end_timestamp)
    else:
        end_datetime = datetime.fromtimestamp(await get_now_timestamp())
    if start_timestamp is not None:
        start_datetime = datetime.fromtimestamp(start_timestamp)
    else:
        start_datetime = datetime.fromtimestamp(await get_delta_timestamp())
    return start_datetime, end_datetime
