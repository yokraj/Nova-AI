"""Approval Manager managing human-in-the-loop validation checkpoints gates.
"""

import structlog
from typing import Dict, Optional
from app.ai.workflow.models import ApprovalRequest, ApprovalResult
from app.ai.workflow.interfaces import IApprovalManager

logger = structlog.get_logger("approval_manager")

class ApprovalManager(IApprovalManager):
    """Pauses steps on destructive/risky actions until manual approvals release locks."""

    def __init__(self) -> None:
        self.requests: Dict[str, ApprovalRequest] = {}
        self.results: Dict[str, ApprovalResult] = {}

    def request_approval(self, request: ApprovalRequest) -> None:
        """Stores a new approval block request."""
        logger.info("Human approval gate requested for step", 
                    workflow_id=request.workflow_id, step_id=request.step_id, action=request.action)
        self.requests[request.approval_id] = request

    def resolve_approval(self, approval_id: str, result: ApprovalResult) -> None:
        """Saves reviewer feedback and releases workflow pauses."""
        if approval_id not in self.requests:
            logger.error("Approval request ID not registered", approval_id=approval_id)
            return

        self.results[approval_id] = result
        self.requests[approval_id].status = "approved" if result.approved else "rejected"
        logger.info("Human approval gate resolved", 
                    approval_id=approval_id, approved=result.approved, comments=result.comments)

    def get_status(self, approval_id: str) -> str:
        """Returns current gating status of target approval ID."""
        req = self.requests.get(approval_id)
        return req.status if req else "not_found"
