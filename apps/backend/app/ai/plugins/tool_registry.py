"""Tool Registry exposing plugin capabilities as executable agent tools."""

from typing import Any, Callable, Dict, List, Optional
import structlog

from app.ai.plugins.models import PluginCapability

logger = structlog.get_logger("tool_registry")


class ToolRegistry:
    """Registry making plugin capabilities accessible as agent tool definitions."""

    def __init__(self) -> None:
        # tool_name -> Dict description metadata
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        plugin_id: str,
        capability: PluginCapability,
        handler: Optional[Callable] = None,
    ) -> None:
        """Expose a capability as a formatted agent tool."""
        tool_name = f"{plugin_id}_{capability.name}"
        self._tools[tool_name] = {
            "tool_name": tool_name,
            "plugin_id": plugin_id,
            "capability_name": capability.name,
            "description": capability.description,
            "parameters_schema": capability.parameters_schema,
            "handler": handler,
        }
        logger.debug("Registered agent tool", tool_name=tool_name)

    def unregister_plugin_tools(self, plugin_id: str) -> None:
        """Remove all agent tools belonging to a plugin."""
        to_remove = [k for k, v in self._tools.items() if v["plugin_id"] == plugin_id]
        for key in to_remove:
            self._tools.pop(key, None)

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent tool definition by name."""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available agent tools."""
        return list(self._tools.values())

    def count(self) -> int:
        """Total registered tools."""
        return len(self._tools)

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
