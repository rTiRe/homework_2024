"""Module with utils for coin API."""

import aiohttp


async def get_coin_data(name: str) -> dict:
    """Get coin data from okx api.

    Args:
        name: str - coin name.

    Returns:
        dict: response with coin data.
    """
    inst_coin = f'{name.upper()}-USD-SWAP'
    url = f'https://www.okx.com/api/v5/market/ticker?instId={inst_coin}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
