"""Execution Context tracking active execution frames states.
"""

from typing import Dict, Any, Optional

class ExecutionContext:
    """Stores variables for individual agent task executions."""

    def __init__(self, execution_id: Optional[str] = None) -> None:
        self.execution_id = execution_id
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Sets execution variable."""
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Gets execution variable."""
        return self._store.get(key, default)
