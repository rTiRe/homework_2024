import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport, Response
from main import app
from typing import AsyncGenerator


def assert_content(response: Response, test_content: list | tuple) -> None:
    content = str(response.content.decode())
    print(content)
    for test_content_part in test_content:
        assert test_content_part in content


sync_client = TestClient(app)

@pytest_asyncio.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client