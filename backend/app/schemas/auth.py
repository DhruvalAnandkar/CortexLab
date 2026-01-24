"""
Authentication Schemas

Pydantic models for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth authentication."""
    id_token: str


class UserResponse(BaseModel):
    """User data response."""
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response with session token."""
    user: UserResponse
    session_token: str


class SessionValidation(BaseModel):
    """Session validation response."""
    valid: bool
    user: Optional[UserResponse] = None
