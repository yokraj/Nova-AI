"""Scans packages dynamically to auto-discover and load agent classes.
"""

import uuid
from typing import Any, List, Optional, Type
import importlib
import inspect
import pkgutil
from app.agents.base import BaseAgent
from app.agents.registry.registry import AgentRegistry


class DiscoveryService:
    """Service for discovering, validating, and checking dependencies of AI agent classes."""

    def __init__(self, registry: AgentRegistry) -> None:
        """Initializes DiscoveryService.

        Args:
            registry: Active AgentRegistry.
        """
        self.registry = registry

    def discover(self, package_path: str) -> List[Type[BaseAgent]]:
        """Scans module paths discovering python classes inheriting from BaseAgent.

        Args:
            package_path: String representation of import package segment (e.g. 'app.plugins').

        Returns:
            List of subclasses classes types.
        """
        discovered: List[Type[BaseAgent]] = []
        try:
            package = importlib.import_module(package_path)
            if hasattr(package, "__path__"):
                for _, name, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                    try:
                        mod = importlib.import_module(name)
                        for _, cls in inspect.getmembers(mod, inspect.isclass):
                            if issubclass(cls, BaseAgent) and cls is not BaseAgent:
                                if cls not in discovered:
                                    discovered.append(cls)
                    except Exception:
                        pass
        except Exception:
            pass
        return discovered

    def validate(self, agent_cls: Type[Any]) -> bool:
        """Verifies if a class type matches agent inheritance criteria.

        Args:
            agent_cls: Class type to validate.

        Returns:
            True if valid; False otherwise.
        """
        try:
            return issubclass(agent_cls, BaseAgent) and agent_cls is not BaseAgent
        except TypeError:
            return False

    def reload(self, package_path: str) -> List[Type[BaseAgent]]:
        """Resets all registered mappings and re-scans modules.

        Args:
            package_path: Python package segments.

        Returns:
            Re-scanned discovered classes list.
        """
        for desc in self.registry.list():
            self.registry.unregister(desc.id)
        return self.discover(package_path)

    def dependency_check(self, agent_id: Optional[uuid.UUID] = None) -> bool:
        """Verifies if agent dependencies are registered and satisfied.

        Args:
            agent_id: Optional target agent identifier. If None, checks all agents.

        Returns:
            True if all dependencies are satisfied; False otherwise.
        """
        agents_to_check = []
        if agent_id is not None:
            agent = self.registry.get(agent_id)
            if not agent:
                return False
            agents_to_check.append(agent_id)
        else:
            agents_to_check = [d.id for d in self.registry.list()]

        for aid in agents_to_check:
            agent = self.registry.get(aid)
            if not agent:
                continue
            
            descriptor = self.registry._descriptors.get(aid)
            class_deps = getattr(agent.__class__, "dependencies", [])
            descriptor_deps = getattr(descriptor, "dependencies", []) if descriptor else []
            metadata_deps = getattr(agent.metadata, "dependencies", []) if getattr(agent, "metadata", None) else []
            
            all_deps = list(set(class_deps) | set(descriptor_deps) | set(metadata_deps))
            
            for dep in all_deps:
                dep_found = False
                try:
                    dep_uuid = uuid.UUID(str(dep)) if not isinstance(dep, uuid.UUID) else dep
                    if self.registry.exists(dep_uuid):
                        dep_found = True
                except ValueError:
                    for registered_desc in self.registry.list():
                        if registered_desc.name == dep:
                            dep_found = True
                            break
                if not dep_found:
                    return False
        return True


class Discovery(DiscoveryService):
    """Helper for discovering and validating AI agent classes from python packages."""

    pass

