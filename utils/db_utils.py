"""Module with methods for working with db."""

from typing import AsyncGenerator

from .constants import DBNAME, HOST, PASSWORD, PORT, USER
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def load_db(protocol: str = 'postgresql+psycopg') -> str:
    """Generate url for db.

    Args:
        protocol: str, optional - url protocol. Defaults to 'postgresql+psycopg'.

    Returns:
        str: url.
    """
    user_data = f'{USER}:{PASSWORD}'
    server_data = f'{HOST}:{PORT}'
    return f'{protocol}://{user_data}@{server_data}/{DBNAME}'


def load_async_db() -> str:
    """Generate url for async db.

    Returns:
        str: url.
    """
    return load_db(protocol='postgresql+asyncpg')


def init_session() -> AsyncSession:
    """Initialize session.

    Returns:
        AsyncSession: created session.
    """
    engine = create_async_engine(load_async_db(), echo=True)
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    )


SessionLocal = init_session()


async def get_session() -> AsyncGenerator:
    """Return session as generator.

    Yields:
        Iterator[AsyncGenerator]: Session generator.
    """
    async with SessionLocal() as session:
        yield session
