"""Prompt Builder constructing optimized LLM instructions for writing pytest test files.
"""

from app.agents.software_engineer.testing.interfaces import PromptBuilder
from app.agents.software_engineer.testing.models import (
    TestRequest,
    TestingContext,
)
from app.agents.software_engineer.generator.models import PromptPackage
from app.ai.models import PromptMessage


class TestingPromptBuilder(PromptBuilder):
    """Packages instructions guidelines and targets mock styles into LLM prompts."""

    def build_prompt(
        self, request: TestRequest, context: TestingContext, task_instructions: str
    ) -> PromptPackage:
        """Packages instructions.

        Args:
            request: Active test request settings.
            context: Collected testing context.
            task_instructions: Individual test task details.

        Returns:
            PromptPackage.
        """
        system_prompt = (
            "You are a Senior QA Automation Engineer assistant specialized in pytest and async testing.\n"
            "Generate production-ready tests covering standard execution paths, edge cases, and exceptions.\n"
            "Respond strictly with the code inside markdown python code blocks, e.g. ```python\\n[code]\\n```."
        )

        user_content = (
            f"Target module: {context.target_module}\n"
            f"Style guidelines: {context.style_guidelines}\n"
            f"Instructions: {task_instructions}\n\n"
            f"Please write the test suite code."
        )

        messages = [
            PromptMessage(role="system", content=system_prompt),
            PromptMessage(role="user", content=user_content),
        ]

        return PromptPackage(messages=messages, system_prompt=system_prompt)
