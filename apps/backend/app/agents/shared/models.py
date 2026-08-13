"""Shared domain models for specialized agents.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

class AgentTaskPayload(BaseModel):
    """Payload representing a task assigned to a specialized agent."""
    task_id: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

class AgentExecutionOutput(BaseModel):
    """Output results model returned by specialized agents operations."""
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)
    reasoning: str = ""
