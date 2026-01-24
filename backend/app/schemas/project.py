"""
Project Schemas

Pydantic models for project requests and responses.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProjectCreate(BaseModel):
    """Request body for creating a project."""
    title: str
    description: Optional[str] = None
    domain_tags: Optional[List[str]] = None


class ProjectUpdate(BaseModel):
    """Request body for updating a project."""
    title: Optional[str] = None
    description: Optional[str] = None
    domain_tags: Optional[List[str]] = None
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project data response."""
    id: str
    title: str
    description: Optional[str] = None
    domain_tags: Optional[dict] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """List of projects response."""
    projects: List[ProjectResponse]
    total: int


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with counts."""
    artifact_count: int = 0
    source_count: int = 0
    experiment_count: int = 0
