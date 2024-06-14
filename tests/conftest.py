import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport, Response
from main import app
from typing import AsyncGenerator


def assert_content(response: Response, test_content: list | tuple) -> None:
    content = str(response.content.decode())
    for test_content_part in test_content:
        assert test_content_part in content


def assert_json_contenttype(response: Response) -> None:
    assert 'application/json' in response.headers['content-type']


async def get_coin_id(name: str, async_client: AsyncClient) -> str:
    response = await async_client.get('/coins/')
    coins = response.json()['coins']
    for coin in coins:
        if coin['name'] == name.upper():
            return coin['id']


sync_client = TestClient(app)

@pytest_asyncio.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client