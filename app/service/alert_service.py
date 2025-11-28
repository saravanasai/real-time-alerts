

from hmac import new
from certifi import where
from httpx import delete
from sqlalchemy import select

from app.model import user
from app.model.alerts import Alerts


class AlertService:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_alerts(self, user_id: int, skip: int = 0, limit: int = 10):
        result = await self.db_session.execute(select(Alerts).where(Alerts.user_id == user_id).offset(skip).limit(limit))
        alerts = result.scalars().all()
        alerts_dict = [alert.to_dict() for alert in alerts]
        return alerts_dict

    async def get_alert_by_id(self, alert_id: int):
        result = await self.db_session.execute(select(Alerts).where(Alerts.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            return alert.to_dict()
        return None

    async def create_alert(self, alert_data: dict):
        new_alert = Alerts()
        new_alert.user_id = alert_data['user_id']
        new_alert.alert_price = alert_data['alert_price']
        new_alert.metal_type = alert_data['metal_type']

        self.db_session.add(new_alert)
        await self.db_session.commit()
        await self.db_session.refresh(new_alert)
        return new_alert.to_dict()

    async def delete_alert(self, alert_id: int):
        result = await self.db_session.execute(select(Alerts).where(Alerts.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            await self.db_session.delete(alert)
            await self.db_session.commit()
            return True
        return False
