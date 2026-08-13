"""PEP 562 Lazy Import Utility Mapping for the Plugins package."""

import importlib
from typing import Any

_LAZY_MAP: dict = {
    # Core
    "PluginConfiguration": "app.ai.plugins.configuration",
    # Models
    "PluginStatus": "app.ai.plugins.models",
    "PermissionType": "app.ai.plugins.models",
    "CapabilityType": "app.ai.plugins.models",
    "RiskLevel": "app.ai.plugins.models",
    "PluginPermission": "app.ai.plugins.models",
    "PluginCapability": "app.ai.plugins.models",
    "PluginMetadata": "app.ai.plugins.models",
    "PluginSpec": "app.ai.plugins.models",
    "ExecutionRequest": "app.ai.plugins.models",
    "ExecutionResult": "app.ai.plugins.models",
    "PluginMetrics": "app.ai.plugins.models",
    "PluginHealth": "app.ai.plugins.models",
    # Interfaces
    "IPluginEngine": "app.ai.plugins.interfaces",
    "IPluginManager": "app.ai.plugins.interfaces",
    "IPluginRegistry": "app.ai.plugins.interfaces",
    "IPluginLoader": "app.ai.plugins.interfaces",
    "ISandbox": "app.ai.plugins.interfaces",
    # Exceptions
    "PluginError": "app.ai.plugins.exceptions",
    "PluginNotFoundError": "app.ai.plugins.exceptions",
    "PluginLoadError": "app.ai.plugins.exceptions",
    "PluginValidationError": "app.ai.plugins.exceptions",
    "PermissionDeniedError": "app.ai.plugins.exceptions",
    "DependencyError": "app.ai.plugins.exceptions",
    "PluginExecutionError": "app.ai.plugins.exceptions",
    "SandboxViolationError": "app.ai.plugins.exceptions",
    # Platform Components
    "PluginRegistry": "app.ai.plugins.plugin_registry",
    "CapabilityRegistry": "app.ai.plugins.capability_registry",
    "SkillRegistry": "app.ai.plugins.skill_registry",
    "ToolRegistry": "app.ai.plugins.tool_registry",
    "PermissionManager": "app.ai.plugins.permission_manager",
    "PluginSandbox": "app.ai.plugins.sandbox",
    "DependencyResolver": "app.ai.plugins.dependency_resolver",
    "VersionManager": "app.ai.plugins.version_manager",
    "PluginValidator": "app.ai.plugins.plugin_validator",
    "PluginDiscovery": "app.ai.plugins.plugin_discovery",
    "PluginLoader": "app.ai.plugins.plugin_loader",
    "PluginInstaller": "app.ai.plugins.plugin_installer",
    "PluginUninstaller": "app.ai.plugins.plugin_uninstaller",
    "PluginUpdater": "app.ai.plugins.plugin_updater",
    "LifecycleManager": "app.ai.plugins.lifecycle_manager",
    "PluginEventManager": "app.ai.plugins.event_manager",
    "ExecutionManager": "app.ai.plugins.execution_manager",
    "ApiRouter": "app.ai.plugins.api_router",
    "ContextProvider": "app.ai.plugins.context_provider",
    "ConfigurationManager": "app.ai.plugins.configuration_manager",
    "PluginMemory": "app.ai.plugins.plugin_memory",
    "PluginMetricsTracker": "app.ai.plugins.metrics",
    "PluginHealthMonitor": "app.ai.plugins.health",
    "PluginCache": "app.ai.plugins.cache",
    "PluginManager": "app.ai.plugins.plugin_manager",
    "PluginEngine": "app.ai.plugins.plugin_engine",
    "MockPluginProvider": "app.ai.plugins.providers.mock_provider",
}


def lazy_import(name: str) -> Any:
    """Dynamically imports a mapped class or utility by name."""
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"Attribute '{name}' not found in plugins lazy mapping.")
