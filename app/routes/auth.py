from fastapi import APIRouter, HTTPException, status
from app.schemas.auth_schemas import LoginRequest, TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):

    print(login_request.email)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
