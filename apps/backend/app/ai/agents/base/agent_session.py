"""Session model storing session variables and transitions history logs.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List

class AgentSession:
    """Manages unique execution sessions properties, variables, and histories."""

    def __init__(self, agent_id: str) -> None:
        self.session_id = str(uuid.uuid4())
        self.agent_id = agent_id
        self.variables: Dict[str, Any] = {}
        self.state_history: List[Dict[str, Any]] = []
        self.started_at = datetime.utcnow()

    def record_state_change(self, old_state: str, new_state: str, details: str = "") -> None:
        """Appends status history change entry."""
        self.state_history.append({
            "timestamp": datetime.utcnow(),
            "from_state": old_state,
            "to_state": new_state,
            "details": details
        })

    def set_variable(self, key: str, value: Any) -> None:
        """Stores custom session variable."""
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Retrieves custom session variable."""
        return self.variables.get(key, default)
