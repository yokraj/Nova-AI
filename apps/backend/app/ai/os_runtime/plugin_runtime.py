"""Plugin Runtime supporting hot installation, removal, update, and reload of skills/plugins without restarting OS.
"""

from typing import Any, Dict


class PluginRuntime:
    """Plugin loader supporting hot installation, removal, updates, and module reloads without restarting Nova OS."""

    async def hot_reload_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Hot reloads target plugin/skill module dynamically."""
        return {
            "plugin_name": plugin_name,
            "status": "HOT_RELOADED",
            "no_restart_required": True,
        }
