"""Prompt Builder preparing structured prompt instruction guides for local coding LLMs.
"""

from app.agents.software_engineer.debugging.models import (
    DebugContext,
    DebugRequest,
    RootCause,
)
from app.agents.software_engineer.generator.models import PromptPackage
from app.ai.models import PromptMessage


class DebuggingPromptBuilder:
    """Assembles context models, stacktrace lines, and root cause findings into coding messages."""

    def build_prompt(
        self, request: DebugRequest, context: DebugContext, root_cause: RootCause
    ) -> PromptPackage:
        """Packages instructions for resolving a detected crash error.

        Args:
            request: Active debug request configuration parameters.
            context: Workspace context elements.
            root_cause: Detected root cause details.

        Returns:
            PromptPackage.
        """
        system_prompt = (
            "You are a Senior Principal Software Debugging Engineer.\n"
            "Analyze the failure trace and root cause details to generate a safe code repair plan.\n"
            "Respond strictly with the code changes formatted inside markdown python code blocks."
        )

        user_content = (
            f"Traceback error:\n{request.traceback_str}\n\n"
            f"Detected Root Cause:\n"
            f"- File: {root_cause.origin_file}\n"
            f"- Function: {root_cause.origin_name if hasattr(root_cause, 'origin_name') else root_cause.origin_function}\n"
            f"- Causes: {root_cause.potential_causes}\n\n"
            f"Please propose code fixes suggestions and explanation descriptions."
        )

        messages = [
            PromptMessage(role="system", content=system_prompt),
            PromptMessage(role="user", content=user_content),
        ]

        return PromptPackage(messages=messages, system_prompt=system_prompt)
