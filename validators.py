"""Module with validation methods."""

import re

from fastapi import HTTPException, status

from api.coin_utils import get_coin_data


def positive_number_validator(number: int | float) -> None:
    """Check if a positive number.

    Args:
        number: int | float - number for check.

    Raises:
        HTTPException: if number is not positive.
    """
    if number < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Number must be positive!')


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
        raise ValueError('Email must contain @')
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        raise ValueError('Provided email is not a valid email address.')
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
