from fastapi import APIRouter, Depends, HTTPException, status

from app.service import alert_service
from app.service.alert_service import AlertService
from app.utils.auth import get_current_user
from app.database.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import alerts_sehemas
from typing import List

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/alerts")
async def get_alerts(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_async_db)):
    alert_service_instance = AlertService(db)
    alerts = await alert_service_instance.get_alerts(skip=skip, limit=limit)

    return {"count": len(alerts), "data": alerts}


@router.post("/alerts", status_code=status.HTTP_201_CREATED, response_model=alerts_sehemas.AlertResponseFormatter)
async def store_alert(new_alert: alerts_sehemas.Alert, db=Depends(get_async_db)):

    alert_service_instance = AlertService(db)
    alert = await alert_service_instance.create_alert(new_alert.dict())

    return {"data": alert}


@router.get("/alerts/{id}")
async def get_alert(id: int, db: AsyncSession = Depends(get_async_db)):

    alert_service_instance = AlertService(db)
    alert = await alert_service_instance.get_alert_by_id(id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {"data": alert}


@router.delete("/alerts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(id: int, db: AsyncSession = Depends(get_async_db)):
    alert_service_instance = AlertService(db)
    alert = await alert_service_instance.delete_alert(id)

    if alert is False:
        raise HTTPException(status_code=404, detail="Alert not found")
    return None
