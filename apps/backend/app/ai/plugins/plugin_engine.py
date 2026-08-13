"""Central Universal Plugin Platform Engine facade."""

from typing import Any, Dict, List, Optional
import structlog

from app.ai.plugins.capability_registry import CapabilityRegistry
from app.ai.plugins.configuration import PluginConfiguration
from app.ai.plugins.execution_manager import ExecutionManager
from app.ai.plugins.health import PluginHealthMonitor
from app.ai.plugins.interfaces import IPluginEngine
from app.ai.plugins.metrics import PluginMetricsTracker
from app.ai.plugins.models import ExecutionResult, PluginCapability, PluginHealth, PluginMetrics, PluginSpec, PluginStatus
from app.ai.plugins.permission_manager import PermissionManager
from app.ai.plugins.plugin_installer import PluginInstaller
from app.ai.plugins.plugin_manager import PluginManager
from app.ai.plugins.plugin_memory import PluginMemory
from app.ai.plugins.plugin_registry import PluginRegistry
from app.ai.plugins.plugin_uninstaller import PluginUninstaller
from app.ai.plugins.providers.mock_provider import MockPluginProvider
from app.ai.plugins.sandbox import PluginSandbox
from app.ai.plugins.skill_registry import SkillRegistry
from app.ai.plugins.tool_registry import ToolRegistry

logger = structlog.get_logger("plugin_engine")


class PluginEngine(IPluginEngine):
    """Central engine orchestrating full Universal Plugin & Skill Integration Platform lifecycle."""

    def __init__(
        self,
        memory_engine: Optional[Any] = None,
        config: Optional[PluginConfiguration] = None,
    ) -> None:
        self.config = config or PluginConfiguration()
        self.registry = PluginRegistry()
        self.capabilities = CapabilityRegistry()
        self.skills = SkillRegistry()
        self.tools = ToolRegistry()
        self.permissions = PermissionManager()
        self.sandbox = PluginSandbox(timeout_seconds=self.config.sandbox_timeout_seconds)

        self.manager = PluginManager(
            config=self.config,
            registry=self.registry,
            capability_registry=self.capabilities,
            skill_registry=self.skills,
            tool_registry=self.tools,
        )
        self.execution = ExecutionManager(
            registry=self.registry,
            capability_registry=self.capabilities,
            permission_manager=self.permissions,
            sandbox=self.sandbox,
        )
        self.installer = PluginInstaller(config=self.config)
        self.uninstaller = PluginUninstaller()
        self.metrics = PluginMetricsTracker()
        self.health = PluginHealthMonitor(
            registry=self.registry,
            capability_registry=self.capabilities,
            sandbox=self.sandbox,
        )
        self.memory = PluginMemory(memory_engine=memory_engine)
        self.mock = MockPluginProvider()

        # Auto-discover built-in or local plugins if enabled
        if self.config.auto_discover:
            self._load_builtins()

        logger.info("PluginEngine initialized", plugins_count=self.registry.count())

    # ------------------------------------------------------------------
    # Core API Implementation
    # ------------------------------------------------------------------

    async def install_plugin(self, plugin_path: str) -> PluginSpec:
        """Install a plugin from file path or identifier."""
        spec = self.installer.install(plugin_path)
        self.manager.register_plugin(spec)
        self.metrics.update_counts(
            self.registry.count(),
            self.registry.count(),
            len([p for p in self.registry.list_plugins() if p.status == PluginStatus.ENABLED]),
        )
        await self.memory.persist_plugin_info(spec.plugin_id, spec.metadata.description)
        return spec

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a registered plugin."""
        success = self.manager.unregister_plugin(plugin_id)
        if success:
            self.uninstaller.uninstall(plugin_id)
        return success

    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable an installed plugin."""
        return self.manager.enable_plugin(plugin_id)

    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable an active plugin."""
        return self.manager.disable_plugin(plugin_id)

    async def list_plugins(self) -> List[PluginSpec]:
        """List all registered plugins."""
        return self.manager.list_plugins()

    async def plugin_capabilities(self, plugin_id: str = "") -> List[PluginCapability]:
        """List active capabilities across plugins."""
        return self.capabilities.list_capabilities(plugin_id=plugin_id)

    async def execute_plugin(
        self,
        plugin_id: str,
        capability: str,
        parameters: Dict[str, Any],
        **kwargs: Any,
    ) -> ExecutionResult:
        """Execute a capability safely."""
        agent_id = kwargs.get("agent_id", "system")
        mission_id = kwargs.get("mission_id")
        result = await self.execution.execute_capability(
            plugin_id=plugin_id,
            capability_name=capability,
            parameters=parameters,
            agent_id=agent_id,
            mission_id=mission_id,
        )
        self.metrics.record_execution(result.success, result.execution_time_seconds)
        return result

    async def resolve_voice_command(self, utterance: str) -> Optional[Dict[str, Any]]:
        """Resolve natural language voice phrase to capability match."""
        resolved = self.skills.resolve_intent(utterance)
        if resolved:
            plugin_id, capability_name = resolved
            return {
                "plugin_id": plugin_id,
                "capability": capability_name,
                "confidence": 0.95,
            }
        return None

    async def get_metrics(self) -> PluginMetrics:
        """Return platform telemetry metrics snapshot."""
        enabled_count = len([p for p in self.registry.list_plugins() if p.status == PluginStatus.ENABLED])
        self.metrics.update_counts(self.registry.count(), self.registry.count(), enabled_count)
        return self.metrics.snapshot()

    def check_health(self) -> PluginHealth:
        """Check composite health status."""
        return self.health.check_health()

    # ------------------------------------------------------------------
    # Built-in loader helper
    # ------------------------------------------------------------------

    def _load_builtins(self) -> None:
        """Load reference built-in plugins."""
        from app.ai.plugins.builtins.browser_plugin import BrowserPlugin
        from app.ai.plugins.builtins.desktop_plugin import DesktopPlugin
        from app.ai.plugins.builtins.file_plugin import FilePlugin
        from app.ai.plugins.builtins.pdf_plugin import PDFPlugin
        from app.ai.plugins.builtins.email_plugin import EmailPlugin
        from app.ai.plugins.builtins.calendar_plugin import CalendarPlugin
        from app.ai.plugins.builtins.office_plugin import OfficePlugin
        from app.ai.plugins.builtins.terminal_plugin import TerminalPlugin

        builtins = [
            ("browser", BrowserPlugin()),
            ("desktop", DesktopPlugin()),
            ("file", FilePlugin()),
            ("pdf", PDFPlugin()),
            ("email", EmailPlugin()),
            ("calendar", CalendarPlugin()),
            ("office", OfficePlugin()),
            ("terminal", TerminalPlugin()),
        ]

        for pid, inst in builtins:
            spec = PluginSpec(
                plugin_id=pid,
                metadata=inst.metadata if hasattr(inst, "metadata") else None or
                from_meta(inst.name, inst.version, inst.description),
                status=PluginStatus.INSTALLED,
            )
            try:
                self.manager.register_plugin(spec, instance=inst)
            except Exception as err:
                logger.warning("Failed to register builtin plugin", pid=pid, error=str(err))


def from_meta(name: str, version: str, desc: str) -> Any:
    from app.ai.plugins.models import PluginMetadata
    return PluginMetadata(name=name, version=version, description=desc)
