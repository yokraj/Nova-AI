"""Approval Manager orchestrating pause/resume flows for gated actions.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.ai.safety.models import ApprovalItem, RiskLevel
from app.ai.safety.approval_queue import ApprovalQueue
from app.ai.safety.approval_history import ApprovalHistory

class ApprovalManager:
    """Handles human approval cycles blocking executions."""

    def __init__(self, queue: ApprovalQueue, history: ApprovalHistory) -> None:
        self.queue = queue
        self.history = history

    def create_request(self, mission_id: str, action: str, risk_level: RiskLevel, reason: str, voice_prompt: str) -> str:
        """Registers a new pending approval and returns a unique ID."""
        approval_id = f"app_{uuid.uuid4().hex[:8]}"
        item = ApprovalItem(
            approval_id=approval_id,
            mission_id=mission_id,
            action=action,
            risk_level=risk_level,
            reason=reason,
            voice_prompt=voice_prompt
        )
        self.queue.add_pending(item)
        return approval_id

    def approve(self, approval_id: str) -> bool:
        """Resolves request status as approved."""
        resolved = self.queue.resolve(approval_id, approved=True)
        if resolved:
            self.history.log_resolved(resolved)
            return True
        return False

    def reject(self, approval_id: str) -> bool:
        """Resolves request status as rejected."""
        resolved = self.queue.resolve(approval_id, approved=False)
        if resolved:
            self.history.log_resolved(resolved)
            return True
        return False
