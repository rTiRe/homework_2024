import pytest
from httpx import AsyncClient
from fastapi import status
from conftest import get_coin_id, add_coin
from main import update_prices


@pytest.mark.asyncio(scope='session')
async def test_put_alert(async_client: AsyncClient) -> None:
    coin1_name = 'sand'
    coin2_name = 'yfi'
    await add_coin(coin1_name, async_client)
    await add_coin(coin2_name, async_client)
    coin1_id = await get_coin_id(coin1_name, async_client)
    coin2_id = await get_coin_id(coin2_name, async_client)
    await update_prices()
    response = await async_client.post(
        '/alerts',
        json={
            'email': 'example1@example.com',
            'threshold_price': 1.0,
            'coin_id': coin1_id,
        },
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.put(
        f'/alerts/{alert_id}',
        json={
            'email': 'edited@example.com',
            'threshold_price': 2.0,
            'coin_id': coin2_id,
        }
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio(scope='session')
async def test_put_alert_incorrect_email1(async_client: AsyncClient) -> None:
    coin1_name = 'sand'
    coin1_id = await get_coin_id(coin1_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': 'example2@example.com',
            'threshold_price': 1.0,
            'coin_id': coin1_id,
        },
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.put(
        f'/alerts/{alert_id}',
        json={
            'email': 'edited',
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_incorrect_email2(async_client: AsyncClient) -> None:
    coin1_name = 'sand'
    coin1_id = await get_coin_id(coin1_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': 'example3@example.com',
            'threshold_price': 1.0,
            'coin_id': coin1_id,
        },
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.put(
        f'/alerts/{alert_id}',
        json={
            'email': 'edited@dfd',
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_negative_price(async_client: AsyncClient) -> None:
    coin1_name = 'sand'
    coin1_id = await get_coin_id(coin1_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': 'example4@example.com',
            'threshold_price': 1.0,
            'coin_id': coin1_id,
        },
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.put(
        f'/alerts/{alert_id}',
        json={
            'threshold_price': -2.0,
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_incorrect_id(async_client: AsyncClient) -> None:
    coin1_name = 'sand'
    coin1_id = await get_coin_id(coin1_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': 'example5@example.com',
            'threshold_price': 1.0,
            'coin_id': coin1_id,
        },
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.put(
        f'/alerts/{alert_id}',
        json={
            'coin_id': 'hfgd',
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_unexist_id(async_client: AsyncClient) -> None:
    coin1_name = 'sand'
    coin1_id = await get_coin_id(coin1_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': 'example6@example.com',
            'threshold_price': 1.0,
            'coin_id': coin1_id,
        },
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.put(
        f'/alerts/{alert_id}',
        json={
            'coin_id': '00000000-0000-0000-0000-000000000000',
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
