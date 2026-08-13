"""Abstract interfaces for components of the Human Approval & Safety Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.safety.models import RiskAssessment, ApprovalItem, AuditRecord

class IRiskClassifier(ABC):
    """Abstract classifier evaluating execution action risk categories."""

    @abstractmethod
    def classify(self, action: str, parameters: Dict[str, Any]) -> RiskAssessment:
        """Evaluates parameters context returning a risk assessment snapshot."""
        pass

class ISafetyPersistence(ABC):
    """Abstract persistence layer for approvals and audit logs."""

    @abstractmethod
    def save_approval(self, item: ApprovalItem) -> None:
        """Stores approval request state."""
        pass

    @abstractmethod
    def get_approval(self, approval_id: str) -> Optional[ApprovalItem]:
        """Retrieves target approval request."""
        pass

    @abstractmethod
    def list_pending(self) -> List[ApprovalItem]:
        """Lists pending approvals."""
        pass

    @abstractmethod
    def log_audit(self, record: AuditRecord) -> None:
        """Appends audit log record."""
        pass
