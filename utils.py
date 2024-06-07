from constants import HOST, PORT, USER, PASSWORD, DBNAME
from datetime import datetime, timezone
import requests

def load_db(protocol: str = 'postgresql+psycopg') -> str:
    return f'{protocol}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'

def load_async_db() -> str:
    return load_db(protocol='postgresql+asyncpg')

def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)

async def get_coin_data(coin: str) -> requests.Response:
    instCoin = f'{coin.upper()}-USD-SWAP'
    url = f"https://www.okx.com/api/v5/market/ticker?instId={instCoin}"
    return requests.get(url)

async def check_coin_name(coin: str) -> bool:
    response = get_coin_data(coin)
    if response.status_code == 200:
        data = response.json()
        return data['code'] == '0'