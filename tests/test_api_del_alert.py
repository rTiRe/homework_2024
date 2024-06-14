"""Tests for delete alert."""

import pytest
from conftest import add_coin, get_coin_id
from fastapi import status
from httpx import AsyncClient

from main import update_prices


@pytest.mark.asyncio(scope='session')
async def test_del_alert(async_client: AsyncClient) -> None:
    """Test for delete with correct data.

    Args:
        async_client: AsyncClient - client.
    """
    coin_name = 'uni'
    await add_coin(coin_name, async_client)
    coin_id = await get_coin_id(coin_name, async_client)
    await update_prices()
    response = await async_client.post(
        '/alerts',
        json={
            'email': 'example@example.com',
            'threshold_price': 1.0,
            'coin_id': coin_id,
        },
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.delete(f'/alerts/{alert_id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio(scope='session')
async def test_del_alert_unexist_id(async_client: AsyncClient) -> None:
    """Test for delete with unexist id.

    Args:
        async_client: AsyncClient - client.
    """
    response = await async_client.delete('/alerts/00000000-0000-0000-0000-000000000000')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(scope='session')
async def test_del_alert_incorrect_id(async_client: AsyncClient) -> None:
    """Test for delete with incorrect id.

    Args:
        async_client: AsyncClient - client.
    """
    response = await async_client.delete('/alerts/0')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
