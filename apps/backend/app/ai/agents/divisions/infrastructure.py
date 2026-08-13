"""Infrastructure Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class InfrastructureDivision:
    """Infrastructure Division managing local runtimes, GPU resources, model lifecycle, memory, storage, and networking."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="runtime_manager_agent", name="Runtime Manager Agent", division=AgentDivision.INFRASTRUCTURE, role_description="Local AI engine & process manager"),
            AgentBlueprint(agent_id="model_manager_agent", name="Model Manager Agent", division=AgentDivision.INFRASTRUCTURE, role_description="Model downloading, SHA-256 verification & hot swapping"),
            AgentBlueprint(agent_id="gpu_manager_agent", name="GPU Manager Agent", division=AgentDivision.INFRASTRUCTURE, role_description="VRAM scheduler & thermal monitoring"),
            AgentBlueprint(agent_id="memory_manager_agent", name="Memory Manager Agent", division=AgentDivision.INFRASTRUCTURE, role_description="RAM allocation & garbage collection"),
            AgentBlueprint(agent_id="storage_manager_agent", name="Storage Manager Agent", division=AgentDivision.INFRASTRUCTURE, role_description="Disk space allocation & artifact management"),
            AgentBlueprint(agent_id="workspace_manager_agent", name="Workspace Manager Agent", division=AgentDivision.INFRASTRUCTURE, role_description="Multi-workspace context & environment isolation"),
            AgentBlueprint(agent_id="network_manager_agent", name="Network Manager Agent", division=AgentDivision.INFRASTRUCTURE, role_description="Local HTTP, WebSocket & Device Mesh networking"),
        ]
