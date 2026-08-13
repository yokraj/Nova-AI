"""Prompt Builder composing instructions for the local coding model.
"""

from app.agents.software_engineer.refactoring.interfaces import PromptBuilder
from app.agents.software_engineer.refactoring.models import (
    RefactoringContext,
    RefactoringRequest,
)
from app.agents.software_engineer.generator.models import PromptPackage
from app.ai.models import PromptMessage


class RefactoringPromptBuilder(PromptBuilder):
    """Packages style profiles and goals instructions into LLM system prompts."""

    def build_prompt(
        self, request: RefactoringRequest, context: RefactoringContext, instructions: str
    ) -> PromptPackage:
        """Constructs system constraints and user instructions chat messages.

        Args:
            request: Active refactoring request.
            context: Collected context.
            instructions: Decomposed task instructions.

        Returns:
            PromptPackage.
        """
        system_prompt = (
            "You are a Senior Software Developer assistant specialized in codebase refactoring.\n"
            "Apply the requested refactoring goals keeping the exact class and function signatures.\n"
            "Ensure code compiles successfully.\n"
            "Respond strictly with the code inside markdown python code blocks, e.g. ```python\\n[code]\\n```."
        )

        user_content = (
            f"Target file: {context.target_file}\n"
            f"Goals: {instructions}\n\n"
            f"Perform refactoring and return the completed code."
        )

        messages = [
            PromptMessage(role="system", content=system_prompt),
            PromptMessage(role="user", content=user_content),
        ]

        return PromptPackage(messages=messages, system_prompt=system_prompt)
