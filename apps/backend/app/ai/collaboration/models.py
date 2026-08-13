"""Structured collaboration models and messaging schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MessagePriority(str, Enum):
    """Message priority rating levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MessageType(str, Enum):
    """Supported structured message types in inter-agent cooperation cycles."""
    TASK_REQUEST = "TaskRequest"
    TASK_RESPONSE = "TaskResponse"
    QUESTION = "Question"
    ANSWER = "Answer"
    PROGRESS_UPDATE = "ProgressUpdate"
    WARNING = "Warning"
    ERROR = "Error"
    APPROVAL_REQUEST = "ApprovalRequest"
    APPROVAL_RESPONSE = "ApprovalResponse"
    TASK_TRANSFER = "TaskTransfer"
    ARTIFACT = "Artifact"
    SUMMARY = "Summary"
    HEARTBEAT = "Heartbeat"

class StructuredMessage(BaseModel):
    """Standard payload structure for all inter-agent messages."""
    sender: str
    receiver: str
    correlation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: MessagePriority = MessagePriority.MEDIUM
    message_type: MessageType
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Explicit payload helper schemas for reference
class TaskRequestPayload(BaseModel):
    task_id: str
    title: str
    description: str
    required_capabilities: List[str] = Field(default_factory=list)
    context_data: Dict[str, Any] = Field(default_factory=dict)

class TaskResponsePayload(BaseModel):
    task_id: str
    status: str
    data: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)

class NegotiationBid(BaseModel):
    """Ownership negotiation bid structure."""
    agent_id: str
    capability_score: float
    workload_score: float
    bid_value: float
