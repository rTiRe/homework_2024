"""Main tests file."""

import asyncio
from typing import AsyncGenerator

import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient, Response

from main import app, update_prices


def assert_content(response: Response, test_content: list | tuple) -> None:
    """Compare content with given content parts and assert.

    Args:
        response: Response - response from server.
        test_content: list | tuple - content parts for compare.
    """
    response_content = str(response.content.decode())
    for test_content_part in test_content:
        assert test_content_part in response_content


def assert_html_contenttype(response: Response, async_client: AsyncClient) -> None:
    """Compare and assert content type.

    Args:
        response: Response - response from server
        async_client: AsyncClient - client
    """
    assert 'text/html; charset=utf-8' in response.headers['content-type']


def assert_json_contenttype(response: Response) -> None:
    """Compare and assert content type.

    Args:
        response: Response - response from server.
    """
    assert 'application/json' in response.headers['content-type']


async def get_coin_id(name: str, async_client: AsyncClient) -> str:
    """Return coin id by name.

    Args:
        name: str - coin name.
        async_client: AsyncClient - client for get response.

    Returns:
        str: _description_
    """
    response = await async_client.get('/coins/')
    coins = response.json()['coins']
    for coin in coins:
        if coin['name'] == name.upper():
            return coin['id']


async def update_and_wait() -> None:
    """Update coins prices and wait."""
    await update_prices()
    await asyncio.sleep(2)


async def add_coin(name: str, async_client: AsyncClient) -> None:
    """Add coin to a database.

    Args:
        name: str - coin name.
        async_client: AsyncClient - client for get response.
    """
    await async_client.post(
        '/coins/',
        json={
            'name': name,
        },
    )


sync_client = TestClient(app)


@pytest_asyncio.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Yield AsyncClient iterator.

    Yields:
        Iterator[AsyncGenerator[AsyncClient, None]]: client.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client
