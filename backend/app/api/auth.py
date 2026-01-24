"""
Authentication API Routes

Handles Google OAuth authentication and session management.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Optional

from app.core.database import get_db
from app.core.security import create_session_token, verify_session_token
from app.config import get_settings
from app.models import User
from app.schemas import GoogleAuthRequest, AuthResponse, UserResponse

router = APIRouter()
settings = get_settings()


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    request: GoogleAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate with Google OAuth.
    
    Verifies the Google ID token and creates/retrieves the user account.
    Returns a session token stored in an httpOnly cookie.
    """
    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            request.id_token,
            requests.Request(),
            settings.google_client_id
        )
        
        # Extract user info from the token
        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name", email.split("@")[0])
        avatar_url = idinfo.get("picture")
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.google_id == google_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=avatar_url
        )
        db.add(user)
        await db.flush()
    else:
        # Update user info if changed
        user.name = name
        user.avatar_url = avatar_url
    
    # Create session token
    session_token = create_session_token(user.id)
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,  # Set to False for local development without HTTPS
        samesite="lax",
        max_age=86400 * 7  # 7 days
    )
    
    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url
        ),
        session_token=session_token
    )


@router.post("/logout")
async def logout(response: Response):
    """
    Logout the current user.
    
    Clears the session cookie.
    """
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    session_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user.
    
    Returns user info if the session is valid.
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
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url
    )
