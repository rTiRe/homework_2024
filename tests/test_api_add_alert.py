"""Tests for add alert function."""

import pytest
from conftest import add_coin, assert_json_contenttype, get_coin_id
from fastapi import status
from httpx import AsyncClient

from main import update_prices


@pytest.mark.asyncio(scope='session')
async def test_add_alert_no_price(async_client: AsyncClient) -> None:
    """Test add alert with no price in table.

    Args:
        async_client: AsyncClient - client.
    """
    coin_name = 'sol'
    await add_coin(coin_name, async_client)
    email = 'testemail@example.com'
    coin_id = await get_coin_id(coin_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': email,
            'threshold_price': 1.0,
            'coin_id': coin_id,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'Не удалось получить текущую цену монеты'


@pytest.mark.asyncio(scope='session')
async def test_add_alert(async_client: AsyncClient) -> None:
    """Test add alert correctly.

    Args:
        async_client: AsyncClient - client.
    """
    await update_prices()
    coin_name = 'sol'
    email = 'testemail@example.com'
    coin_id = await get_coin_id(coin_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': email,
            'threshold_price': 1.0,
            'coin_id': coin_id,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('email') == email


@pytest.mark.asyncio(scope='session')
async def test_add_alert_incorrect_email(async_client: AsyncClient) -> None:
    """Test add alert without at symbol.

    Args:
        async_client: AsyncClient - client.
    """
    coin_name = 'sol'
    email = 'testemail'
    coin_id = await get_coin_id(coin_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': email,
            'threshold_price': 1.0,
            'coin_id': coin_id,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'Email должен содержать @'


@pytest.mark.asyncio(scope='session')
async def test_add_alert_incorrect_email2(async_client: AsyncClient) -> None:
    """Test add alert with incorrect email part after at symbol.

    Args:
        async_client: AsyncClient - client.
    """
    coin_name = 'sol'
    email = 'testemail@grfd'
    coin_id = await get_coin_id(coin_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': email,
            'threshold_price': 1.0,
            'coin_id': coin_id,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'Переданный email не валидный.'


@pytest.mark.asyncio(scope='session')
async def test_add_alert_incorrect_uuid(async_client: AsyncClient) -> None:
    """Test add alert with incorrect uuid.

    Args:
        async_client: AsyncClient - client.
    """
    email = 'testemail@example.com'
    response = await async_client.post(
        '/alerts',
        json={
            'email': email,
            'threshold_price': 1.0,
            'coin_id': 'htgrftfdd',
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail')[0]['type'] == 'uuid_parsing'


@pytest.mark.asyncio(scope='session')
async def test_add_alert_unexist_uuid(async_client: AsyncClient) -> None:
    """Test add alert with unexist uuid.

    Args:
        async_client: AsyncClient - client.
    """
    email = 'testemail@example.com'
    response = await async_client.post(
        '/alerts',
        json={
            'email': email,
            'threshold_price': 1.0,
            'coin_id': '00000000-0000-0000-0000-000000000000',
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'Монета не найдена в базе данных!'


@pytest.mark.asyncio(scope='session')
async def test_add_alert_negative_price(async_client: AsyncClient) -> None:
    """Test add alert with negative price.

    Args:
        async_client: AsyncClient - client.
    """
    coin_name = 'sol'
    email = 'testemail@example.com'
    coin_id = await get_coin_id(coin_name, async_client)
    response = await async_client.post(
        '/alerts',
        json={
            'email': email,
            'threshold_price': -1.0,
            'coin_id': coin_id,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'threshold_price должен быть больше нуля.'
