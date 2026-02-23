"""
Experiments API Routes

File upload and management for experiment data.
"""

import os
import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.config import get_settings
from app.dependencies import get_current_user
from app.models import User, Project, ExperimentUpload
from app.schemas import ExperimentUploadResponse, ExperimentListResponse

router = APIRouter()
settings = get_settings()

# Allowed file types
ALLOWED_EXTENSIONS = {"csv", "json", "png", "jpg", "jpeg", "pdf", "xlsx", "txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def sanitize_filename(name: str) -> str:
    """Strip path separators and dangerous characters from a filename."""
    # Take only the basename (removes any directory traversal)
    name = os.path.basename(name)
    # Remove any remaining characters that aren't alphanumeric, dot, dash, underscore, or space
    name = re.sub(r"[^\w .\-]", "", name)
    return name[:255] or "file"  # max 255 chars, never empty


def _assert_safe_id(value: str, label: str = "ID") -> None:
    """Raise 400 if value is not a plain UUID (blocks path traversal via project_id)."""
    try:
        uuid.UUID(value)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail=f"Invalid {label}") from None


@router.post("/projects/{project_id}/experiments/upload", response_model=ExperimentUploadResponse)
async def upload_experiment(
    project_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an experiment data file.

    Supports CSV, JSON, images (PNG, JPG), PDF, and Excel files.
    """
    # Guard: project_id must be a valid UUID (prevents directory traversal)
    _assert_safe_id(project_id, "project ID")

    # Verify project ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Validate file extension
    file_ext = get_file_extension(file.filename or "")
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (read content to check)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Create project-specific upload directory
    project_upload_dir = os.path.join(settings.upload_dir, project_id)
    os.makedirs(project_upload_dir, exist_ok=True)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(project_upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create database record
    safe_name = sanitize_filename(file.filename or "upload")
    experiment = ExperimentUpload(
        project_id=project_id,
        file_path=file_path,
        file_type=file_ext,
        original_name=safe_name,
        description=description,
        meta={"size": len(content)},
    )
    db.add(experiment)
    await db.flush()
    
    return ExperimentUploadResponse.model_validate(experiment)


@router.get("/projects/{project_id}/experiments", response_model=ExperimentListResponse)
async def list_experiments(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all uploaded experiment files for a project."""
    # Verify project ownership
    project_result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(
        select(ExperimentUpload)
        .where(ExperimentUpload.project_id == project_id)
        .order_by(ExperimentUpload.created_at.desc())
    )
    experiments = result.scalars().all()
    
    return ExperimentListResponse(
        experiments=[ExperimentUploadResponse.model_validate(e) for e in experiments],
        total=len(experiments)
    )


@router.delete("/experiments/{experiment_id}")
async def delete_experiment(
    experiment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an uploaded experiment file."""
    result = await db.execute(
        select(ExperimentUpload).where(ExperimentUpload.id == experiment_id)
    )
    experiment = result.scalar_one_or_none()
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Verify ownership through project
    project_result = await db.execute(
        select(Project)
        .where(Project.id == experiment.project_id, Project.user_id == current_user.id)
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Delete file from disk
    if os.path.exists(experiment.file_path):
        os.remove(experiment.file_path)
    
    # Delete database record
    await db.delete(experiment)
    
    return {"message": "Experiment deleted successfully"}
