"""Business Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class BusinessDivision:
    """Business Division handling reports, spreadsheets, presentations, emails, schedules, and project management."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="excel_agent", name="Excel Agent", division=AgentDivision.BUSINESS, role_description="Spreadsheet creation, financial modeling & pivot tables"),
            AgentBlueprint(agent_id="word_agent", name="Word Agent", division=AgentDivision.BUSINESS, role_description="Executive business document & report authoring"),
            AgentBlueprint(agent_id="powerpoint_agent", name="PowerPoint Agent", division=AgentDivision.BUSINESS, role_description="Corporate slide deck & pitch deck generation"),
            AgentBlueprint(agent_id="pdf_agent", name="PDF Agent", division=AgentDivision.BUSINESS, role_description="PDF document generation & invoice processing"),
            AgentBlueprint(agent_id="email_agent", name="Email Agent", division=AgentDivision.BUSINESS, role_description="Professional email composition & inbox management"),
            AgentBlueprint(agent_id="meeting_agent", name="Meeting Agent", division=AgentDivision.BUSINESS, role_description="Meeting agenda synthesis & transcript summarization"),
            AgentBlueprint(agent_id="calendar_agent", name="Calendar Agent", division=AgentDivision.BUSINESS, role_description="Schedule optimization & appointment management"),
            AgentBlueprint(agent_id="project_manager_agent", name="Project Manager Agent", division=AgentDivision.BUSINESS, role_description="Project milestone tracking & deliverable timeline oversight"),
        ]
