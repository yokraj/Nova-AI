"""Context Provider generating PluginContext objects."""

from typing import Any, Dict, Optional
from app.ai.plugins.sdk.context import PluginContext


class ContextProvider:
    """Constructs PluginContext objects for execution calls."""

    def build_context(
        self,
        agent_id: str = "system",
        mission_id: Optional[str] = None,
        workspace_path: str = "./",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> PluginContext:
        """Construct context object."""
        return PluginContext(
            agent_id=agent_id,
            mission_id=mission_id,
            workspace_path=workspace_path,
            parameters=parameters or {},
        )
