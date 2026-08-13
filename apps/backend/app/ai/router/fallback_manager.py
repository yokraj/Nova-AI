"""Fallback Manager implements fallback chain executions.
"""

import structlog
from typing import List, Optional
from app.ai.router.models import RoutingDecision
from app.ai.router.exceptions import FallbackExhaustedError

logger = structlog.get_logger(__name__)

class FallbackManager:
    """Orchestrates model changes and tracks failures across fallback loops."""

    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts
        self.failures_count = 0

    def resolve_next_model(self, decision: RoutingDecision, failed_model: str) -> str:
        """Returns the next model in the fallback chain or raises FallbackExhaustedError."""
        self.failures_count += 1
        
        if self.failures_count >= self.max_attempts:
            raise FallbackExhaustedError("All fallback model attempts in the routing chain failed execution.")

        chain = decision.fallback_chain
        if not chain:
            raise FallbackExhaustedError(f"No fallback configurations available for model '{failed_model}'.")

        # Select next model in chain
        next_model = chain[0]
        # Rotate chain for future retries
        decision.fallback_chain = chain[1:] + [failed_model]
        decision.selected_model = next_model

        logger.info(
            "model_routing_fallback_triggered",
            failed_model=failed_model,
            next_model=next_model,
            remaining_chain=decision.fallback_chain
        )
        return next_model
