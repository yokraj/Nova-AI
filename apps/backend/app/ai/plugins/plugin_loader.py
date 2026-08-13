"""Plugin Loader dynamically importing and instantiating plugin classes."""

import importlib.util
import os
import sys
from typing import Any, Optional
import structlog

from app.ai.plugins.exceptions import PluginLoadError
from app.ai.plugins.interfaces import IPluginLoader
from app.ai.plugins.models import PluginSpec
from app.ai.plugins.sdk.plugin import BasePlugin

logger = structlog.get_logger("plugin_loader")


class PluginLoader(IPluginLoader):
    """Dynamically loads Python plugin modules from file paths or module names."""

    def __init__(self) -> None:
        self._loaded_modules: dict = {}

    def load_plugin(self, spec: PluginSpec) -> Any:
        """Load and instantiate plugin instance from entrypoint or module path."""
        try:
            # If instance class is already provided directly in entrypoint or loaded before
            if hasattr(spec, "_instance") and getattr(spec, "_instance"):
                return getattr(spec, "_instance")

            if not spec.entrypoint or not os.path.exists(spec.entrypoint):
                # Fallback: create a generic BasePlugin instance if no custom entrypoint file
                inst = BasePlugin()
                inst.name = spec.metadata.name
                inst.version = spec.metadata.version
                return inst

            module_name = f"nova_plugin_{spec.plugin_id}"
            spec_module = importlib.util.spec_from_file_location(module_name, spec.entrypoint)
            if not spec_module or not spec_module.loader:
                raise PluginLoadError(f"Cannot load module spec from entrypoint '{spec.entrypoint}'")

            module = importlib.util.module_from_spec(spec_module)
            sys.modules[module_name] = module
            spec_module.loader.exec_module(module)
            self._loaded_modules[spec.plugin_id] = module

            # Find BasePlugin subclass in module
            plugin_cls = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugin_cls = attr
                    break

            if not plugin_cls:
                inst = BasePlugin()
                inst.name = spec.metadata.name
                inst.version = spec.metadata.version
                return inst

            instance = plugin_cls()
            logger.info("Loaded plugin class", plugin_id=spec.plugin_id, class_name=plugin_cls.__name__)
            return instance

        except Exception as err:
            logger.error("Failed to load plugin", plugin_id=spec.plugin_id, error=str(err))
            raise PluginLoadError(f"Failed to load plugin '{spec.plugin_id}': {err}") from err

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload module from sys.modules cache."""
        module_name = f"nova_plugin_{plugin_id}"
        if module_name in sys.modules:
            sys.modules.pop(module_name, None)
            self._loaded_modules.pop(plugin_id, None)
            logger.info("Unloaded plugin module", plugin_id=plugin_id)
            return True
        return False
