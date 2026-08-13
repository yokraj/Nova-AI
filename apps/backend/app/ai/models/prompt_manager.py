"""Prompt Manager maintaining versioned system, agent, and task prompt templates.
"""

from typing import Dict, Optional
from app.ai.models.interfaces import IPromptManager
from app.ai.models.models import PromptTemplate


class PromptManager(IPromptManager):
    """Prompt Manager maintaining prompt template versioning and string substitution."""

    def __init__(self) -> None:
        self._templates: Dict[str, PromptTemplate] = self._seed_templates()

    def _seed_templates(self) -> Dict[str, PromptTemplate]:
        templates = [
            PromptTemplate(
                template_id="sys_code_engineer",
                name="Software Engineering System Prompt",
                template_string="You are Nova AI Software Copilot. Write clean, production-grade {language} code for {goal}.",
                version="1.0.0",
                variables=["language", "goal"],
            ),
            PromptTemplate(
                template_id="sys_vision_reasoning",
                name="Vision Reasoning System Prompt",
                template_string="Analyze desktop interface image. Identify interactive control for {query}.",
                version="1.0.0",
                variables=["query"],
            ),
        ]
        return {t.template_id: t for t in templates}

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Retrieves prompt template by ID."""
        return self._templates.get(template_id)

    def render_prompt(self, template_id: str, **kwargs: str) -> str:
        """Renders template string with variable values."""
        tpl = self.get_template(template_id)
        if tpl:
            return tpl.template_string.format(**kwargs)
        return ""
