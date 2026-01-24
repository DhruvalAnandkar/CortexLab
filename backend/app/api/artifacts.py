"""
Artifacts API Routes

CRUD operations for generated artifacts (reports, papers).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models import User, Project, Artifact, Source
from app.schemas import (
    ArtifactCreate,
    ArtifactUpdate,
    ArtifactReviseRequest,
    ArtifactResponse,
    ArtifactListResponse,
    SourceResponse,
    SourceListResponse,
)

router = APIRouter()


@router.get("/projects/{project_id}/artifacts", response_model=ArtifactListResponse)
async def list_artifacts(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all artifacts for a project."""
    # Verify project ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(
        select(Artifact)
        .where(Artifact.project_id == project_id)
        .order_by(Artifact.created_at.desc())
    )
    artifacts = result.scalars().all()
    
    return ArtifactListResponse(
        artifacts=[ArtifactResponse.model_validate(a) for a in artifacts],
        total=len(artifacts)
    )


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get an artifact by ID."""
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id)
    )
    artifact = result.scalar_one_or_none()
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Verify ownership through project
    project_result = await db.execute(
        select(Project)
        .where(Project.id == artifact.project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return ArtifactResponse.model_validate(artifact)


@router.put("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(
    artifact_id: str,
    artifact_data: ArtifactUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an artifact (manual edits)."""
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id)
    )
    artifact = result.scalar_one_or_none()
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Verify ownership through project
    project_result = await db.execute(
        select(Project)
        .where(Project.id == artifact.project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Update fields
    if artifact_data.title is not None:
        artifact.title = artifact_data.title
    if artifact_data.content_markdown is not None:
        artifact.content_markdown = artifact_data.content_markdown
        artifact.version += 1
    
    return ArtifactResponse.model_validate(artifact)


@router.post("/artifacts/{artifact_id}/revise", response_model=ArtifactResponse)
async def revise_artifact(
    artifact_id: str,
    request: ArtifactReviseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Request AI revision of an artifact.
    
    Uses AI to revise the artifact based on user instructions.
    """
    result = await db.execute(
        select(Artifact).where(Artifact.id == artifact_id)
    )
    artifact = result.scalar_one_or_none()
    
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Verify ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == artifact.project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # TODO: Implement AI revision using Paper Editor agent
    # For now, just return the artifact unchanged
    
    return ArtifactResponse.model_validate(artifact)


@router.get("/projects/{project_id}/sources", response_model=SourceListResponse)
async def list_sources(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all sources/papers referenced in a project."""
    # Verify project ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(
        select(Source)
        .where(Source.project_id == project_id)
        .order_by(Source.accessed_at.desc())
    )
    sources = result.scalars().all()
    
    return SourceListResponse(
        sources=[SourceResponse.model_validate(s) for s in sources],
        total=len(sources)
    )
