import pytest
from httpx import AsyncClient
from fastapi import status
from conftest import assert_content
from test_root import test_root

@pytest.mark.asyncio(scope='session')
async def test_add(async_client: AsyncClient) -> None:
    response = await async_client.post('/add-coin', data={'name': 'eth'})
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        [
            'ETH: ',
            'Монета успешно добавлена!',
        ],
    )
    await test_root(async_client, test_content=['ETH: '])


@pytest.mark.asyncio(scope='session')
async def test_add_one_more_time(async_client: AsyncClient) -> None:
    response = await async_client.post('/add-coin', data={'name': 'eth'})
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        [
            'ETH: ',
            'Монета с таким именем уже существует в базе данных!',
        ],
    )
    await test_root(async_client, test_content=['ETH: '])


@pytest.mark.asyncio(scope='session')
async def test_add_incorrect(async_client: AsyncClient) -> None:
    response = await async_client.post('/add-coin', data={'name': 'non-existing-coin'})
    assert response.status_code == status.HTTP_200_OK
    assert 'text/html; charset=utf-8' in response.headers['content-type']
    assert_content(
        response,
        [
            'ETH: ',
            'Монета не найдена на бирже!',
        ],
    )
    await test_root(async_client, test_content=['ETH: '])
