"""Prompt Manager Module.

Dynamic system, agent, tool, workflow, and conversation prompt template rendering and management.
Ensures prompt templates are decoupled, configurable, and parameterizable without hardcoded prompt locks.
"""

from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class PromptManager:
    """Enterprise Prompt Template Registry and Dynamic Rendering Engine."""

    def __init__(self) -> None:
        self._templates: Dict[str, str] = {
            "system_default": (
                "You are Nova AI Operating System's Universal Intelligence Engine. "
                "You provide calm, accurate, professional, helpful, and honest assistance. "
                "Tone: {personality_tone}. Persona: {personality_traits}."
            ),
            "reasoning": (
                "System: Execute step-by-step logical reasoning to analyze the problem.\n"
                "Problem Statement: {problem}\n"
                "Constraints: {constraints}\n"
                "Goal: Provide a rigorous, step-by-step resolution."
            ),
            "planning": (
                "Goal: {goal}\n"
                "Available Tools: {tools}\n"
                "Available Agents: {agents}\n"
                "Decompose this goal into a structured, dependency-ordered execution plan."
            ),
            "verification": (
                "Draft Answer:\n{draft_answer}\n"
                "Context & Grounding:\n{context}\n"
                "Verify the draft answer for factual accuracy, mathematical logic, code correctness, "
                "and absence of hallucinations."
            ),
            "reflection": (
                "Review the following draft output:\n{draft_output}\n"
                "Identify potential weaknesses, lack of clarity, or missing details, and propose a refined version."
            ),
            "tool_call": (
                "Task: {task}\n"
                "Selected Tool: {tool_name}\n"
                "Generate precise structured JSON arguments for executing this tool."
            ),
            "agent_assignment": (
                "Subtask: {subtask}\n"
                "Agent Role: {agent_role}\n"
                "Generate clear instructions and contextual bounds for this agent."
            ),
        }
        logger.info("prompt_manager_initialized", template_count=len(self._templates))

    def register_template(self, name: str, template: str) -> None:
        """Registers or overrides a prompt template."""
        self._templates[name] = template
        logger.info("prompt_template_registered", name=name)

    def render(self, template_name: str, **kwargs: Any) -> str:
        """Renders target prompt template with provided keyword variables."""
        if template_name not in self._templates:
            logger.warning("prompt_template_not_found_fallback", template_name=template_name)
            # Safe fallback if template name is unknown
            return f"Prompt Template [{template_name}] context: {kwargs}"
        
        template_str = self._templates[template_name]
        try:
            return template_str.format(**kwargs)
        except KeyError as exc:
            logger.error("prompt_render_missing_key", template_name=template_name, missing_key=str(exc))
            # Graceful partial formatting fallback
            return template_str
