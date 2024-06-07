from .constants import HOST, PORT, USER, PASSWORD, DBNAME
from datetime import datetime, timezone


def load_db() -> str:
    return f'postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'

def load_async_db() -> str:
    return f'postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'

def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)