"""Executive Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision, AgentStatus


class ExecutiveDivision:
    """Executive Division managing mission decomposition, strategy, resource allocation, and final approvals."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="ceo_agent", name="CEO Agent", division=AgentDivision.EXECUTIVE, role_description="Executive leadership & final mission approval"),
            AgentBlueprint(agent_id="mission_director", name="Mission Director", division=AgentDivision.EXECUTIVE, role_description="Multi-divisional mission orchestration"),
            AgentBlueprint(agent_id="strategy_agent", name="Strategy Agent", division=AgentDivision.EXECUTIVE, role_description="Strategic roadmap & goal analysis"),
            AgentBlueprint(agent_id="planning_director", name="Planning Director", division=AgentDivision.EXECUTIVE, role_description="Hierarchical DAG planning & task decomposition"),
            AgentBlueprint(agent_id="operations_director", name="Operations Director", division=AgentDivision.EXECUTIVE, role_description="Resource allocation & priority management"),
            AgentBlueprint(agent_id="decision_agent", name="Decision Agent", division=AgentDivision.EXECUTIVE, role_description="Risk assessment & conflict resolution"),
        ]
