"""Tests for api alert put method."""

import pytest
from conftest import add_coin, get_coin_id
from fastapi import status
from httpx import AsyncClient

from main import update_prices


async def get_coins_ids(
    name1: str,
    name2: str,
    async_client: AsyncClient,
) -> tuple[str, str]:
    """Get ids of multiple coins.

    Args:
        name1: str - first coin name.
        name2: str - second coin name.
        async_client: AsyncClient - client.

    Returns:
        tuple[str, str]: _description_
    """
    await add_coin(name1, async_client)
    await add_coin(name2, async_client)
    coin1_id = await get_coin_id(name1, async_client)
    coin2_id = await get_coin_id(name2, async_client)
    return coin1_id, coin2_id


@pytest.mark.asyncio(scope='session')
async def test_put_alert(async_client: AsyncClient) -> None:
    """Test correct alert put.

    Args:
        async_client: AsyncClient - _description_
    """
    coin1_name = 'sand'
    coin2_name = 'yfi'
    coin1_id, coin2_id = await get_coins_ids(
        coin1_name,
        coin2_name,
        async_client,
    )
    await update_prices()
    local_data = {
        'email': 'example1@example.com',
        'threshold_price': 1.0,
        'coin_id': '',
    }
    local_data['coin_id'] = coin1_id
    response = await async_client.post(
        '/alerts',
        json=local_data,
    )
    alert_id = response.json()
    alert_id = alert_id['id']
    response = await async_client.put(
        f'/alerts/{alert_id}',
        json={
            'email': 'edited@example.com',
            'threshold_price': 2.0,
            'coin_id': coin2_id,
        },
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio(scope='session')
async def test_put_alert_incorrect_email1(async_client: AsyncClient) -> None:
    """Alert test with incorrect email part on at symbol.

    Args:
        async_client: AsyncClient - client
    """
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
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_incorrect_email2(async_client: AsyncClient) -> None:
    """Alert test with incorrect email part after at symbol.

    Args:
        async_client: AsyncClient - client
    """
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
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_negative_price(async_client: AsyncClient) -> None:
    """Alert test with negative price.

    Args:
        async_client: AsyncClient - client
    """
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
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_incorrect_id(async_client: AsyncClient) -> None:
    """Alert test with incorrect id.

    Args:
        async_client: AsyncClient - client.
    """
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
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio(scope='session')
async def test_put_alert_unexist_id(async_client: AsyncClient) -> None:
    """Alert test with unexist id.

    Args:
        async_client: AsyncClient - client.
    """
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
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
