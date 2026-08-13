"""Safety health check checker diagnostic checking queue and configurations.
"""

from typing import Dict, Any

class SafetyHealthMonitor:
    """Evaluates live component status maps of safety submodules."""

    def __init__(self, queue: Any, policy: Any, consent: Any, audit: Any) -> None:
        self.queue = queue
        self.policy = policy
        self.consent = consent
        self.audit = audit

    def check_health(self) -> Dict[str, Any]:
        """Runs diagnostics checks returning a status report."""
        details = {
            "approval_queue": "online" if self.queue is not None else "offline",
            "policy_engine": "online" if self.policy is not None else "offline",
            "consent_manager": "online" if self.consent is not None else "offline",
            "audit_logger": "online" if self.audit is not None else "offline"
        }
        overall = "healthy" if all(v == "online" for v in details.values()) else "degraded"
        return {
            "status": overall,
            "components": details
        }
