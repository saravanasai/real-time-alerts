

from sqlalchemy import select

from app.model.alerts import Alerts


class AlertService:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_alerts(self, skip: int = 0, limit: int = 10):
        result = await self.db_session.execute(select(Alerts).offset(skip).limit(limit))
        alerts = result.scalars().all()
        alerts_dict = [alert.to_dict() for alert in alerts]
        return alerts_dict
