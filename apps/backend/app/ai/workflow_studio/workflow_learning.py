"""Workflow Learning detecting repeated user actions and auto-suggesting automations.
"""

from typing import Any, Dict, List


class WorkflowLearning:
    """Observes repeated user UI actions and automatically recommends creating reusable workflows."""

    def analyze_action_frequency(self, action_signature: str, count: int) -> Dict[str, Any]:
        """Analyzes action frequency for workflow suggestion."""
        return {
            "action_signature": action_signature,
            "count": count,
            "recommend_automation": count >= 3,
        }
