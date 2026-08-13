"""Plugin Action Registry enabling Skills SDK plugins to register custom desktop actions.
"""

from typing import Any, Callable, Dict, List


class PluginActionRegistry:
    """Registry allowing Skills SDK plugins to register Desktop, Browser, Office, Developer, Terminal, and Explorer actions."""

    def __init__(self) -> None:
        self._registered_actions: Dict[str, Callable[..., Any]] = {}

    def register_action(self, category: str, action_name: str, handler_fn: Callable[..., Any]) -> Dict[str, Any]:
        """Registers custom plugin action handler."""
        key = f"{category}:{action_name}"
        self._registered_actions[key] = handler_fn
        return {
            "action_key": key,
            "status": "REGISTERED",
        }

    def list_actions(self) -> List[str]:
        """Lists registered plugin actions."""
        return list(self._registered_actions.keys())
