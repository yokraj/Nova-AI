"""Automation Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class AutomationDivision:
    """Automation Division executing desktop automation, browser automation, and computer control workflows."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="desktop_automation_agent", name="Desktop Automation Agent", division=AgentDivision.AUTOMATION, role_description="Native Windows application & UI automation"),
            AgentBlueprint(agent_id="browser_automation_agent", name="Browser Automation Agent", division=AgentDivision.AUTOMATION, role_description="Playwright web scraping & web app automation"),
            AgentBlueprint(agent_id="workflow_agent", name="Workflow Agent", division=AgentDivision.AUTOMATION, role_description="Observed workflow learning & voice execution"),
            AgentBlueprint(agent_id="mission_execution_agent", name="Mission Execution Agent", division=AgentDivision.AUTOMATION, role_description="Autonomous multi-step long-running mission execution"),
            AgentBlueprint(agent_id="vision_automation_agent", name="Vision Automation Agent", role_description="Computer vision screen layout & element detection", division=AgentDivision.AUTOMATION),
            AgentBlueprint(agent_id="os_automation_agent", name="OS Automation Agent", division=AgentDivision.AUTOMATION, role_description="Registry, file system & Windows settings automation"),
        ]
