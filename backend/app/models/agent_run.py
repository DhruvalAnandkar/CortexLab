"""
Agent Run Model

Represents an execution of the agent workflow.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.run_event import RunEvent


class AgentRun(Base):
    """Agent workflow run model."""
    
    __tablename__ = "agent_runs"
    
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
    run_type: Mapped[str] = mapped_column(
        String(50)  # discovery, deep_dive, paper
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"  # pending, running, completed, failed
    )
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="agent_runs")
    events: Mapped[list["RunEvent"]] = relationship(
        "RunEvent",
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="RunEvent.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<AgentRun {self.run_type} - {self.status}>"
