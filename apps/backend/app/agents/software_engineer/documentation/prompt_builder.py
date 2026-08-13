"""Prompt Builder compiling instructions for LLMs writing technical documents.
"""

from app.agents.software_engineer.documentation.interfaces import PromptBuilder
from app.agents.software_engineer.documentation.models import (
    DocumentationContext,
    DocumentationRequest,
)
from app.agents.software_engineer.generator.models import PromptPackage
from app.ai.models import PromptMessage


class DocumentationPromptBuilder(PromptBuilder):
    """Packages style constraints and file stats into LLM instructions messages."""

    def build_prompt(
        self, request: DocumentationRequest, context: DocumentationContext, task_instructions: str
    ) -> PromptPackage:
        """Constructs technical documentation chat prompts.

        Args:
            request: Active request settings.
            context: Compiled context details.
            task_instructions: Instruction string.

        Returns:
            PromptPackage.
        """
        system_prompt = (
            "You are a Technical Writer and Software Architect.\n"
            "Produce clear, high-quality, and complete documentation in markdown format.\n"
            "Never use cloud references. Detail parameter types, internal structures, and code workflows."
        )

        user_content = (
            f"Instructions: {task_instructions}\n"
            f"Workspace files count: {context.scanned_files_count}\n"
            f"Style guidelines: {context.style_guidelines}\n\n"
            f"Please write the requested documentation."
        )

        messages = [
            PromptMessage(role="system", content=system_prompt),
            PromptMessage(role="user", content=user_content),
        ]

        return PromptPackage(messages=messages, system_prompt=system_prompt)
