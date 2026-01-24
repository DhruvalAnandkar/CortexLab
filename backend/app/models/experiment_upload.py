"""
Experiment Upload Model

Represents uploaded experiment data files.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class ExperimentUpload(Base):
    """Uploaded experiment file model."""
    
    __tablename__ = "experiment_uploads"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True
    )
    file_path: Mapped[str] = mapped_column(String(1000))
    file_type: Mapped[str] = mapped_column(
        String(50)  # csv, json, png, jpg, pdf
    )
    original_name: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="experiment_uploads")
    
    def __repr__(self) -> str:
        return f"<ExperimentUpload {self.original_name}>"
