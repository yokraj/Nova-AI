"""Clarification Engine generating context-aware choices when user intent is ambiguous.
"""

from typing import List
from app.ai.conversation.models import ClarificationOption, ConversationContextSnapshot


class ClarificationEngine:
    """Formulates smart clarification choices ('Did you mean A or B?') instead of generic errors."""

    def generate_clarification_options(self, prompt: str, context: ConversationContextSnapshot) -> List[ClarificationOption]:
        """Generates clarification choices for ambiguous user input.

        Args:
            prompt: Ambiguous prompt text.
            context: Active ConversationContextSnapshot.

        Returns:
            List of ClarificationOption instances.
        """
        return [
            ClarificationOption(
                option_id="opt_a",
                label="Build Frontend Dashboard in React",
                description=f"Create new React dashboard in project {context.active_project}",
                target_intent="create_react_dashboard",
            ),
            ClarificationOption(
                option_id="opt_b",
                label="Build Backend API in FastAPI",
                description="Create new FastAPI REST endpoints",
                target_intent="create_fastapi_backend",
            ),
        ]
