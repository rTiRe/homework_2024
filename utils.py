from constants import HOST, PORT, USER, PASSWORD, DBNAME, SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from datetime import datetime, timezone
import aiohttp
import aiosmtplib
from email.message import EmailMessage

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


async def send_email(subject: str, recipient: str, body: str) -> None:
    message = EmailMessage()
    message['From'] = SMTP_USERNAME
    message['To'] = recipient
    message['Subject'] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
