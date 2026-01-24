"""
FastAPI Dependencies

Shared dependencies for authentication and database access.
"""

from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.security import verify_session_token
from app.models import User


async def get_current_user(
    session_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that returns the currently authenticated user.
    
    Raises HTTPException if not authenticated.
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = verify_session_token(session_token)
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
