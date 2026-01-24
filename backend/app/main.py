"""
CortexLab Backend - FastAPI Application

Main entry point for the CortexLab Research Agent API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import get_settings
from app.core.database import init_db
from app.api import auth, projects, conversations, runs, artifacts, experiments, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    settings = get_settings()
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Initialize database
    await init_db()
    
    yield
    
    # Shutdown
    # Add cleanup logic here if needed


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="CortexLab API",
        description="AI-powered research assistant for discovering research gaps and generating papers",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
    app.include_router(conversations.router, prefix="/api", tags=["Conversations"])
    app.include_router(runs.router, prefix="/api", tags=["Agent Runs"])
    app.include_router(artifacts.router, prefix="/api", tags=["Artifacts"])
    app.include_router(experiments.router, prefix="/api", tags=["Experiments"])
    app.include_router(export.router, prefix="/api", tags=["Export"])
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
