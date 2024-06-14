"""Coin api get tests."""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio(scope='session')
async def test_get_coins(async_client: AsyncClient) -> None:
    """Test for api get method.

    Args:
        async_client: AsyncClient - client.
    """
    response = await async_client.get('/coins/')
    assert response.status_code == status.HTTP_200_OK
    assert 'application/json' in response.headers['content-type']
    response_content: dict = response.json()
    assert response_content.get('coins')
