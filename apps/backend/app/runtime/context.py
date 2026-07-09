"""Global system context for the Nova AI Runtime Kernel.

Provides shared access to execution states, variable configurations, and lifecycle
cancellation handles.
"""

from typing import Any, Dict, Optional


class RuntimeContext:
    """Consolidated state context variables for active runtime executions."""

    def __init__(self, env: str = "production") -> None:
        """Initializes the RuntimeContext.

        Args:
            env: The environment identifier string.
        """
        self.env: str = env
        self.settings: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.is_cancelled: bool = False
        self.metadata: Dict[str, Any] = {}

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieves a configuration value from context variables.

        Args:
            key: Target settings key.
            default: Fallback value if key is not found.

        Returns:
            The mapped configuration value.
        """
        return self.variables.get(key, self.settings.get(key, default))

    def set(self, key: str, value: Any) -> None:
        """Saves a state variable in execution context.

        Args:
            key: Target variable key.
            value: Value object to assign.
        """
        self.variables[key] = value

    def cancel(self) -> None:
        """Raises the runtime cancellation flag to abort execution loops."""
        self.is_cancelled = True
