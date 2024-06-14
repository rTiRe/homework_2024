import pytest
from httpx import AsyncClient
from fastapi import status
from conftest import get_coin_id, add_coin
from main import update_prices


@pytest.mark.asyncio(scope='session')
async def test_del_alert(async_client: AsyncClient) -> None:
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
    response = await async_client.delete(f'/alerts/00000000-0000-0000-0000-000000000000')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio(scope='session')
async def test_del_alert_incorrect_id(async_client: AsyncClient) -> None:
    response = await async_client.delete(f'/alerts/0')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY