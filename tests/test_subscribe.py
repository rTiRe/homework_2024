"""Test subscribe view."""

from copy import deepcopy

import pytest
from conftest import add_coin, assert_content, assert_html_contenttype
from fastapi import status
from httpx import AsyncClient
from test_root import test_root

from main import update_prices

session_literal = 'session'
subscribe_literal = '/subscribe'

global_data = {
    'email': 'testemail@example.com',
    'coin': 'doge',
    'threshold_price': 1.0,
}


@pytest.mark.asyncio(scope=session_literal)
async def test_subscribe_cannot_get_price(async_client: AsyncClient) -> None:
    """Test subscribe with coin without price.

    Args:
        async_client: AsyncClient - price
    """
    await add_coin('doge', async_client)
    response = await async_client.post(
        subscribe_literal,
        data=global_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert_html_contenttype(response, async_client)
    assert_content(
        response,
        ['Не удалось получить цену монеты.'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope=session_literal)
async def test_subscribe(async_client: AsyncClient) -> None:
    """Test correct subscribe.

    Args:
        async_client: AsyncClient - client.
    """
    await update_prices()
    response = await async_client.post(
        subscribe_literal,
        data=global_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert_html_contenttype(response, async_client)
    assert_content(
        response,
        ['Подписка оформлена успешно'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope=session_literal)
async def test_subscribe_with_equal_data(async_client: AsyncClient) -> None:
    """Test subscribe with data equal also exists.

    Args:
        async_client: AsyncClient - client.
    """
    response = await async_client.post(
        subscribe_literal,
        data=global_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert_html_contenttype(response, async_client)
    assert_content(
        response,
        ['Такая подписка уже оформлена!'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope=session_literal)
async def test_subscribe_with_negative_threshold_price(async_client: AsyncClient) -> None:
    """Test subscribe with negative threshold price.

    Args:
        async_client: AsyncClient - client.
    """
    local_data = deepcopy(global_data)
    local_data['threshold_price'] = -1.0
    response = await async_client.post(
        subscribe_literal,
        data=local_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert_html_contenttype(response, async_client)
    assert_content(
        response,
        ['Цена не может быть отрицательной'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope=session_literal)
async def test_subscribe_with_email_without_at(async_client: AsyncClient) -> None:
    """Subscribe test for email withou part after at symbol.

    Args:
        async_client: AsyncClient - client.
    """
    local_data = deepcopy(global_data)
    local_data['email'] = 'testemail'
    response = await async_client.post(
        subscribe_literal,
        data=local_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert_html_contenttype(response, async_client)
    assert_content(
        response,
        ['Email должен содержать @'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope=session_literal)
async def test_subscribe_incorrect_email_after_at(async_client: AsyncClient) -> None:
    """Subscribe test with incorrect email after at symbol.

    Args:
        async_client: AsyncClient - client.
    """
    local_data = deepcopy(global_data)
    local_data['email'] = 'testemail@incorrect part'
    response = await async_client.post(
        subscribe_literal,
        data=local_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert_html_contenttype(response, async_client)
    assert_content(
        response,
        ['Переданный email не валидный.'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope=session_literal)
async def test_subscribe_with_unexist_coin(async_client: AsyncClient) -> None:
    """Subscribe test with unexist coin.

    Args:
        async_client: AsyncClient - client.
    """
    local_data = deepcopy(global_data)
    local_data['coin'] = 'unexist coin'
    response = await async_client.post(
        subscribe_literal,
        data=local_data,
    )
    assert response.status_code == status.HTTP_200_OK
    assert_html_contenttype(response, async_client)
    assert_content(
        response,
        ['Монета не найдена'],
    )
    await test_root(async_client)
