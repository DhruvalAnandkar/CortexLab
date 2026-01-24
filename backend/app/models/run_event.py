"""
Run Event Model

Represents events that occur during an agent run (for SSE streaming).
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.agent_run import AgentRun


class RunEvent(Base):
    """Agent run event model for streaming updates."""
    
    __tablename__ = "run_events"
    
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(50)  # agent_start, tool_call, tool_result, agent_note, partial_output, artifact_ready, run_complete, run_error
    )
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    # Relationships
    run: Mapped["AgentRun"] = relationship("AgentRun", back_populates="events")
    
    def __repr__(self) -> str:
        return f"<RunEvent {self.event_type}>"
