import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio(scope='session')
async def test_get_coins(async_client: AsyncClient) -> None:
    response = await async_client.get('/coins/')
    assert response.status_code == status.HTTP_200_OK
    assert 'application/json' in response.headers['content-type']
    content: dict = response.json()
    assert content.get('coins')