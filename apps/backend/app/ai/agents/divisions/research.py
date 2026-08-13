"""Research Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class ResearchDivision:
    """Research Division providing deep technical research, fact verification, and knowledge synthesis."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="research_lead_agent", name="Research Lead Agent", division=AgentDivision.RESEARCH, role_description="Directs deep technical research investigations"),
            AgentBlueprint(agent_id="research_agent", name="Research Agent", division=AgentDivision.RESEARCH, role_description="Literature search, arXiv, OpenAlex research retrieval"),
            AgentBlueprint(agent_id="verification_agent", name="Verification Agent", division=AgentDivision.RESEARCH, role_description="Fact-checking & evidence verification"),
            AgentBlueprint(agent_id="knowledge_graph_agent", name="Knowledge Graph Agent", division=AgentDivision.RESEARCH, role_description="Semantic knowledge graph synthesis"),
            AgentBlueprint(agent_id="citation_agent", name="Citation Agent", division=AgentDivision.RESEARCH, role_description="Academic citation & reference validation"),
            AgentBlueprint(agent_id="document_analysis_agent", name="Document Analysis Agent", division=AgentDivision.RESEARCH, role_description="PDF & technical documentation analysis"),
            AgentBlueprint(agent_id="repository_analysis_agent", name="Repository Analysis Agent", division=AgentDivision.RESEARCH, role_description="Codebase & repository structure analysis"),
            AgentBlueprint(agent_id="reasoning_agent", name="Reasoning Agent", division=AgentDivision.RESEARCH, role_description="Formal logical reasoning & technical synthesis"),
        ]
