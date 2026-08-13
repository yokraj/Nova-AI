"""Central UniversalAgentWorkforceEngine facade for Nova Autonomous AI Company.
"""

from typing import Any, Dict, List, Optional
from app.ai.agents.interfaces import IUniversalAgentWorkforceEngine
from app.ai.agents.manager import UniversalAgentWorkforceManager
from app.ai.agents.models import AgentBlueprint, WorkforceHealth


class UniversalAgentWorkforceEngine(IUniversalAgentWorkforceEngine):
    """Central AI Company facade acting as the multi-agent execution brain for Nova AI OS."""

    _instance: Optional["UniversalAgentWorkforceEngine"] = None

    def __new__(cls, manager: Optional[UniversalAgentWorkforceManager] = None) -> "UniversalAgentWorkforceEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.manager = manager or UniversalAgentWorkforceManager()
        elif manager is not None:
            cls._instance.manager = manager
        return cls._instance

    async def execute_voice_mission(self, voice_prompt: str) -> Dict[str, Any]:
        """Executes complete voice-driven mission through Executive -> Divisions -> Review -> Delivery."""
        return await self.manager.voice_orchestrator.process_voice_mission(voice_prompt)

    def list_all_agents(self) -> List[AgentBlueprint]:
        """Lists all 68 specialized agents across 9 divisions."""
        return self.manager.list_all_agents()

    def get_workforce_health(self) -> WorkforceHealth:
        """Snapshot overall workforce health diagnostics."""
        return self.manager.get_health()
