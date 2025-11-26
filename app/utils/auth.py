from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.model.user import User
from app.database.database import get_async_db
from app.utils.jwt import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    Extract JWT token from Authorization header and return authenticated user.

    HTTPBearer() automatically:
    1. Looks for 'Authorization' header
    2. Validates it starts with 'Bearer '
    3. Extracts the token part
    4. Passes it to credentials.credentials
    """
    token = credentials.credentials
    # Verify the token
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
