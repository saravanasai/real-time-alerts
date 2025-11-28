import json
from fastapi import APIRouter, Depends, HTTPException, status


from app.service.alert_service import AlertService
from app.utils.auth import get_current_user
from app.database.database import get_async_db, get_cache
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas import alerts_sehemas
from typing import List

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)

# auhorization policys


async def authorize_alert_access(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    user=Depends(get_current_user)
):
    alert_service_instance = AlertService(db)
    alert = await alert_service_instance.get_alert_by_id(id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Check if the alert belongs to the current user
    if alert.get("user_id") != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this alert"
        )

    return alert


@router.get("/alerts")
async def get_alerts(skip: int = 0, limit: int = 10,
                     db: AsyncSession = Depends(get_async_db),
                     user=Depends(get_current_user)
                     ):
    alert_service_instance = AlertService(db)
    alerts = await alert_service_instance.get_alerts(user.id, skip=skip, limit=limit)

    return {"count": len(alerts), "data": alerts}


@router.post("/alerts", status_code=status.HTTP_201_CREATED, response_model=alerts_sehemas.AlertResponseFormatter)
async def store_alert(new_alert: alerts_sehemas.Alert, db=Depends(get_async_db)):

    alert_service_instance = AlertService(db)
    alert = await alert_service_instance.create_alert(new_alert.dict())

    return {"data": alert}


@router.get("/alerts/{id}")
async def get_alert(alert=Depends(authorize_alert_access)):
    return {"data": alert}


@router.delete("/alerts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(alert=Depends(authorize_alert_access), db: AsyncSession = Depends(get_async_db)):
    alert_service_instance = AlertService(db)
    await alert_service_instance.delete_alert(alert.get("id"))
    return None


@router.post("/alerts-set")
async def cache_all_alerts_to_redis(db: AsyncSession = Depends(get_async_db)):
    """
    Cache all alerts to Redis ZSET organized by metal type.

    Structure:
    - Key: alerts:gold
    - Key: alerts:silver  
    - Score: alert_price
    - Member: JSON {"id": 204, "user_id": 14, "alert_price": 2710, "metal_type": "gold"}
    """
    cache = await get_cache()
    alert_service = AlertService(db)
    chunk_size = 100

    # Get min and max alert IDs
    min_id, max_id = await alert_service.get_min_max_alert_ids()

    if min_id is None or max_id is None:
        return {"success": True, "message": "No alerts found"}

    # Clear existing data
    await cache.delete("alerts:gold")
    await cache.delete("alerts:silver")

    # Process alerts in chunks
    current_id = min_id

    while current_id <= max_id:
        alerts = await alert_service.get_alerts_set(current_id, chunk_size)

        if not alerts:
            break

        # Group by metal type
        gold_mapping = {}
        silver_mapping = {}

        for alert in alerts:
            alert_data = {
                "id": alert['id'],
                "user_id": alert['user_id'],
                "alert_price": alert['alert_price'],
                "metal_type": alert['metal_type']
            }

            score = float(alert['alert_price'])
            member = json.dumps(alert_data)

            metal_type = alert['metal_type'].lower()
            if metal_type == 'gold':
                gold_mapping[member] = score
            elif metal_type == 'silver':
                silver_mapping[member] = score

        # Add to Redis
        if gold_mapping:
            await cache.zadd("alerts:gold", gold_mapping)

        if silver_mapping:
            await cache.zadd("alerts:silver", silver_mapping)

        # Move cursor
        last_alert_id = alerts[-1]['id']
        current_id = last_alert_id + 1

        if len(alerts) < chunk_size:
            break

    return {"success": True, "message": "Alerts cached to Redis"}
