"""
FastAPI Dependencies

Shared dependencies for authentication and database access.
"""

from fastapi import Depends, HTTPException, Cookie, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_session_token
from app.models import User


async def get_current_user(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that returns the currently authenticated user.

    Accepts the session token from:
    1. httpOnly cookie `session_token` (preferred — set by the /auth/google endpoint)
    2. Authorization header `Bearer <token>` (fallback — used by frontend localStorage flow)

    Raises HTTPException if not authenticated.
    """
    token = session_token

    # Fall back to Authorization header if no cookie
    if not token and authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and value:
            token = value

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = verify_session_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def get_optional_user(
    session_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency that returns the currently authenticated user if present.
    
    Returns None if not authenticated (doesn't raise exception).
    """
    if not session_token:
        return None
    
    user_id = verify_session_token(session_token)
    if not user_id:
        return None
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
