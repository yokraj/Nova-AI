"""Autonomous Decision Engine evaluating executing policies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class IDecisionPolicy(ABC):
    """Abstract interface contract for evaluation policies."""

    @abstractmethod
    def evaluate(self, state: Dict[str, Any]) -> Optional[str]:
        """Evaluates metrics variables returning decided action string."""
        pass

class FailureCountPolicy(IDecisionPolicy):
    """Gives pause recommendation if failures limit exceeded."""

    def evaluate(self, state: Dict[str, Any]) -> Optional[str]:
        failures = state.get("failures_count", 0)
        if failures > 3:
            return "pause"
        return None

class ResourceThresholdPolicy(IDecisionPolicy):
    """Gives pause recommendation if system resources limits are crossed."""

    def evaluate(self, state: Dict[str, Any]) -> Optional[str]:
        cpu = state.get("cpu_usage_pct", 0.0)
        ram = state.get("ram_usage_pct", 0.0)
        if cpu > 95.0 or ram > 95.0:
            return "pause"
        return None

class AutonomousDecisionEngine:
    """Invokes extensible rules/policies to decide next execution transitions."""

    def __init__(self) -> None:
        self.policies: List[IDecisionPolicy] = [
            FailureCountPolicy(),
            ResourceThresholdPolicy()
        ]

    def add_policy(self, policy: IDecisionPolicy) -> None:
        """Registers a custom policy evaluator."""
        self.policies.append(policy)

    def decide(self, execution_state: Dict[str, Any]) -> str:
        """Evaluates state metrics against all policies, returning decided path."""
        for policy in self.policies:
            recommendation = policy.evaluate(execution_state)
            if recommendation:
                return recommendation
        return "continue"
