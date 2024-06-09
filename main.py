"""App."""

from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
import uvicorn
from constants import APP_HOST, APP_PORT
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Coin, CoinPrice, Alert
from utils import load_async_db, check_coin_name, get_coin_data, send_email
from typing import AsyncGenerator

engine = create_async_engine(load_async_db(), echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_session() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session


async def check_alerts_and_send_emails(db: AsyncSession, coin: Coin, current_price: float):
    alerts = await db.execute(
        select(Alert).where(Alert.coin_id == coin.id)
    )
    alerts = alerts.scalars().all()
    for alert in alerts:
        if ((alert.alert_type == "inc" and current_price >= alert.threshold_price) or
            (alert.alert_type == "dec" and current_price <= alert.threshold_price)):
            await send_email(
                "Price Alert",
                alert.email,
                f"Alert for {coin.name}: price reached {current_price} which triggers your alert set at {alert.threshold_price}."
            )


async def update_prices():
    async for session in get_session():
        coins = await session.execute(select(Coin))
        coins = coins.scalars().all()
        for coin in coins:
            coin_data = await get_coin_data(coin.name)
            if coin_data['code'] == '0' and coin_data['data']:
                price_data = coin_data['data'][0]
                current_price = float(price_data['last'])
                new_price = CoinPrice(
                    coin_id=coin.id,
                    price=current_price,
                )
                session.add(new_price)
                await check_alerts_and_send_emails(session, coin, current_price)
        await session.commit()


async def periodic_message():
    while True:
        await update_prices()
        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Background task starts at statrup."""
    asyncio.create_task(periodic_message())
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


async def get_coins_data(request: Request, db: AsyncSession) -> list:
    coins_data = []
    coins_result = await db.execute(select(Coin).order_by(Coin.name))
    coins = coins_result.scalars().all()
    for coin in coins:
        price_result = await db.execute(
            select(CoinPrice)
            .where(CoinPrice.coin_id == coin.id)
            .order_by(CoinPrice.timedate.desc())
            .limit(1)
        )
        price = price_result.scalars().first()
        coin_data = {
            "name": coin.name,
            "price": price.price if price else "No Price"
        }
        coins_data.append(coin_data)
    return coins_data


async def get_all_coins(db):
    result = await db.execute(select(Coin).order_by(Coin.name))
    return result.scalars().all()


@app.post("/add-coin")
async def add_coin(request: Request, name: str = Form(), db: AsyncSession = Depends(get_session)):
    coin_exists = await db.execute(select(Coin).filter(Coin.name == name.upper()))
    coin_in_db = coin_exists.scalars().first() is not None
    coin_on_exchange = await check_coin_name(name)
    if coin_in_db:
        message = "Монета с таким именем уже существует в базе данных!"
    elif not coin_on_exchange:
        message = "Монета не найдена на бирже!"
    else:
        new_coin = Coin(name=name)
        db.add(new_coin)
        await db.commit()
        message = "Монета успешно добавлена!"

    coins_data = await get_coins_data(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "coins": coins_data, "message": message})


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: AsyncSession = Depends(get_session)):
    coins_data = await get_coins_data(request, db)
    return templates.TemplateResponse("index.html", {"request": request, "coins": coins_data})


if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)