"""Authentication endpoints (login, register, refresh token)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.

    TODO: Implement actual database user creation
    """
    # Placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User registration not yet implemented"
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    """
    Authenticate user and return JWT tokens.

    TODO: Implement actual database user lookup and validation
    """
    # Placeholder implementation
    # In production, look up user in database and verify password

    # For now, create a dummy token
    user_id = "test-user-123"  # Replace with actual user ID from DB

    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user_id,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    refresh_token: str,
) -> LoginResponse:
    """
    Refresh access token using refresh token.

    TODO: Implement refresh token validation and rotation
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )
