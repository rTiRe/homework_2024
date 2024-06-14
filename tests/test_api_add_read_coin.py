import pytest
from httpx import AsyncClient
from fastapi import status
from conftest import get_coin_id, assert_json_contenttype
from main import update_prices
from utils.time_utils import get_now_timestamp, get_delta_timestamp
from test_api_get_coin import test_get_coins
import asyncio


@pytest.mark.asyncio(scope='session')
async def test_api_add_coin(async_client: AsyncClient) -> None:
    coin_name = 'btc'
    response = await async_client.post(
        '/coins/',
        json={
            'name': coin_name,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('name') == coin_name.upper()


@pytest.mark.asyncio(scope='session')
async def test_api_add_existing_coin(async_client: AsyncClient) -> None:
    coin_name = 'btc'
    response = await async_client.post(
        '/coins/',
        json={
            'name': coin_name,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'Монета с таким именем уже добавлена!'


@pytest.mark.asyncio(scope='session')
async def test_api_add_coin_with_unexisting_name(async_client: AsyncClient) -> None:
    coin_name = 'unexisting name'
    response = await async_client.post(
        '/coins/',
        json={
            'name': coin_name,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'Монета не найдена на бирже!'


@pytest.mark.asyncio(scope='session')
async def test_get_coins_with_data(async_client: AsyncClient) -> None:
    await test_get_coins(async_client)
    response = await async_client.get('/coins/')
    result_content: dict = response.json()
    assert result_content.get('coins')


@pytest.mark.asyncio(scope='session')
async def test_get_coin_data(async_client: AsyncClient) -> None:
    prices_count = 3
    coin_name = 'btc'
    for _ in range(prices_count):
        await update_prices()
    coin_id = await get_coin_id(coin_name, async_client)
    response = await async_client.get(f'/coins/{coin_id}')
    assert response.status_code == status.HTTP_200_OK
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('name') == coin_name.upper()
    assert not result_content.get('alert_ids')
    assert len(result_content.get('prices')) == prices_count


@pytest.mark.asyncio(scope='session')
async def test_get_unexisting_coin_data(async_client: AsyncClient) -> None:
    coin_id = '00000000-0000-0000-0000-000000000000'
    response = await async_client.get(f'/coins/{coin_id}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'Монета не найдена в базе данных!'


@pytest.mark.asyncio(scope='session')
async def test_get_coin_data_with_timestamp(async_client: AsyncClient) -> None:
    prices_count = 3
    coin_name = 'btc'
    for _ in range(prices_count):
        await update_prices()
        await asyncio.sleep(2)
    coin_id = await get_coin_id(coin_name, async_client)
    start_timestamp = await get_delta_timestamp(0.05)
    end_timestamp = await get_now_timestamp()
    response = await async_client.get(
        f'/coins/{coin_id}?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}',
    )
    assert response.status_code == status.HTTP_200_OK
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('name') == coin_name.upper()
    assert not result_content.get('alert_ids')
    assert len(result_content.get('prices')) <= 2


@pytest.mark.asyncio(scope='session')
async def test_coin_data_incorrect_timestamps_positions(async_client: AsyncClient) -> None:
    prices_count = 2
    coin_name = 'btc'
    coin_id = await get_coin_id(coin_name, async_client)
    start_seconds = round((prices_count-1)/60, 2)
    start_timestamp = await get_delta_timestamp(start_seconds)
    end_timestamp = await get_now_timestamp()
    response = await async_client.get(
        f'/coins/{coin_id}?start_timestamp={end_timestamp}&end_timestamp={start_timestamp}',
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == 'end_timestamp должен быть меньше start_timestamp'


@pytest.mark.asyncio(scope='session')
async def test_coin_data_start_timestamp_in_future(async_client: AsyncClient) -> None:
    prices_count = 2
    coin_name = 'btc'
    coin_id = await get_coin_id(coin_name, async_client)
    start_seconds = round((prices_count-1)/60, 2)
    start_timestamp = (await get_delta_timestamp(start_seconds)) * 1000
    end_timestamp = await get_now_timestamp()
    response = await async_client.get(
        f'/coins/{coin_id}?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}',
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == f'timestamp {start_timestamp} не может быть в будущем!'


@pytest.mark.asyncio(scope='session')
async def test_coin_data_end_timestamp_in_future(async_client: AsyncClient) -> None:
    prices_count = 2
    coin_name = 'btc'
    coin_id = await get_coin_id(coin_name, async_client)
    start_seconds = round((prices_count-1)/60, 2)
    start_timestamp = await get_delta_timestamp(start_seconds)
    end_timestamp = (await get_now_timestamp()) * 1000
    response = await async_client.get(
        f'/coins/{coin_id}?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}',
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert_json_contenttype(response)
    result_content: dict = response.json()
    assert result_content.get('detail') == f'timestamp {end_timestamp} не может быть в будущем!'
