"""Goal Optimizer learning user priorities, working hours, and coding preferences.
"""

from typing import Any, Dict


class GoalOptimizer:
    """Learns user priorities, working hours, project types, and coding preferences."""

    def __init__(self) -> None:
        self._user_profile: Dict[str, Any] = {
            "primary_tech_stack": ["Python", "FastAPI", "React"],
            "peak_working_hours": "09:00 - 18:00",
            "communication_preference": "voice_first",
        }

    def update_user_profile(self, key: str, value: Any) -> None:
        """Updates user profile preference."""
        self._user_profile[key] = value

    def get_user_profile(self) -> Dict[str, Any]:
        """Returns snapshot of learned user profile preferences."""
        return self._user_profile
