"""Mission Context container managing execution variables.
"""

from typing import Dict, Any
from app.ai.mission.models import MissionContext

class MissionContextContainer:
    """Manages active mission execution variables scopes."""

    def __init__(self, mission_id: str) -> None:
        self.context = MissionContext(mission_id=mission_id)

    def set(self, key: str, value: Any) -> None:
        """Sets mission context variable."""
        self.context.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves mission context variable."""
        return self.context.variables.get(key, default)

    def dump(self) -> Dict[str, Any]:
        """Dumps dictionary copy of context variables."""
        return dict(self.context.variables)

    def load(self, data: Dict[str, Any]) -> None:
        """Loads dictionary context variables."""
        self.context.variables = dict(data)
