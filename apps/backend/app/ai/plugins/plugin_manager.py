"""Plugin Manager facade coordinating discovery, loading, capability registration, and state transitions."""

from typing import Any, List, Optional
import structlog

from app.ai.plugins.capability_registry import CapabilityRegistry
from app.ai.plugins.configuration import PluginConfiguration
from app.ai.plugins.interfaces import IPluginManager
from app.ai.plugins.lifecycle_manager import LifecycleManager
from app.ai.plugins.models import PluginCapability, PluginPermission, PluginSpec, PluginStatus
from app.ai.plugins.permission_manager import PermissionManager
from app.ai.plugins.plugin_discovery import PluginDiscovery
from app.ai.plugins.plugin_loader import PluginLoader
from app.ai.plugins.plugin_registry import PluginRegistry
from app.ai.plugins.skill_registry import SkillRegistry
from app.ai.plugins.tool_registry import ToolRegistry
from app.ai.plugins.plugin_validator import PluginValidator
from app.ai.plugins.sdk.plugin import BasePlugin

logger = structlog.get_logger("plugin_manager")


class PluginManager(IPluginManager):
    """Coordinates full plugin lifecycle: register, load, enable, disable, capability indexing."""

    def __init__(
        self,
        config: Optional[PluginConfiguration] = None,
        registry: Optional[PluginRegistry] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        skill_registry: Optional[SkillRegistry] = None,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        self.config = config or PluginConfiguration()
        self.registry = registry or PluginRegistry()
        self.capabilities = capability_registry or CapabilityRegistry()
        self.skills = skill_registry or SkillRegistry()
        self.tools = tool_registry or ToolRegistry()
        self.loader = PluginLoader()
        self.discovery = PluginDiscovery(config=self.config)
        self.validator = PluginValidator()
        self.lifecycle = LifecycleManager(registry=self.registry)
        self.permissions = PermissionManager()

    def register_plugin(self, spec: PluginSpec, instance: Optional[Any] = None) -> None:
        """Register a plugin specification and optional class instance."""
        self.validator.validate(spec)

        if instance is None:
            instance = self.loader.load_plugin(spec)

        # Inspect decorators on instance if present
        self._extract_capabilities_and_permissions(spec, instance)

        # Store spec and instance
        self.registry.add_plugin(spec, instance)

        # Auto-enable if status loaded
        if spec.status in (PluginStatus.INSTALLED, PluginStatus.LOADED):
            self.enable_plugin(spec.plugin_id)

    def unregister_plugin(self, plugin_id: str) -> bool:
        """Unregister a plugin and purge capability maps."""
        self.disable_plugin(plugin_id)
        self.capabilities.unregister_plugin_capabilities(plugin_id)
        self.skills.unregister_plugin_skills(plugin_id)
        self.tools.unregister_plugin_tools(plugin_id)
        self.loader.unload_plugin(plugin_id)
        return self.registry.remove_plugin(plugin_id)

    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin and publish capabilities/skills/tools."""
        spec = self.registry.get_plugin(plugin_id)
        if not spec:
            return False

        instance = self.registry.get_instance(plugin_id)
        if instance and hasattr(instance, "initialize"):
            try:
                instance.initialize()
            except Exception as err:
                logger.error("Failed to initialize plugin", plugin_id=plugin_id, error=str(err))
                self.registry.update_status(plugin_id, PluginStatus.ERROR, str(err))
                return False

        self.registry.update_status(plugin_id, PluginStatus.ENABLED)

        # Register capabilities, skills, tools
        for cap in spec.capabilities:
            self.capabilities.register_capability(plugin_id, cap)
            self.skills.register_skills(plugin_id, cap)
            self.tools.register_tool(plugin_id, cap)

        logger.info("Enabled plugin", plugin_id=plugin_id)
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin and unindex its capabilities."""
        spec = self.registry.get_plugin(plugin_id)
        if not spec:
            return False

        instance = self.registry.get_instance(plugin_id)
        if instance and hasattr(instance, "shutdown"):
            try:
                instance.shutdown()
            except Exception:
                pass

        self.capabilities.unregister_plugin_capabilities(plugin_id)
        self.skills.unregister_plugin_skills(plugin_id)
        self.tools.unregister_plugin_tools(plugin_id)
        self.registry.update_status(plugin_id, PluginStatus.DISABLED)
        logger.info("Disabled plugin", plugin_id=plugin_id)
        return True

    def get_plugin(self, plugin_id: str) -> Optional[PluginSpec]:
        """Get plugin spec."""
        return self.registry.get_plugin(plugin_id)

    def list_plugins(self) -> List[PluginSpec]:
        """List all registered plugins."""
        return self.registry.list_plugins()

    def discover_and_load_all(self) -> List[PluginSpec]:
        """Automatically scan and register all plugins in plugins_dir."""
        discovered = self.discovery.discover_plugins()
        for spec in discovered:
            try:
                self.register_plugin(spec)
            except Exception as err:
                logger.warning("Failed to auto-register discovered plugin", plugin_id=spec.plugin_id, error=str(err))
        return self.list_plugins()

    # ------------------------------------------------------------------
    # Introspection helper
    # ------------------------------------------------------------------

    def _extract_capabilities_and_permissions(self, spec: PluginSpec, instance: Any) -> None:
        """Extract decorated capabilities and permissions from instance."""
        if not instance:
            return

        # Declared permissions on class
        if hasattr(instance, "_declared_permissions"):
            spec.permissions = getattr(instance, "_declared_permissions")

        # Scan methods for @_nova_capability
        extracted_caps: List[PluginCapability] = []
        for attr_name in dir(instance):
            try:
                attr = getattr(instance, attr_name)
                if hasattr(attr, "_nova_capability"):
                    cap_obj = getattr(attr, "_nova_capability")
                    extracted_caps.append(cap_obj)
            except Exception:
                pass

        if extracted_caps:
            spec.capabilities = extracted_caps
