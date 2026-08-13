"""Builds optimized instruction prompts to invoke local AI models.
"""

from app.agents.software_engineer.generator.interfaces import PromptBuilder
from app.agents.software_engineer.generator.models import (
    GenerationContext,
    GenerationRequest,
    PromptPackage,
)
from app.ai.models import PromptMessage


class CodePromptBuilder(PromptBuilder):
    """Compiles instructions, constraints, contexts, and styles into PromptPackages."""

    def build_prompt(
        self, request: GenerationRequest, context: GenerationContext, task_instructions: str
    ) -> PromptPackage:
        """Constructs PromptMessage context sequence.

        Args:
            request: Active generation request settings.
            context: Generated context and styles profile.
            task_instructions: Target task instructions.

        Returns:
            PromptPackage model containing prompt history messages list.
        """
        # Create clear guidelines for the local coding model
        system_prompt = (
            "You are a Senior Software Developer assistant.\n"
            "Generate production-ready code that matches the project's style guidelines.\n"
            "Strictly write code inside markdown code blocks, e.g. ```python\\n[code]\\n```.\n"
            "Return only the requested code. No conversation or side explanations."
        )

        style = context.style_profile
        user_content = (
            f"Repository context: {context.summary.repository_summary}\n"
            f"Style Guidelines:\n"
            f"- Indentation: {repr(style.indentation)}\n"
            f"- Class naming: {style.naming_convention_class}\n"
            f"- Function naming: {style.naming_convention_function}\n"
            f"- Docstring style: {style.docstring_format}\n\n"
            f"Instructions:\n{task_instructions}\n"
        )

        messages = [
            PromptMessage(role="system", content=system_prompt),
            PromptMessage(role="user", content=user_content),
        ]

        return PromptPackage(messages=messages, system_prompt=system_prompt)
