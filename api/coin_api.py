"""Module with Coin API views."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_models.coin_models import (CoinCreate, CoinPriceRead, CoinRead,
                                    CoinsRead, Price)
from models import Alert, Coin, CoinPrice
from utils.db_utils import get_session
from utils.validators import check_coin_name, validate_timestamps

router = APIRouter()


async def get_coin(coin_id: UUID, db: AsyncSession) -> Coin:
    """Get Coin by id.

    Args:
        coin_id: UUID - Coin id.
        db: AsyncSession - db session.

    Raises:
        HTTPException: when coin is not found in the database.

    Returns:
        Coin: Coin model object.
    """
    query = await db.execute(select(Coin).filter(Coin.id == coin_id))
    coin = query.scalars().first()
    if not coin:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Монета не найдена в базе данных!')
    return coin


async def get_current_coin_price(coin_name: str, db: AsyncSession) -> float:
    """Get last coin price from database.

    Args:
        coin_name: str - Name of coin.
        db : AsyncSession - db session.

    Raises:
        HTTPException: if cannot get coin price.

    Returns:
        float: coin price.
    """
    query = await db.execute(
        select(
            CoinPrice.price,
        ).join(
            Coin, Coin.id == CoinPrice.coin_id,
        ).where(
            Coin.name == coin_name.upper(),
        ).order_by(
            CoinPrice.timedate.desc(),
        ).limit(1),
    )
    price = query.scalars().first()
    if price:
        return price
    raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Не удалось получить текущую цену монеты')


async def get_coin_data_pretty(name: str, db: AsyncSession) -> tuple | str:
    """Get coin object and coin price.

    Args:
        name: str - coin name.
        db: AsyncSession - db session.

    Returns:
        tuple | str: coin data or error message.
    """
    coin = await db.execute(select(Coin).filter(Coin.name == name.upper()))
    coin = coin.scalars().first()
    if not coin:
        return 'Монета не найдена'
    try:
        current_price = await get_current_coin_price(name, db)
    except HTTPException:
        return 'Не удалось получить цену монеты.'
    return coin, current_price


@router.post('/coins/', response_model=CoinRead, status_code=status.HTTP_201_CREATED)
async def create_coin(coin: CoinCreate, db: AsyncSession = Depends(get_session)) -> CoinRead:
    """Create new Coin.

    Args:
        coin: CoinCreate - Pydantic model with fields for create.
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Raises:
        HTTPException: on creating error.

    Returns:
        CoinRead: Pydantic model with fields for read.
    """
    coin_exists = await db.execute(select(Coin).filter(Coin.name == coin.name.upper()))
    coin_in_db = coin_exists.scalars().first()
    if coin_in_db:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Монета с таким именем уже добавлена!')
    if not await check_coin_name(coin.name):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Монета не найдена на бирже!')
    db_coin = Coin(name=coin.name.upper())
    db.add(db_coin)
    await db.commit()
    await db.refresh(db_coin)
    return CoinRead(
        id=db_coin.id,
        name=db_coin.name,
    )


@router.get('/coins/', response_model=CoinsRead)
async def read_coins(db: AsyncSession = Depends(get_session)) -> CoinsRead:
    """Get list of all Coins.

    Args:
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Returns:
        CoinsRead: Pydantic model with fields for read.
    """
    query = await db.execute(select(Coin))
    coins = query.scalars().all()
    coins_list = []
    for coin in coins:
        coins_list.append(
            CoinRead(
                id=coin.id,
                name=coin.name,
            ),
        )
    return CoinsRead(coins=coins_list)


@router.get('/coins/{coin_id}', response_model=CoinPriceRead)
async def read_coin(
    coin_id: str,
    start_timestamp: float = None,
    end_timestamp: float = None,
    db: AsyncSession = Depends(get_session),
) -> CoinPriceRead:
    """Get all data about Coin.

    Args:
        coin_id: str - Coin id.
        start_timestamp: float - start timestamp for find prices. Defaults to None (5 minutes ago).
        end_timestamp: float - end timestamp for find prices. Defaults to None (now).
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Raises:
        HTTPException: when coin is not found in the database.

    Returns:
        CoinPriceRead: Pydantic model with fields for read coin data with prices.
    """
    try:
        UUID(coin_id)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Неверный id монеты')
    start_datetime, end_datetime = await validate_timestamps(start_timestamp, end_timestamp)
    coin = await get_coin(coin_id, db)
    query = await db.execute(
        select(CoinPrice).filter(
            CoinPrice.coin_id == coin_id,
            CoinPrice.timedate >= start_datetime,
            CoinPrice.timedate <= end_datetime,
        ),
    )
    prices = query.scalars().all()
    query = await db.execute(select(Alert).filter(Alert.coin_id == coin_id))
    alerts = query.scalars().all()
    alert_ids = [alert.id for alert in alerts]
    return CoinPriceRead(
        name=coin.name,
        alert_ids=alert_ids,
        prices=[Price(price=price.price, timedate=price.timedate) for price in prices],
    )
