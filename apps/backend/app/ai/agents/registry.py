"""Agent Registry managing registration mappings and capabilities descriptors.
"""

import structlog
from typing import Dict, List, Optional

from app.ai.agents.models import AgentMetadata, AgentDescriptor, AgentRegistration
from app.ai.agents.exceptions import AgentRegistrationError

logger = structlog.get_logger("agent_registry")

class AgentRegistry:
    """Central registration mapping agent identities to execution blueprints."""

    def __init__(self) -> None:
        self._registrations: Dict[str, AgentRegistration] = {}
        self._aliases: Dict[str, str] = {}

        # Auto-register specialized workforce agents
        try:
            from app.agents.shared.utils import register_all_specialized_agents
            register_all_specialized_agents(self)
        except Exception:
            pass

    def register(self, descriptor: AgentDescriptor, metadata: AgentMetadata) -> str:
        """Registers a new agent descriptor and metadata model, validating uniqueness."""
        agent_id = metadata.id
        if agent_id in self._registrations:
            raise AgentRegistrationError(f"Agent registration failed: ID '{agent_id}' is already registered.")

        registration = AgentRegistration(
            registration_id=agent_id,
            descriptor=descriptor,
            metadata=metadata
        )
        self._registrations[agent_id] = registration
        self._aliases[metadata.name.lower()] = agent_id

        logger.info("Registered agent configuration blueprints", agent_id=agent_id, name=metadata.name)
        return agent_id

    def unregister(self, agent_id: str) -> None:
        """Removes registered blueprints and aliases."""
        if agent_id not in self._registrations:
            raise AgentRegistrationError(f"Agent unregistration failed: ID '{agent_id}' is not registered.")

        registration = self._registrations.pop(agent_id)
        name_key = registration.metadata.name.lower()
        if self._aliases.get(name_key) == agent_id:
            self._aliases.pop(name_key, None)

        logger.info("Unregistered agent configuration blueprints", agent_id=agent_id)

    def lookup(self, identifier: str) -> Optional[AgentRegistration]:
        """Finds active blueprint using direct unique IDs or lookup name aliases."""
        if identifier in self._registrations:
            return self._registrations[identifier]

        alias_id = self._aliases.get(identifier.lower())
        if alias_id:
            return self._registrations[alias_id]

        return None

    def list(self) -> List[AgentRegistration]:
        """Exposes raw registrations list."""
        return list(self._registrations.values())

    def exists(self, agent_id: str) -> bool:
        """Returns True if matching registration ID or alias exists."""
        return agent_id in self._registrations or agent_id.lower() in self._aliases
