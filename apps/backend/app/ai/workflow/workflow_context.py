"""Workflow Context container managing execution variables.
"""

from typing import Dict, Any
from app.ai.workflow.models import WorkflowContext

class WorkflowContextContainer:
    """Manages active thread execution variables scopes."""

    def __init__(self, workflow_id: str) -> None:
        self.context = WorkflowContext(workflow_id=workflow_id)

    def set(self, key: str, value: Any) -> None:
        """Sets workflow context variable."""
        self.context.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves workflow context variable."""
        return self.context.variables.get(key, default)

    def dump(self) -> Dict[str, Any]:
        """Dumps dictionary copy of context variables."""
        return dict(self.context.variables)

    def load(self, data: Dict[str, Any]) -> None:
        """Loads dictionary context variables."""
        self.context.variables = dict(data)
