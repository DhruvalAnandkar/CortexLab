"""
Artifact Model

Represents generated artifacts like reports, deep-dives, and paper drafts.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project


class Artifact(Base):
    """Generated artifact model (reports, papers, etc.)."""
    
    __tablename__ = "artifacts"
    
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
    artifact_type: Mapped[str] = mapped_column(
        String(50)  # trend_report, gap_analysis, deep_dive_report, experiment_plan, paper_draft
    )
    title: Mapped[str] = mapped_column(String(500))
    content_markdown: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="artifacts")
    
    def __repr__(self) -> str:
        return f"<Artifact {self.artifact_type}: {self.title}>"
