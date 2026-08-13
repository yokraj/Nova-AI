"""Universal Intent Engine converting natural language into structured goals.
"""

import re
from typing import Any, Dict, List
from app.ai.kernel.interfaces import IIntentEngine
from app.ai.kernel.models import IntentRequest, OperatingMode, PriorityLevel


class IntentEngine(IIntentEngine):
    """Universal Intent Engine parsing queries without hardcoded workflows."""

    def __init__(self) -> None:
        self._intent_patterns = [
            (r"(?i)\b(build|create|develop|code|write)\b.*\b(website|app|backend|api|service|component|project)\b", "software_project_goal", "software_copilot"),
            (r"(?i)\b(summarize|read|analyze|extract)\b.*\b(pdf|document|file|paper|text|report)\b", "document_analysis_goal", "document_analysis"),
            (r"(?i)\b(book|reserve|schedule|ticket|travel|flight|train|hotel)\b", "travel_automation_goal", "web_automation"),
            (r"(?i)\b(deploy|launch|host|server|docker|kubernetes|ci/cd)\b", "devops_goal", "devops_automation"),
            (r"(?i)\b(open|launch|start|run|close)\b.*\b(photoshop|chrome|vscode|app|application|calculator|notepad)\b", "desktop_automation_goal", "desktop_automation"),
            (r"(?i)\b(rename|delete|move|copy|find)\b.*\b(file|folder|directory)\b", "file_management_goal", "desktop_automation"),
            (r"(?i)\b(browse|navigate|search|scrape)\b.*\b(web|google|site|page)\b", "web_browsing_goal", "browser_automation"),
            (r"(?i)\b(swarm|collaborate|team)\b", "multi_agent_swarm_goal", "swarm_collaboration"),
            (r"(?i)\b(remind|calendar|event|schedule|today)\b", "personal_assistant_goal", "assistant_service"),
        ]

    async def parse_intent(self, request: IntentRequest) -> Dict[str, Any]:
        """Parses natural language query into a structured goal object.

        Args:
            request: The incoming IntentRequest.

        Returns:
            Dictionary defining goal_name, intent_type, domain, required_inputs, and metadata.
        """
        query = request.query.strip()
        matched_goal = "general_intent_goal"
        matched_domain = "general_intelligence"

        for pattern, goal_type, domain in self._intent_patterns:
            if re.search(pattern, query):
                matched_goal = goal_type
                matched_domain = domain
                break

        return {
            "intent_id": request.request_id,
            "raw_query": query,
            "goal": matched_goal,
            "intent_type": matched_domain,
            "target_domain": matched_domain,
            "operating_mode": request.operating_mode.value if hasattr(request.operating_mode, "value") else str(request.operating_mode),
            "priority": request.priority.value if hasattr(request.priority, "value") else str(request.priority),
            "user_id": request.user_id,
            "session_id": request.session_id,
            "source": request.source,
            "parameters": request.parameters,
            "extracted_entities": {
                "keywords": [word for word in query.split() if len(word) > 3],
                "action": query.split()[0] if query else "process",
            },
        }
