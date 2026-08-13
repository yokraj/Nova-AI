"""Creative Division for Nova Autonomous AI Company.
"""

from typing import List
from app.ai.agents.models import AgentBlueprint, AgentDivision


class CreativeDivision:
    """Creative Division delivering UI/UX design, visual graphics, presentations, and branding assets."""

    @staticmethod
    def get_agents() -> List[AgentBlueprint]:
        return [
            AgentBlueprint(agent_id="ui_designer_agent", name="UI Designer Agent", division=AgentDivision.CREATIVE, role_description="Modern web UI layout & glassmorphism styling"),
            AgentBlueprint(agent_id="ux_designer_agent", name="UX Designer Agent", division=AgentDivision.CREATIVE, role_description="User experience flows & interaction patterns"),
            AgentBlueprint(agent_id="presentation_agent", name="Presentation Agent", division=AgentDivision.CREATIVE, role_description="Slide deck & presentation layout design"),
            AgentBlueprint(agent_id="image_generation_agent", name="Image Generation Agent", division=AgentDivision.CREATIVE, role_description="Visual asset & UI mockup generation"),
            AgentBlueprint(agent_id="video_planning_agent", name="Video Planning Agent", division=AgentDivision.CREATIVE, role_description="Video storyboard & demo script planning"),
            AgentBlueprint(agent_id="branding_agent", name="Branding Agent", division=AgentDivision.CREATIVE, role_description="Brand design system & typography guidelines"),
            AgentBlueprint(agent_id="voice_design_agent", name="Voice Design Agent", division=AgentDivision.CREATIVE, role_description="Natural voice persona & prompt styling"),
        ]
