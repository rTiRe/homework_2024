import pytest
from httpx import AsyncClient
from fastapi import status
from conftest import assert_content
from test_root import test_root
from main import update_prices

@pytest.mark.asyncio(scope="session")
async def test_subscribe_cannot_get_price(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/subscribe',
        data={
            'email': 'testemail@example.com',
            'coin': 'eth',
            'threshold_price': 1.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        ['Не удалось получить цену монеты.'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope="session")
async def test_subscribe(async_client: AsyncClient) -> None:
    await update_prices()
    response = await async_client.post(
        '/subscribe',
        data={
            'email': 'testemail@example.com',
            'coin': 'eth',
            'threshold_price': 1.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        ['Подписка оформлена успешно'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope="session")
async def test_subscribe_with_equal_data(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/subscribe',
        data={
            'email': 'testemail@example.com',
            'coin': 'eth',
            'threshold_price': 1.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        ['Такая подписка уже оформлена!'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope="session")
async def test_subscribe_with_negative_threshold_price(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/subscribe',
        data={
            'email': 'testemail@example.com',
            'coin': 'eth',
            'threshold_price': -1.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        ['Цена не может быть отрицательной'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope="session")
async def test_subscribe_with_email_without_at(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/subscribe',
        data={
            'email': 'testemail',
            'coin': 'eth',
            'threshold_price': 1.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        ['Email должен содержать @'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope="session")
async def test_subscribe_with_incorrect_email_part_after_at(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/subscribe',
        data={
            'email': 'testemail@incorrect part',
            'coin': 'eth',
            'threshold_price': 1.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        ['Переданный email не валидный.'],
    )
    await test_root(async_client)


@pytest.mark.asyncio(scope="session")
async def test_subscribe_with_unexist_coin(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/subscribe',
        data={
            'email': 'testemail@example.com',
            'coin': 'unexist coin',
            'threshold_price': 1.0,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        ['Монета не найдена'],
    )
    await test_root(async_client)