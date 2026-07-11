"""AgentSelector resolving candidate agent instances.
"""

from typing import List
from app.agents.base import AgentCapability
from app.agents.registry.registry import AgentRegistry
from app.orchestrator.intent import IntentType

# Map IntentType to AgentCapability
INTENT_TO_CAPABILITY = {
    IntentType.CHAT: AgentCapability.CHAT,
    IntentType.CODE: AgentCapability.CODE,
    IntentType.SEARCH: AgentCapability.SEARCH,
    IntentType.BROWSER: AgentCapability.BROWSER,
    IntentType.DESKTOP: AgentCapability.DESKTOP,
    IntentType.VOICE: AgentCapability.VOICE,
    IntentType.VISION: AgentCapability.VISION,
    IntentType.WORKFLOW: AgentCapability.WORKFLOW,
}


class AgentSelector:
    """Selects, ranks, and resolves fallback concrete agents for tasks."""

    def __init__(self, registry: AgentRegistry) -> None:
        """Initializes AgentSelector.

        Args:
            registry: Central AgentRegistry.
        """
        self.registry = registry

    def select(self, intent: IntentType) -> List[str]:
        """Resolves list of agent names capable of processing the given intent.

        Args:
            intent: Classified IntentType.

        Returns:
            List of candidate agent names.
        """
        capability = INTENT_TO_CAPABILITY.get(intent)
        if not capability:
            return [self.fallback(intent)]

        descriptors = self.registry.find_by_capability(capability)
        return [d.name for d in descriptors if d.enabled]

    def rank(self, agents: List[str]) -> List[str]:
        """Ranks list of agents according to suitability (using descriptor priority).

        Args:
            agents: List of candidate agent names.

        Returns:
            Ranked list of agent names.
        """
        agent_priorities = []
        for name in agents:
            priority = 100
            for d in self.registry.list():
                if d.name == name:
                    priority = d.priority
                    break
            agent_priorities.append((name, priority))

        # Sort descending (highest priority ranking first)
        agent_priorities.sort(key=lambda x: x[1], reverse=True)
        return [x[0] for x in agent_priorities]

    def fallback(self, intent: IntentType) -> str:
        """Returns default fallback agent name.

        Args:
            intent: The intent for fallback resolution.

        Returns:
            Name of default agent.
        """
        for d in self.registry.list():
            if d.enabled and AgentCapability.CHAT in d.capabilities:
                return d.name
        return "ChatAgent"
