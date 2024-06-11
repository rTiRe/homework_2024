from fastapi import Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Coin, CoinPrice, Alert
from utils import check_coin_name, get_current_datetime, get_session
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timedelta

def get_five_min_ago_timestamp() -> float:
    return (get_current_datetime() - timedelta(minutes=5)).timestamp()

def get_now_timestamp() -> float:
    return get_current_datetime().timestamp()

router = APIRouter()

class CoinBase(BaseModel):
    name: str

class CoinCreate(CoinBase):
    pass

class CoinRead(BaseModel):
    id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    name: str

    class Config:
        json_encoders = {
            UUID: lambda x: str(x)
        }


class Price(BaseModel):
    price: float
    timedate: datetime

class CoinResponse(BaseModel):
    name: str
    alert_ids: list[UUID]
    prices: list[Price]


class CoinQuery(BaseModel):
    start_timestamp: Optional[float] = None
    end_timestamp: Optional[float] = None

    
    @field_validator('start_timestamp', 'end_timestamp')
    def validate_not_future(cls, value: Optional[float], info: ValidationInfo) -> Optional[float]:
        if value is not None:
            current_time = get_current_datetime().timestamp()
            if value > current_time:
                raise HTTPException(status_code=400, detail=f'{info.field_name} must not be in the future')
        return value

    @field_validator('end_timestamp')
    def validate_end_after_start(cls, value: Optional[int], info: ValidationInfo) -> Optional[int]:
        start_value = info.data.get('start_timestamp')
        if start_value is not None and value is not None:
            if value < start_value:
                raise HTTPException(status_code=400, detail='end_timestamp must be after start_timestamp')
        return value

    def convert_to_datetime(self):
        """Converts timestamp integers to datetime objects if provided, or sets default for last 5 minutes."""
        if self.end_timestamp is not None:
            self.end_timestamp = datetime.fromtimestamp(self.end_timestamp)
        else:
            self.end_timestamp = datetime.fromtimestamp(get_now_timestamp())
        if self.start_timestamp is not None:
            self.start_timestamp = datetime.fromtimestamp(self.start_timestamp)
        else:
            self.start_timestamp = datetime.fromtimestamp(get_five_min_ago_timestamp())


# CRUD операции
@router.post('/coins/', response_model=CoinRead)
async def create_coin(coin: CoinCreate, db: AsyncSession = Depends(get_session)):
    coin_exists = await db.execute(select(Coin).filter(Coin.name == coin.name.upper()))
    coin_in_db = coin_exists.scalars().first()
    if coin_in_db:
        raise HTTPException(status_code=400, detail='Монета с таким именем уже существует в базе данных!')
    if not await check_coin_name(coin.name):
        raise HTTPException(status_code=404, detail='Монета не найдена на бирже!')
    db_coin = Coin(name=coin.name.upper())
    db.add(db_coin)
    await db.commit()
    await db.refresh(db_coin)
    return db_coin

@router.get('/coins/')
async def read_coins(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Coin))
    coins = result.scalars().all()
    return coins


@router.get('/coins/{coin_id}', response_model=CoinResponse)
async def read_coin(coin_id: str, query: CoinQuery = Depends(CoinQuery), db: AsyncSession = Depends(get_session)) -> CoinResponse:
    query.convert_to_datetime()
    async with db as session:
        result = await session.execute(select(Coin).filter(Coin.id==coin_id))
        coin = result.scalars().first()
        if not coin:
            raise HTTPException(status_code=404, detail='Coin not found')
        result = await session.execute(
            select(CoinPrice)
            .filter(CoinPrice.coin_id==coin_id, CoinPrice.timedate>=query.start_timestamp, CoinPrice.timedate<=query.end_timestamp)
        )
        prices = result.scalars().all()
        result = await session.execute(select(Alert).filter(Alert.coin_id == coin_id))
        alerts = result.scalars().all()
        alert_ids = [alert.id for alert in alerts]
        response = CoinResponse(
            name=coin.name,
            alert_ids=alert_ids,
            prices=[Price(price=p.price, timedate=p.timedate) for p in prices]
        )
    return response