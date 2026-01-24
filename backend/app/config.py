"""
CortexLab Backend Configuration

Load environment variables and provide typed configuration settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./cortexlab.db",
        description="Database connection URL"
    )
    
    # Google OAuth
    google_client_id: str = Field(
        default="",
        description="Google OAuth Client ID"
    )
    
    # Gemini AI
    google_api_key: str = Field(
        default="",
        description="Google API Key for Gemini"
    )
    
    # Session
    session_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for signing session tokens"
    )
    
    # External APIs
    semantic_scholar_api_key: str = Field(
        default="",
        description="Semantic Scholar API key (optional)"
    )
    
    # File Storage
    upload_dir: str = Field(
        default="./uploads",
        description="Directory for uploaded files"
    )
    
    # CORS
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="Frontend URL for CORS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
