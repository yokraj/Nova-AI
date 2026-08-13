"""Risk Classifier classifying action intents dynamically.
"""

from typing import Dict, Any
from app.ai.safety.models import RiskLevel, RiskAssessment
from app.ai.safety.interfaces import IRiskClassifier

class RiskClassifier(IRiskClassifier):
    """Evaluates parameters and classifies risk levels."""

    def classify(self, action: str, parameters: Dict[str, Any]) -> RiskAssessment:
        """Classifies action intent returning risk levels and reasons."""
        act_lower = action.lower()
        
        if any(w in act_lower for w in ["pay", "purchase", "booking", "money", "transfer", "buy"]):
            return RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                reason="Permanent transaction or financial purchase actions.",
                required_approvals=["user_explicit"],
                policy_matched="FinancialTransactionGate"
            )

        if any(w in act_lower for w in ["delete", "remove", "destroy", "rm", "format"]):
            return RiskAssessment(
                risk_level=RiskLevel.HIGH,
                reason="Irreversible database or local storage deletion actions.",
                required_approvals=["user_explicit"],
                policy_matched="DataLossPrevention"
            )

        if any(w in act_lower for w in ["fill", "upload", "send", "submit"]):
            return RiskAssessment(
                risk_level=RiskLevel.MEDIUM,
                reason="Data transmission or form submission action.",
                required_approvals=["user_implicit"],
                policy_matched="DataExfiltrationGate"
            )

        if any(w in act_lower for w in ["open", "run", "launch"]):
            return RiskAssessment(
                risk_level=RiskLevel.LOW,
                reason="Local browser or app launching actions.",
                required_approvals=[],
                policy_matched="LocalExecutionRule"
            )

        return RiskAssessment(
            risk_level=RiskLevel.NO_APPROVAL,
            reason="Passive read, analysis, or lookup actions.",
            required_approvals=[],
            policy_matched="PassiveReadRule"
        )
