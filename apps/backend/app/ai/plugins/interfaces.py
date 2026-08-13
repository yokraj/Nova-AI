"""Abstract base interfaces for the Universal Plugin Platform."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.plugins.models import (
    ExecutionRequest,
    ExecutionResult,
    PluginCapability,
    PluginHealth,
    PluginMetrics,
    PluginSpec,
)


class IPluginEngine(ABC):
    """Abstract interface contract for the central Plugin Engine facade."""

    @abstractmethod
    async def install_plugin(self, plugin_path: str) -> PluginSpec:
        pass

    @abstractmethod
    async def uninstall_plugin(self, plugin_id: str) -> bool:
        pass

    @abstractmethod
    async def enable_plugin(self, plugin_id: str) -> bool:
        pass

    @abstractmethod
    async def disable_plugin(self, plugin_id: str) -> bool:
        pass

    @abstractmethod
    async def list_plugins(self) -> List[PluginSpec]:
        pass

    @abstractmethod
    async def plugin_capabilities(self, plugin_id: str = "") -> List[PluginCapability]:
        pass

    @abstractmethod
    async def execute_plugin(
        self,
        plugin_id: str,
        capability: str,
        parameters: Dict[str, Any],
        **kwargs: Any,
    ) -> ExecutionResult:
        pass

    @abstractmethod
    async def get_metrics(self) -> PluginMetrics:
        pass

    @abstractmethod
    def check_health(self) -> PluginHealth:
        pass


class IPluginManager(ABC):
    """Abstract interface for high-level plugin lifecycle coordination."""

    @abstractmethod
    def register_plugin(self, spec: PluginSpec, instance: Optional[Any] = None) -> None:
        pass

    @abstractmethod
    def unregister_plugin(self, plugin_id: str) -> bool:
        pass

    @abstractmethod
    def get_plugin(self, plugin_id: str) -> Optional[PluginSpec]:
        pass


class IPluginRegistry(ABC):
    """Abstract interface for storing plugin specifications and capability maps."""

    @abstractmethod
    def add_plugin(self, spec: PluginSpec) -> None:
        pass

    @abstractmethod
    def get_plugin(self, plugin_id: str) -> Optional[PluginSpec]:
        pass

    @abstractmethod
    def list_plugins(self) -> List[PluginSpec]:
        pass


class IPluginLoader(ABC):
    """Abstract interface for dynamic plugin module loading."""

    @abstractmethod
    def load_plugin(self, spec: PluginSpec) -> Any:
        pass

    @abstractmethod
    def unload_plugin(self, plugin_id: str) -> bool:
        pass


class ISandbox(ABC):
    """Abstract interface for safe capability execution isolation."""

    @abstractmethod
    async def execute(
        self,
        request: ExecutionRequest,
        handler: Any,
    ) -> ExecutionResult:
        pass
