"""BasePlugin class definition for plugin authoring."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.plugins.models import PluginCapability, PluginMetadata, PluginPermission
from app.ai.plugins.sdk.context import PluginContext
from app.ai.plugins.sdk.responses import PluginResult

logger = structlog.get_logger("nova_plugin")


class BasePlugin:
    """Abstract base class that all Nova plugins inherit from."""

    name: str = "BasePlugin"
    version: str = "1.0.0"
    author: str = "Nova AI"
    description: str = ""

    def __init__(self) -> None:
        self.permissions: List[PluginPermission] = []
        self.capabilities: List[PluginCapability] = []
        self.config: Dict[str, Any] = {}

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Called when the plugin is enabled."""
        self.config = config or {}
        logger.info("Initialized plugin", plugin=self.name, version=self.version)

    def shutdown(self) -> None:
        """Called when the plugin is disabled or unloaded."""
        logger.info("Shutdown plugin", plugin=self.name)

    async def execute_capability(
        self, capability_name: str, context: PluginContext
    ) -> PluginResult:
        """Dynamic dispatch to declared capability method."""
        method_name = capability_name.lower()
        method = getattr(self, method_name, None)
        if not method or not callable(method):
            return PluginResult.fail(
                f"Capability '{capability_name}' not implemented in plugin '{self.name}'."
            )
        try:
            res = await method(context) if self._is_coroutine(method) else method(context)
            if isinstance(res, PluginResult):
                return res
            return PluginResult.ok(data=res)
        except Exception as err:
            logger.error("Plugin capability error", plugin=self.name, capability=capability_name, error=str(err))
            return PluginResult.fail(str(err))

    @staticmethod
    def _is_coroutine(func: Any) -> bool:
        import inspect
        return inspect.iscoroutinefunction(func)
