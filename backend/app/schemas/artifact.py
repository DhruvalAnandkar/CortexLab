"""
Artifact Schemas

Pydantic models for artifact requests and responses.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ArtifactCreate(BaseModel):
    """Request body for creating an artifact."""
    artifact_type: str
    title: str
    content_markdown: str


class ArtifactUpdate(BaseModel):
    """Request body for updating an artifact."""
    title: Optional[str] = None
    content_markdown: Optional[str] = None


class ArtifactReviseRequest(BaseModel):
    """Request to revise an artifact using AI."""
    instructions: str  # e.g., "Make it more concise", "Add more technical details"


class ArtifactResponse(BaseModel):
    """Artifact data response."""
    id: str
    project_id: str
    artifact_type: str
    title: str
    content_markdown: str
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArtifactListResponse(BaseModel):
    """List of artifacts response."""
    artifacts: List[ArtifactResponse]
    total: int


class SourceResponse(BaseModel):
    """Source/paper data response."""
    id: str
    provider: str
    external_id: Optional[str] = None
    title: str
    authors: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    citation_count: Optional[int] = None
    accessed_at: datetime
    
    class Config:
        from_attributes = True


class SourceListResponse(BaseModel):
    """List of sources response."""
    sources: List[SourceResponse]
    total: int


class ExperimentUploadResponse(BaseModel):
    """Experiment upload data response."""
    id: str
    file_type: str
    original_name: str
    description: Optional[str] = None
    meta: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ExperimentListResponse(BaseModel):
    """List of experiment uploads response."""
    experiments: List[ExperimentUploadResponse]
    total: int
