from fastapi import APIRouter, HTTPException, status
from ..schemas import alerts_sehemas
from ..config import Config
from typing import List

router = APIRouter()

alerts = [
    {'id': 1, 'user_id': 1, 'alert_price': '2000', 'metal_type': 'gold'},
    {'id': 2, 'user_id': 1, 'alert_price': '2500', 'metal_type': 'silver'},
    {'id': 3, 'user_id': 2, 'alert_price': '1800', 'metal_type': 'gold'},
    {'id': 4, 'user_id': 2, 'alert_price': '3000', 'metal_type': 'platinum'},
    {'id': 5, 'user_id': 3, 'alert_price': '2200', 'metal_type': 'gold'},
    {'id': 6, 'user_id': 3, 'alert_price': '2800', 'metal_type': 'silver'},
    {'id': 7, 'user_id': 1, 'alert_price': '3200', 'metal_type': 'platinum'},
    {'id': 8, 'user_id': 4, 'alert_price': '1900', 'metal_type': 'gold'},
    {'id': 9, 'user_id': 4, 'alert_price': '2600', 'metal_type': 'silver'},
    {'id': 10, 'user_id': 5, 'alert_price': '3500', 'metal_type': 'platinum'},
]


@router.get("/alerts")
async def get_alerts(skip: int = 0, limit: int = 10):
    data = alerts[skip:skip+limit]
    return {"count": len(data), "data": data}


@router.post("/alerts", status_code=status.HTTP_201_CREATED, response_model=alerts_sehemas.AlertResponseFormatter)
async def store_alerts_bulk(alerts_list: List[alerts_sehemas.Alert]):
    created_alerts = []

    for alert in alerts_list:
        new_alert = {
            "id": len(alerts) + 1,
            "user_id": alert.user_id,
            "alert_price": alert.alert_price,
            "metal_type": alert.metal_type
        }
        alerts.append(new_alert)
        created_alerts.append(new_alert)

    return {"count": len(created_alerts), "data": created_alerts}


@router.get("/alerts/{id}")
async def get_alert(id: int):
    for alert in alerts:
        if alert['id'] == id:
            return {"data": alert}

    raise HTTPException(status_code=404, detail="Alert not found")


@router.delete("/alerts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(id: int):
    if id > len(alerts) or id < 1:
        raise HTTPException(status_code=404, detail="Alert not found")

    del alerts[id-1]
