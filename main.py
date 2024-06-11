"""FastAPI app for crypto alerts."""

import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import (Depends, FastAPI, Form, HTTPException, Request, responses,
                     templating)
from sqlalchemy import Sequence, exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from api import alert_api, coin_api, coin_utils
from constants import APP_HOST, APP_PORT
from db_utils import get_session
from email_utils import send_email
from models import Alert, Coin, CoinPrice
from validators import check_coin_name

alert_router = alert_api.router
coin_router = coin_api.router


async def check_alerts_and_send_emails(
    db: AsyncSession,
    coin: Coin,
    current_price: float,
) -> AsyncSession:
    """Alerts check and send emails if price reached expected value.

    Args:
        db: AsyncSession - db session.
        coin: Coin - coin for price update.
        current_price: float - current coin price.

    Returns:
        AsyncSession: updated db session.
    """
    alerts = await db.execute(
        select(Alert).where(Alert.coin_id == coin.id),
    )
    alerts = alerts.scalars().all()
    for alert in alerts:
        increment = alert.alert_type == 'inc' and current_price >= alert.threshold_price
        decrement = alert.alert_type == 'dec' and current_price <= alert.threshold_price
        if (increment or decrement):
            email_body = f"""Спешим сообщить!
Цена {coin.name} достигла {current_price}.
Вы получили это сообщение потому что подписались на обновление цены до {alert.threshold_price}.
            """
            await send_email(
                'Ваша цена!',
                alert.email,
                email_body,
            )
            await db.delete(alert)
    return db


async def update_price_for_coin(coin: Coin) -> None:
    """Get new price for coin.

    Args:
        coin: Coin - coin for price update.
    """
    async for session in get_session():
        coin_data = await coin_utils.get_coin_data(coin.name)
        if coin_data['code'] == '0' and coin_data['data']:
            price_data = coin_data['data'][0]
            current_price = float(price_data['last'])
            new_price = CoinPrice(
                coin_id=coin.id,
                price=current_price,
            )
            session.add(new_price)
            session = await check_alerts_and_send_emails(session, coin, current_price)
        await session.commit()


async def update_prices() -> None:
    """Update prices for all coins."""
    async for session in get_session():
        coins = await session.execute(select(Coin))
        coins = coins.scalars().all()
    tasks = [update_price_for_coin(coin) for coin in coins]
    await asyncio.gather(*tasks)


async def periodic_function() -> None:
    """Infinite loop for update prices."""
    infinite = True
    while infinite:
        await update_prices()
        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Background task starts at statrup.

    Args:
        app: FastAPI - FasrAPI app instance.

    Yields:
        None
    """
    asyncio.create_task(periodic_function())
    yield


app = FastAPI(lifespan=lifespan)
templates = templating.Jinja2Templates(directory='templates')


async def get_coins_data(db: AsyncSession) -> list[dict]:
    """Get coins names and prices.

    Args:
        db: AsyncSession - db session.

    Returns:
        list[dict]: list of dicts with coin name and price.
    """
    coins_data = []
    coins_result = await db.execute(select(Coin).order_by(Coin.name))
    coins = coins_result.scalars().all()
    for coin in coins:
        price_result = await db.execute(
            select(
                CoinPrice,
            ).where(
                CoinPrice.coin_id == coin.id,
            ).order_by(
                CoinPrice.timedate.desc(),
            ).limit(1),
        )
        price = price_result.scalars().first()
        coin_data = {
            'name': coin.name,
            'price': price.price if price else 'No Price',
        }
        coins_data.append(coin_data)
    return coins_data


async def get_all_coins(db: AsyncSession) -> Sequence[Coin]:
    """Get all Coin objects.

    Args:
        db: AsyncSession - db session.

    Returns:
        Sequence[Coin]: All Coins.
    """
    query = await db.execute(select(Coin).order_by(Coin.name))
    return query.scalars().all()


@app.get('/', response_class=responses.HTMLResponse)
async def root(
    request: Request,
    db: AsyncSession = Depends(get_session),
    messages: dict = None,
) -> templating.Jinja2Templates.TemplateResponse:
    """View for main page.

    Args:
        request: Request - user request.
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).
        messages: dict, optional - messages (errors, info) for print in fields. Defaults to None.

    Returns:
        TemplateResponse: rendered template.
    """
    coins_data = await get_coins_data(db)
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'coins': coins_data,
            'messages': messages,
        },
    )


@app.post('/subscribe')
async def subscribe(
    request: Request,
    email: str = Form(),
    coin: str = Form(),
    threshold_price: float = Form(),
    db: AsyncSession = Depends(get_session),
) -> templating.Jinja2Templates.TemplateResponse:
    """View for a subscription.

    Args:
        request: Request - user request.
        email: str, optional - email from form field. Defaults to Form().
        coin: str, optional - coin name from form field . Defaults to Form().
        threshold_price: float, optional - threshold price from form field. Defaults to Form().
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Returns:
        templating.Jinja2Templates.TemplateResponse: rendered main page.
    """
    subscribe_message_literal = 'subscribe_message'
    coin_obj = await db.execute(select(Coin).filter(Coin.name == coin.upper()))
    coin_obj = coin_obj.scalars().first()
    messages = False
    if not coin_obj:
        messages = {subscribe_message_literal: 'Монета не найдена'}
    try:
        current_price = await coin_api.get_current_coin_price(coin, db)
    except HTTPException:
        messages = {subscribe_message_literal: 'Не удалось получить цену монеты.'}
    if threshold_price < 0:
        messages = {subscribe_message_literal: 'Цена не может быть отрицательной'}
    if not messages:
        alert_type = 'inc' if threshold_price > current_price else 'dec'
        new_alert = Alert(
            email=email,
            coin_id=coin_obj.id,
            threshold_price=threshold_price,
            alert_type=alert_type,
        )
        db.add(new_alert)
        try:
            await db.commit()
        except exc.IntegrityError:
            messages = {subscribe_message_literal: 'Такая подписка уже оформлена!'}
            await db.rollback()
        else:
            messages = {subscribe_message_literal: 'Подписка оформлена успешно'}
    return await root(request, db, messages)


@app.post('/add-coin')
async def add_coin(
    request: Request,
    name: str = Form(),
    db: AsyncSession = Depends(get_session),
) -> templating.Jinja2Templates.TemplateResponse:
    """View for adding a coin.

    Args:
        request: Request - user request.
        name: str, optional - coin name. Defaults to Form().
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Returns:
        templating.Jinja2Templates.TemplateResponse: rendered main page.
    """
    coin_exists = await db.execute(select(Coin).filter(Coin.name == name.upper()))
    coin_in_db = coin_exists.scalars().first() is not None
    coin_on_exchange = await check_coin_name(name)
    if not coin_in_db and coin_on_exchange:
        new_coin = Coin(name=name)
        db.add(new_coin)
        await db.commit()
        messages = {'add_message': 'Монета успешно добавлена!'}
    elif coin_in_db:
        messages = {'add_message': 'Монета с таким именем уже существует в базе данных!'}
    else:
        messages = {'add_message': 'Монета не найдена на бирже!'}
    return await root(request, db, messages)


app.include_router(alert_router)
app.include_router(coin_router)


if __name__ == '__main__':
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
