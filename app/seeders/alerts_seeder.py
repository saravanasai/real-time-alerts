import random
from app.model.alerts import Alerts
from app.database.database import AsyncSessionLocal


async def seed_alerts():
    async with AsyncSessionLocal() as session:

        metal_types = ["gold", "silver"]

        for _ in range(200):
            alert = Alerts(
                alert_price=random.randint(1000, 5000),
                user_id=random.randint(12, 14),
                metal_type=random.choice(metal_types)
            )
            session.add(alert)

        await session.commit()

        print("200 alerts seeded successfully!")
