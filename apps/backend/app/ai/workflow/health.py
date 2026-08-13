"""Workflow health checkers evaluating subsystem operational states.
"""

from typing import Dict, Any

class WorkflowHealthMonitor:
    """Evaluates live component status maps."""

    def __init__(self, scheduler: Any, persistence: Any, approvals: Any) -> None:
        self.scheduler = scheduler
        self.persistence = persistence
        self.approvals = approvals

    def check_health(self) -> Dict[str, Any]:
        """Runs diagnostics checks returning a status report."""
        details = {
            "workflow_scheduler": "online" if self.scheduler is not None else "offline",
            "state_persistence": "online" if self.persistence is not None else "offline",
            "approval_manager": "online" if self.approvals is not None else "offline"
        }
        
        overall = "healthy" if all(v == "online" for v in details.values()) else "degraded"
        return {
            "status": overall,
            "components": details
        }
