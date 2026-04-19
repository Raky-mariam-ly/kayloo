"""
Custom JWT refresh token flow for mobile clients.

Flow:
  1. POST /auth/jwt/login   → { access_token }  + refresh_token in response body
  2. POST /auth/jwt/refresh  → { access_token }  (send refresh_token to get a new access token)
  3. POST /auth/jwt/logout   → revokes the refresh token
"""
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import (
    JWT_ACCESS_LIFETIME,
    JWT_REFRESH_LIFETIME,
    RefreshToken,
    User,
    UserManager,
    get_bearer_jwt_strategy,
    get_user_db,
    get_user_manager,
)
from core.db import get_db

router = APIRouter(tags=["auth"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_ACCESS_LIFETIME


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = JWT_ACCESS_LIFETIME


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _create_refresh_token(session: AsyncSession, user_id) -> str:
    token_value = secrets.token_urlsafe(64)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=JWT_REFRESH_LIFETIME)
    refresh = RefreshToken(id=token_value, user_id=user_id, expires_at=expires_at)
    session.add(refresh)
    await session.commit()
    return token_value


async def _create_access_token(user: User) -> str:
    strategy = get_bearer_jwt_strategy()
    return await strategy.write_token(user)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/auth/jwt/login", response_model=TokenResponse)
async def jwt_login(
    email: str = "",
    password: str = "",
    session: AsyncSession = Depends(get_db),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Authenticate and return both access + refresh tokens."""
    from fastapi.security import OAuth2PasswordRequestForm

    user = await user_manager.authenticate(
        OAuth2PasswordRequestForm(username=email, password=password),
    )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = await _create_access_token(user)
    refresh_token = await _create_refresh_token(session, user.id)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/jwt/refresh", response_model=RefreshResponse)
async def jwt_refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_db),
    user_manager: UserManager = Depends(get_user_manager),
):
    """Exchange a valid refresh token for a new access token."""
    result = await session.execute(
        select(RefreshToken).filter_by(id=body.refresh_token)
    )
    token = result.scalar_one_or_none()

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await session.execute(delete(RefreshToken).filter_by(id=token.id))
        await session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    user = await user_manager.get(token.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = await _create_access_token(user)
    return RefreshResponse(access_token=access_token)


@router.post("/auth/jwt/logout", status_code=status.HTTP_204_NO_CONTENT)
async def jwt_logout(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_db),
):
    """Revoke a refresh token (logout from device)."""
    await session.execute(delete(RefreshToken).filter_by(id=body.refresh_token))
    await session.commit()
