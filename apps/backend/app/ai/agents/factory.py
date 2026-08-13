"""Agent Factory instantiating agent modules using DependencyContainer resolving.
"""

import structlog
from typing import Any

from app.ai.agents.models import AgentDescriptor, AgentMetadata
from app.ai.agents.exceptions import AgentRegistrationError
from app.ai.agents.utils import load_class_by_path
from app.ai.agents.dependency_container import DependencyContainer

logger = structlog.get_logger("agent_factory")

class AgentFactory:
    """Orchestrates dynamic service importing and constructor instantiations."""

    def __init__(self, container: DependencyContainer) -> None:
        self.container = container

    def create_agent(self, descriptor: AgentDescriptor, metadata: AgentMetadata) -> Any:
        """Dynamically loads and instantiates the agent class from descriptor blueprints."""
        try:
            class_type = load_class_by_path(descriptor.class_path)
        except Exception as err:
            raise AgentRegistrationError(f"Failed to dynamically load class at '{descriptor.class_path}': {str(err)}") from err

        # Optionally resolve standard configuration if present in containers registry
        config = None
        try:
            config = self.container.resolve("config")
        except Exception:
            pass

        try:
            try:
                agent = class_type(metadata=metadata, configuration=config)
            except TypeError:
                try:
                    agent = class_type(metadata=metadata, config=config)
                except TypeError:
                    agent = class_type(metadata=metadata)
            logger.info("Factory successfully instantiated agent", agent_id=metadata.id, class_path=descriptor.class_path)
            return agent
        except Exception as err:
            raise AgentRegistrationError(f"Constructor execution failed for class '{descriptor.class_path}': {str(err)}") from err
