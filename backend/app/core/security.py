"""
Security Utilities

Session token generation and verification using itsdangerous.
"""

from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.config import get_settings


settings = get_settings()

# Session token serializer
serializer = URLSafeTimedSerializer(settings.session_secret_key)


def create_session_token(user_id: str) -> str:
    """
    Create a signed session token for a user.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        A signed session token string
    """
    return serializer.dumps({"user_id": user_id, "created": datetime.utcnow().isoformat()})


def verify_session_token(token: str, max_age: int = 86400 * 7) -> Optional[str]:
    """
    Verify a session token and return the user_id.
    
    Args:
        token: The session token to verify
        max_age: Maximum age of token in seconds (default: 7 days)
        
    Returns:
        The user_id if valid, None otherwise
    """
    try:
        data = serializer.loads(token, max_age=max_age)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_string(value: str) -> str:
    """Create a SHA-256 hash of a string."""
    return hashlib.sha256(value.encode()).hexdigest()
