from .constants import HOST, PORT, USER, PASSWORD, DBNAME
from datetime import datetime, timezone


def load_db(protocol: str = 'postgresql+psycopg') -> str:
    return f'{protocol}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'

def load_async_db() -> str:
    return load_db(protocol='postgresql+asyncpg')

def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)