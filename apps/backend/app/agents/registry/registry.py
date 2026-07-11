"""Registry tracking active instances, metadata descriptors, and health status logs of AI agents.
"""

from typing import Any, Dict, List, Optional
import uuid
from app.agents.base import AgentCapability, AgentPermission, BaseAgent
from app.agents.registry.descriptor import AgentDescriptor
from app.agents.registry.exceptions import (
    DuplicateAgentError,
    AgentRegistrationError,
    AgentInitializationError,
)
from app.agents.registry.health import AgentHealth, HealthReport
from app.agents.registry.status import AgentStatus


class AgentRegistry:
    """Central registry tracking descriptors, active instances, and health of AI Agents."""

    def __init__(self) -> None:
        """Initializes AgentRegistry."""
        self._descriptors: Dict[uuid.UUID, AgentDescriptor] = {}
        self._instances: Dict[uuid.UUID, BaseAgent] = {}
        self._healths: Dict[uuid.UUID, AgentHealth] = {}
        self._status: Dict[uuid.UUID, AgentStatus] = {}

    def register(self, agent: BaseAgent, descriptor: Optional[AgentDescriptor] = None) -> None:
        """Registers a BaseAgent instance and its descriptor metadata.

        Args:
            agent: Concrete agent class instance.
            descriptor: Optional metadata descriptor configuration.

        Raises:
            DuplicateAgentError: If duplicate ID or name exists.
            AgentRegistrationError: If registration fails due to invalid parameters.
        """
        if not isinstance(agent, BaseAgent):
            raise AgentRegistrationError("Target agent must inherit from BaseAgent.")

        if descriptor is None:
            # Derive descriptor from agent.metadata
            if not getattr(agent, "metadata", None):
                raise AgentRegistrationError("Agent metadata is missing; cannot auto-generate descriptor.")
            descriptor = AgentDescriptor(
                id=agent.metadata.id,
                name=agent.metadata.name,
                version=agent.metadata.version,
                description=agent.metadata.description,
                capabilities=agent.metadata.capabilities,
                permissions=agent.metadata.permissions,
                priority=100,
                enabled=True,
                tags=[],
            )

        if descriptor.id in self._descriptors:
            raise DuplicateAgentError(f"Agent with ID '{descriptor.id}' is already registered.")
        for d in self._descriptors.values():
            if d.name == descriptor.name:
                raise DuplicateAgentError(f"Agent with name '{descriptor.name}' is already registered.")

        self._descriptors[descriptor.id] = descriptor
        self._instances[descriptor.id] = agent
        
        initial_status = AgentStatus.REGISTERED if descriptor.enabled else AgentStatus.DISABLED
        self._healths[descriptor.id] = AgentHealth(status=initial_status)
        self._status[descriptor.id] = initial_status

    def unregister(self, agent_id: uuid.UUID) -> None:
        """Removes an agent's registration details.

        Args:
            agent_id: Target agent identifier.
        """
        self._descriptors.pop(agent_id, None)
        self._instances.pop(agent_id, None)
        self._healths.pop(agent_id, None)
        self._status.pop(agent_id, None)

    def get(self, agent_id: uuid.UUID) -> Optional[BaseAgent]:
        """Fetches a registered agent instance by ID.

        Args:
            agent_id: Target agent identifier.

        Returns:
            BaseAgent instance, or None.
        """
        return self._instances.get(agent_id)

    def list(self) -> List[AgentDescriptor]:
        """Returns metadata descriptors of all registered agents.

        Returns:
            List of AgentDescriptor models.
        """
        return list(self._descriptors.values())

    def exists(self, agent_id: uuid.UUID) -> bool:
        """Verifies if an agent ID is registered.

        Args:
            agent_id: Target agent identifier.

        Returns:
            True if registered; False otherwise.
        """
        return agent_id in self._descriptors

    async def initialize_all(self) -> None:
        """Invokes initialize callbacks for all enabled registered agents.

        Raises:
            AgentInitializationError: If initialization of any enabled agent fails.
        """
        for agent_id, instance in self._instances.items():
            descriptor = self._descriptors[agent_id]
            if descriptor.enabled and self._status[agent_id] == AgentStatus.REGISTERED:
                try:
                    await instance.initialize()
                    self._status[agent_id] = AgentStatus.INITIALIZED
                    self._healths[agent_id].status = AgentStatus.INITIALIZED
                except Exception as e:
                    self._status[agent_id] = AgentStatus.FAILED
                    self._healths[agent_id].status = AgentStatus.FAILED
                    self._healths[agent_id].error_count += 1
                    raise AgentInitializationError(
                        f"Failed to initialize agent '{descriptor.name}': {str(e)}"
                    ) from e

    async def shutdown_all(self) -> None:
        """Invokes shutdown callbacks for all active registered agents."""
        for agent_id, instance in self._instances.items():
            if self._status[agent_id] in (AgentStatus.INITIALIZED, AgentStatus.RUNNING, AgentStatus.BUSY):
                try:
                    await instance.shutdown()
                    self._status[agent_id] = AgentStatus.STOPPED
                    self._healths[agent_id].status = AgentStatus.STOPPED
                except Exception:
                    self._status[agent_id] = AgentStatus.FAILED
                    self._healths[agent_id].status = AgentStatus.FAILED
                    self._healths[agent_id].error_count += 1

    def find_by_capability(self, capability: AgentCapability) -> List[AgentDescriptor]:
        """Finds descriptors filtered by capability name tags.

        Args:
            capability: Target capability enum.

        Returns:
            Filtered list of descriptors.
        """
        return [
            d
            for d in self._descriptors.values()
            if capability in d.capabilities
        ]

    def find_by_permission(self, permission: AgentPermission) -> List[AgentDescriptor]:
        """Finds descriptors filtered by permission access tags.

        Args:
            permission: Target permission enum.

        Returns:
            Filtered list of descriptors.
        """
        return [
            d
            for d in self._descriptors.values()
            if permission in d.permissions
        ]

    def health(self, agent_id: Optional[uuid.UUID] = None) -> Any:
        """Returns health diagnostics telemetry status of an agent or all agents.

        Args:
            agent_id: Optional target agent identifier.

        Returns:
            AgentHealth snapshot for the given agent, or a dictionary mapping
            agent IDs to AgentHealth snapshots if agent_id is None.
        """
        if agent_id is not None:
            return self._healths.get(agent_id)
        return self._healths

    def enabled_agents(self) -> List[AgentDescriptor]:
        """Returns metadata descriptors of all enabled agents.

        Returns:
            List of AgentDescriptor models.
        """
        return [d for d in self._descriptors.values() if d.enabled]

    def disabled_agents(self) -> List[AgentDescriptor]:
        """Returns metadata descriptors of all disabled agents.

        Returns:
            List of AgentDescriptor models.
        """
        return [d for d in self._descriptors.values() if not d.enabled]

