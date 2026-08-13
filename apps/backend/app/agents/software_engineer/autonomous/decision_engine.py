"""Decision Engine manages system reasoning gates and user confirmation requests.
"""

from app.agents.software_engineer.autonomous.interfaces import IDecisionEngine
from app.agents.software_engineer.autonomous.models import Decision

class LocalDecisionEngine(IDecisionEngine):
    """Enforces execution checks on proposed decisions."""

    def validate_action(self, decision: Decision) -> bool:
        """Determines if the action is safe or requires user confirmation."""
        # Destructive refactors or deletions require active validation checks
        if "delete" in decision.action_type.lower() or "destructive" in decision.action_type.lower():
            decision.needs_user_confirmation = True
            # In automated execution fallback we assume false until confirmed
            return decision.confirmed
        
        decision.needs_user_confirmation = False
        return True
