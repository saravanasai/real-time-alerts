from app.model.user import User
from app.database.database import AsyncSessionLocal


async def seed_users():
    async with AsyncSessionLocal() as session:

        user1 = User(
            email="john@example.com",
            name="John Doe",
            password="hashedpassword123"
        )
        user2 = User(
            email="jane@example.com",
            name="Jane Doe",
            password="hashedpassword456"
        )

        session.add(user1)
        session.add(user2)

        await session.commit()

        print("Users seeded successfully!")
