"""Requirement Analyzer handles natural language parsing using LLM if gateway is active.
"""

import json
from typing import Optional
from app.agents.software_engineer.project_manager.interfaces import IRequirementAnalyzer
from app.agents.software_engineer.project_manager.models import ProjectRequirement
from app.agents.software_engineer.project_manager.requirement_parser import RequirementParser
from app.ai.gateway import AIGateway
from app.ai.models import ChatRequest, PromptMessage

class LocalRequirementAnalyzer(IRequirementAnalyzer):
    """Analyzes text requirements and maps them to a structured ProjectRequirement."""

    def __init__(self, gateway: Optional[AIGateway] = None) -> None:
        self.gateway = gateway
        self.parser = RequirementParser()

    async def analyze_requirements_async(self, raw_input: str) -> ProjectRequirement:
        """Asynchronously parses requirements using AI Gateway if online, otherwise falls back."""
        if self.gateway:
            try:
                system_prompt = """You are a senior product manager. Break down the user's project description and output a JSON dictionary containing the following keys:
- project_name: Name of the project
- goal: Core business goal
- modules: List of extracted functional modules/components (e.g. Authentication, Cart, Payment, etc.)
- constraints: List of constraints/limitations
- technology_requirements: List of tech stack languages/frameworks
- dependencies: List of external dependencies
- risks: List of technical risks

Ensure your output is valid JSON only, without any markdown formatting wrappers."""
                
                chat_req = ChatRequest(
                    model="qwen2.5-coder",
                    messages=[
                        PromptMessage(role="system", content=system_prompt),
                        PromptMessage(role="user", content=raw_input)
                    ]
                )
                res = await self.gateway.chat(chat_req)
                if res and res.message and res.message.content:
                    cleaned = res.message.content.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned.split("```json", 1)[1].rsplit("```", 1)[0].strip()
                    elif cleaned.startswith("```"):
                        cleaned = cleaned.split("```", 1)[1].rsplit("```", 1)[0].strip()
                    parsed = json.loads(cleaned)
                    return ProjectRequirement(**parsed)
            except Exception:
                # Fallback to local rule-based parsing on LLM failure
                pass

        # Call local rule-based parsing synchronously
        parsed = self.parser.parse_text(raw_input)
        return ProjectRequirement(**parsed)

    def analyze_requirements(self, raw_input: str) -> ProjectRequirement:
        """Synchronous implementation calling the parser."""
        parsed = self.parser.parse_text(raw_input)
        return ProjectRequirement(**parsed)
