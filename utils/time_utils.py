"""Module with methods for working with time."""

from datetime import datetime, timedelta, timezone


def get_current_datetime() -> datetime:
    """Get current datetime in UTC timezone.

    Returns:
        datetime: current UTC datetime.
    """
    return datetime.now(timezone.utc)


async def get_delta_timestamp(delta_minutes: float = 5.0) -> float:
    """Get timestamp for delta minutes ago.

    Args:
        delta_minutes: int - delta between now and needed moment. Defaults to 5.

    Returns:
        float: delta minutes ago timestamp.
    """
    return (get_current_datetime() - timedelta(minutes=delta_minutes)).timestamp()


async def get_now_timestamp() -> float:
    """Get current time in timestamp format.

    Returns:
        float: current timestamp.
    """
    return get_current_datetime().timestamp()
