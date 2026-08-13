"""Mock provider simulating safety check outcomes offline.
"""

from typing import Dict, Any

class MockSafetyProvider:
    """Mock offline safety checks provider."""

    def simulate_risk_check(self, action: str) -> Dict[str, Any]:
        """Classifies mock action risk."""
        if "delete" in action.lower():
            return {"risk_level": "high", "requires_approval": True}
        return {"risk_level": "no_approval", "requires_approval": False}

    def simulate_consent_check(self, scope: str) -> bool:
        """Evaluates simulated consent permissions."""
        return scope == "authorized"
