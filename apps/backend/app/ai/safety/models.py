"""Domain models and Pydantic schemas for the Human Approval & Safety Engine.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    """Classification risk categories for executions."""
    NO_APPROVAL = "no_approval"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessment(BaseModel):
    """Result snapshot of action intent classification evaluations."""
    risk_level: RiskLevel
    reason: str
    required_approvals: List[str] = Field(default_factory=list)
    policy_matched: str

class ApprovalItem(BaseModel):
    """Approval request block tracking status."""
    approval_id: str
    mission_id: str
    action: str
    risk_level: RiskLevel
    status: str = "pending"  # pending, approved, rejected, expired, cancelled
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    reason: str
    voice_prompt: str

class UserConsent(BaseModel):
    """Active explicit permission grant limits."""
    permission_id: str
    scope: str
    granted: bool = False
    expiration: Optional[datetime] = None
    session_scoped: bool = True

class AuditRecord(BaseModel):
    """Audit trail record logged on target executions."""
    record_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user: str = "user"
    mission_id: str
    action: str
    risk_level: RiskLevel
    approved: bool
    reason: str
    execution_outcome: str = "not_executed"
