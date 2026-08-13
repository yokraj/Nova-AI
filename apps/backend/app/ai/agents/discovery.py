"""Discovery Service querying active registry descriptors by capabilities or tags.
"""

from typing import List
from app.ai.agents.registry import AgentRegistry
from app.ai.agents.models import AgentRegistration

class DiscoveryService:
    """Exposes capabilities lookup methods querying the AgentRegistry."""

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def discover_by_capability(self, capability_name: str) -> List[AgentRegistration]:
        """Finds registrations possessing matching capability names."""
        results = []
        for registration in self.registry.list():
            for capability in registration.metadata.capabilities:
                if capability.name.lower() == capability_name.lower():
                    results.append(registration)
                    break
        return results

    def discover_by_type(self, agent_type: str) -> List[AgentRegistration]:
        """Finds registrations of matching type identifier strings."""
        return [
            registration for registration in self.registry.list()
            if registration.metadata.type.lower() == agent_type.lower()
        ]

    def discover_by_tag(self, tag: str) -> List[AgentRegistration]:
        """Finds registrations marked with target tag."""
        return [
            registration for registration in self.registry.list()
            if tag.lower() in [t.lower() for t in registration.metadata.tags]
        ]

    def discover_by_version(self, version: str) -> List[AgentRegistration]:
        """Finds registrations of precise version numbers."""
        return [
            registration for registration in self.registry.list()
            if registration.metadata.version == version
        ]
