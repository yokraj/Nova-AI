"""Permissions profiles and checks for agent executions.
"""

from app.ai.agents.exceptions import AgentPermissionsError

class PermissionProfile:
    """Security clearance profile identifiers."""
    READ_ONLY = "ReadOnly"
    DEVELOPER = "Developer"
    AUTOMATION = "Automation"
    ADMINISTRATOR = "Administrator"

class PermissionsSystem:
    """Asserts hierarchical clearance levels, raising errors on validation failures."""

    def __init__(self) -> None:
        self._hierarchy = {
            PermissionProfile.READ_ONLY: 1,
            PermissionProfile.DEVELOPER: 2,
            PermissionProfile.AUTOMATION: 3,
            PermissionProfile.ADMINISTRATOR: 4
        }

    def check_clearance(self, agent_profile: str, required_profile: str) -> None:
        """Raises AgentPermissionsError if agent profile clearance rank falls below target profile."""
        agent_rank = self._hierarchy.get(agent_profile, 0)
        required_rank = self._hierarchy.get(required_profile, 99)

        if agent_rank < required_rank:
            raise AgentPermissionsError(
                f"Security block: clearance profile '{required_profile}' is required, but agent has '{agent_profile}'."
            )
