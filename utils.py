from constants import HOST, PORT, USER, PASSWORD, DBNAME
from datetime import datetime, timezone
import requests
import aiohttp

def load_db(protocol: str = 'postgresql+psycopg') -> str:
    return f'{protocol}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'

def load_async_db() -> str:
    return load_db(protocol='postgresql+asyncpg')

def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)

async def get_coin_data(coin: str) -> dict:
    instCoin = f'{coin.upper()}-USD-SWAP'
    url = f'https://www.okx.com/api/v5/market/ticker?instId={instCoin}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def check_coin_name(coin: str) -> bool:
    data = await get_coin_data(coin)
    return data and data['code'] == '0' and data['data']
