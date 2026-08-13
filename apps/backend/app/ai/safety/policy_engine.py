"""Policy Engine matching risk levels against gating constraints.
"""

from typing import Dict, Any
from app.ai.safety.models import RiskLevel, RiskAssessment

class PolicyEngine:
    """Decides if an action is blocked or requires approvals based on risk levels."""

    def requires_approval(self, assessment: RiskAssessment) -> bool:
        """Returns True if the risk assessment demands user confirmations."""
        # HIGH and CRITICAL risk levels always require approvals
        return assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def evaluate_policy(self, action: str, risk_level: RiskLevel) -> Dict[str, Any]:
        """Runs policy audits, returning constraints requirements."""
        return {
            "action": action,
            "risk_level": risk_level.value,
            "requires_vocal_confirmation": risk_level == RiskLevel.CRITICAL,
            "allow_auto_approval": risk_level in [RiskLevel.NO_APPROVAL, RiskLevel.LOW]
        }
