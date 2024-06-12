"""Module with Alert API views."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.coin_api import get_coin, get_current_coin_price
from api_models.alert_models import (AlertCreate, AlertRead, AlertsRead,
                                     AlertUpdate)
from models import Alert, Coin
from utils.db_utils import get_session

router = APIRouter()


async def get_alert(alert_id: UUID, db: AsyncSession) -> Alert:
    """Get Alert by id.

    Args:
        alert_id: UUID - Alert id.
        db: AsyncSession - db session.

    Raises:
        HTTPException: when alert is not found.

    Returns:
        Alert: founded Alert object.
    """
    query = await db.execute(select(Alert).filter(Alert.id == alert_id))
    alert: Alert = query.scalar()
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Уведомление не найдено!')
    return alert


async def get_coin_data_from_alert(
    alert: UUID | Alert,
    db: AsyncSession,
) -> tuple[Alert, Coin, float]:
    """Get data about alert coin.

    Args:
        alert: UUID | Alert - Alert or Alert id.
        db: AsyncSession - db session.

    Returns:
        tuple[Alert, Coin, float]: founded alert, founded coin and coin current price.
    """
    if not isinstance(alert, (Alert, AlertCreate)):
        alert = await get_alert(alert, db)
    coin = await get_coin(alert.coin_id, db)
    current_price = await get_current_coin_price(coin.name, db)
    return alert, coin, current_price


@router.get('/alerts', response_model=AlertsRead)
async def get_alerts(db: AsyncSession = Depends(get_session)) -> AlertsRead:
    """Get all alerts.

    Args:
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Returns:
        AlertsRead: Pydantic model with fields for read.
    """
    query = await db.execute(select(Alert))
    alerts = query.scalars().all()
    alerts_list = []
    for alert in alerts:
        alerts_list.append(
            AlertRead(
                id=alert.id,
                alert_type=alert.alert_type,
                coin_id=alert.coin_id,
                email=alert.email,
                threshold_price=alert.threshold_price,
            ),
        )
    return AlertsRead(alerts=alerts_list)


@router.post('/alerts', response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: AlertCreate, db: AsyncSession = Depends(get_session)) -> AlertRead:
    """Create new alert.

    Args:
        alert: AlertCreate - Pydantic model with fields for create.
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Raises:
        HTTPException: on error creating alert.

    Returns:
        AlertRead: Pydantic model with fields for read.
    """
    _, coin, current_price = await get_coin_data_from_alert(alert, db)
    alert_type = 'inc' if alert.threshold_price > current_price else 'dec'
    new_alert = Alert(
        email=alert.email,
        coin_id=coin.id,
        threshold_price=alert.threshold_price,
        alert_type=alert_type,
    )
    db.add(new_alert)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Такая подписка уже оформлена!')
    await db.refresh(new_alert)
    return AlertRead(
        id=new_alert.id,
        alert_type=new_alert.alert_type,
        coin_id=new_alert.coin_id,
        email=new_alert.email,
        threshold_price=new_alert.threshold_price,
    )


@router.delete('/alerts/{alert_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert_id: UUID, db: AsyncSession = Depends(get_session)) -> Response:
    """Delete alert by id.

    Args:
        alert_id: UUID - Alert id.
        db: AsyncSession, optional - db session. Defaults to Depends(get_session).

    Returns:
        Response: _description_
    """
    alert = await get_alert(alert_id, db)
    await db.delete(alert)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/alerts/{alert_id}', response_model=AlertRead, status_code=status.HTTP_200_OK)
async def update_alert(
    alert_id: UUID,
    alert_data: AlertUpdate,
    db: AsyncSession = Depends(get_session),
) -> AlertRead:
    """Update alert by id.

    Args:
        alert_id: UUID - Id of alert for update.
        alert_data: AlertUpdate - Pydantic model with fields for update alert.
        db: AsyncSession, optional - db sesison. Defaults to Depends(get_session).

    Raises:
        HTTPException: on error updating alert.

    Returns:
        AlertRead: Pydantic model with fields for read.
    """
    alert, _, current_price = await get_coin_data_from_alert(alert_id, db)
    if alert_data.threshold_price:
        alert_type = 'inc' if alert_data.threshold_price > current_price else 'dec'
        alert.alert_type = alert_type
        alert.threshold_price = alert_data.threshold_price
    if alert_data.email:
        alert.email = alert_data.email
    if alert_data.coin_id:
        alert.coin_id = alert_data.coin_id
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            'Ошибка обновления уведомления. Возможно, монеты с таким id нет.',
        )
    await db.refresh(alert)
    return AlertRead(
        id=alert.id,
        alert_type=alert.alert_type,
        coin_id=alert.coin_id,
        email=alert.email,
        threshold_price=alert.threshold_price,
    )
