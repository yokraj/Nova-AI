"""Context Builder gathering user context parameters.
"""

from typing import Dict, Any
from app.ai.planner.models import Goal

class ContextBuilder:
    """Constructs metadata contexts for the GoalAnalyzer."""

    def build_context(self, goal: Goal) -> Dict[str, Any]:
        """Returns runtime configuration details mapped from goal context properties."""
        return {
            "conversation_id": goal.context.get("conversation_id", "default_conversation_id"),
            "project_root": goal.context.get("project_root", "C:\\Projects\\Nova-AI"),
            "user_id": goal.context.get("user_id", "default_user"),
            "offline_mode": True
        }
