import asyncio

from app.seeders.alerts_seeder import seed_alerts
from .user_seeder import seed_users


async def run_all_seeders():
    print("Seeding started...")
    # await seed_users()
    await seed_alerts()
    print("Seeding finished!")

if __name__ == "__main__":
    asyncio.run(run_all_seeders())
