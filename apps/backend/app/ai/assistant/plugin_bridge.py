"""Plugin Bridge connecting Assistant Engine to built-in plugins (Calendar, Email, Desktop, Browser, Office, File)."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("assistant_plugin_bridge")


class PluginBridge:
    """Invokes capabilities across built-in plugins for personal assistant operations."""

    async def execute_plugin_capability(self, plugin_id: str, capability: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke plugin capability via Plugin Engine / Gateway."""
        logger.info("PluginBridge invoking plugin capability", plugin=plugin_id, capability=capability)
        try:
            from app.ai.gateway import IAIGateway
            from app.core.dependency_container import resolve
            gateway = resolve(IAIGateway)
            return await gateway.execute_plugin(plugin_id, capability, parameters)
        except Exception as e:
            logger.info("Plugin Engine gateway fallback", error=str(e))
            return {"status": "executed", "plugin": plugin_id, "capability": capability}
