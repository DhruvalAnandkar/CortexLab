"""
Agent Run Schemas

Pydantic models for agent run requests and responses.
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class DiscoveryRunRequest(BaseModel):
    """Request to start a discovery agent run."""
    query: str  # User's research query


class DeepDiveRunRequest(BaseModel):
    """Request to start a deep dive agent run."""
    direction_id: str  # ID of the selected research direction
    direction_summary: str  # Summary of the chosen direction


class PaperRunRequest(BaseModel):
    """Request to start a paper drafting agent run."""
    include_experiments: List[str] = []  # IDs of experiment uploads to include


class RevisionRunRequest(BaseModel):
    """Request to revise an artifact."""
    artifact_id: str
    instructions: str  # User's revision instructions


class RunEventResponse(BaseModel):
    """Single run event response."""
    id: str
    event_type: str
    payload: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentRunResponse(BaseModel):
    """Agent run data response."""
    id: str
    project_id: str
    run_type: str
    status: str
    config: Optional[dict] = None
    result: Optional[dict] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentRunDetailResponse(AgentRunResponse):
    """Detailed agent run response with events."""
    events: List[RunEventResponse] = []


class AgentRunListResponse(BaseModel):
    """List of agent runs response."""
    runs: List[AgentRunResponse]
    total: int
