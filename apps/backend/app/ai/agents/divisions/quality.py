"""Quality Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class QualityDivision:
    """Quality Division enforcing quality gates, code reviews, regression testing, and compliance."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="qa_agent", name="QA Agent", division=AgentDivision.QUALITY, role_description="Quality assurance & test execution validation"),
            AgentBlueprint(agent_id="code_review_agent", name="Code Review Agent", division=AgentDivision.QUALITY, role_description="Static code analysis & code review quality gates"),
            AgentBlueprint(agent_id="regression_agent", name="Regression Agent", division=AgentDivision.QUALITY, role_description="Automated regression test suite execution"),
            AgentBlueprint(agent_id="validation_agent", name="Validation Agent", division=AgentDivision.QUALITY, role_description="Requirements verification & schema validation"),
            AgentBlueprint(agent_id="compliance_agent", name="Compliance Agent", division=AgentDivision.QUALITY, role_description="Regulatory compliance & open source license audit"),
        ]
