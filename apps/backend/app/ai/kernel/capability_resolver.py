"""Capability Resolver determining agents, plugins, services, and runtimes required for an intent.
"""

from typing import Any, Dict, List
from app.ai.kernel.interfaces import ICapabilityResolver
from app.ai.kernel.models import CapabilityMatch


class CapabilityResolver(ICapabilityResolver):
    """Capability Resolver dynamically matching requirements across Nova AI subsystems."""

    async def resolve_capabilities(self, goal_data: Dict[str, Any]) -> CapabilityMatch:
        """Determines subsystem components required to fulfill a goal.

        Args:
            goal_data: Structured goal dictionary from Universal Intent Engine.

        Returns:
            CapabilityMatch instance.
        """
        intent_type = goal_data.get("intent_type", "general_intelligence")
        goal = goal_data.get("goal", "")

        agents: List[str] = ["executive_agent"]
        plugins: List[str] = []
        services: List[str] = ["ai_gateway"]
        automation_modules: List[str] = []
        browser_actions: List[str] = []
        desktop_actions: List[str] = []
        memory_stores: List[str] = ["conversational_memory"]
        models: List[str] = ["ollama/llama3", "mock_llm"]
        runtime = "local_async"

        if intent_type == "software_copilot":
            agents.extend(["software_engineer", "security_engineer", "qa_engineer"])
            plugins.append("developer_tools_plugin")
            services.extend(["code_memory", "project_memory"])
            memory_stores.extend(["code_memory", "project_memory"])

        elif intent_type == "document_analysis":
            agents.extend(["researcher_agent"])
            services.extend(["rag_service", "epistemic_memory"])
            memory_stores.append("epistemic_memory")

        elif intent_type == "web_automation":
            agents.extend(["browser_agent"])
            automation_modules.append("browser_automation")
            browser_actions.extend(["navigate", "click", "fill_form", "extract"])

        elif intent_type == "devops_automation":
            agents.extend(["devops_agent", "security_engineer"])
            plugins.append("system_devops_plugin")

        elif intent_type == "desktop_automation":
            agents.extend(["desktop_agent"])
            automation_modules.append("desktop_automation")
            desktop_actions.extend(["launch_app", "window_focus", "keyboard_input", "mouse_click"])

        elif intent_type == "swarm_collaboration":
            agents.extend(["planner_agent", "swarm_coordinator", "software_engineer", "security_engineer"])
            runtime = "swarm_parallel"

        elif intent_type == "assistant_service":
            agents.extend(["personal_assistant_agent"])
            services.append("calendar_service")

        return CapabilityMatch(
            agents=list(dict.fromkeys(agents)),
            plugins=list(dict.fromkeys(plugins)),
            services=list(dict.fromkeys(services)),
            automation_modules=list(dict.fromkeys(automation_modules)),
            browser_actions=list(dict.fromkeys(browser_actions)),
            desktop_actions=list(dict.fromkeys(desktop_actions)),
            memory_stores=list(dict.fromkeys(memory_stores)),
            models=list(dict.fromkeys(models)),
            execution_runtime=runtime,
        )
