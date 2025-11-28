

from hmac import new
from certifi import where
from httpx import delete
from sqlalchemy import func, select

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

    async def get_alerts_set(self, from_id: int, limit: int):
        """
        Cursor-based pagination using ID range.

        Args:
            user_id: User ID to filter alerts
            from_id: Starting alert ID (cursor position)
            limit: Number of records to fetch

        Returns:
            List of alert dictionaries in the ID range [from_id, from_id + limit)
        """
        to_id = from_id + limit

        result = await self.db_session.execute(
            select(Alerts)
            .where(
                Alerts.id >= from_id,
                Alerts.id < to_id
            )
            .order_by(Alerts.id.asc())
        )
        alerts = result.scalars().all()
        return [alert.to_dict() for alert in alerts]

    async def get_min_max_alert_ids(self):
        """
        Get minimum and maximum alert IDs for a user.

        Args:
            user_id: User ID to filter alerts

        Returns:
            Tuple of (min_id, max_id)
        """
        result = await self.db_session.execute(
            select(
                func.min(Alerts.id).label('min_id'),
                func.max(Alerts.id).label('max_id')
            )
        )
        row = result.first()
        if row and row.min_id and row.max_id:
            return row.min_id, row.max_id
        return None, None
