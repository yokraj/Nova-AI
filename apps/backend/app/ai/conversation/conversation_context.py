"""Cognitive Context Tracker capturing IDE, Desktop, Browser, Mission, and Agent context snapshots.
"""

from typing import Any, Dict
from app.ai.conversation.models import ConversationContextSnapshot


class CognitiveContextTracker:
    """Captures unified multi-subsystem context snapshots for conversational grounding."""

    def capture_snapshot(self, **kwargs: Any) -> ConversationContextSnapshot:
        """Captures cognitive context snapshot across IDE, Desktop, Browser, and Missions.

        Args:
            **kwargs: Overrides for active_app, active_project, active_file, browser_tab, etc.

        Returns:
            ConversationContextSnapshot instance.
        """
        return ConversationContextSnapshot(
            active_app=kwargs.get("active_app", "VS Code"),
            active_project=kwargs.get("active_project", "c:\\Projects\\Nova-AI"),
            active_file=kwargs.get("active_file", "main.py"),
            browser_tab=kwargs.get("browser_tab", "GitHub - Nova AI"),
            mission_id=kwargs.get("mission_id", None),
            agent_role=kwargs.get("agent_role", "software_engineer"),
        )
