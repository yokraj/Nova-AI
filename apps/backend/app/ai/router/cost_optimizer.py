"""Cost Optimizer enforces local models priority.
"""

from app.ai.router.models import RoutingDecision

class CostOptimizer:
    """Enforces zero-cost local priority and handles cloud permission checks."""

    def __init__(self, ask_permission: bool = True) -> None:
        self.ask_permission = ask_permission

    def optimize_decision(self, decision: RoutingDecision, local_available: bool) -> RoutingDecision:
        """Enforces local selection or flags cloud fallback requirements."""
        if local_available:
            # We are using local models
            return decision

        if not local_available and decision.provider != "ollama":
            # Cloud model fallback scenario
            if self.ask_permission:
                # Flag confirmation requirement
                decision.reason += " (Requires explicit user permission before cloud execution)"
        
        return decision
