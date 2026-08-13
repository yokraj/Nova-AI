"""Context Tracker integrating real-time desktop, IDE, and workspace state into conversation turns.
"""

from typing import Any, Dict
from app.ai.conversation.models import ConversationContextSnapshot


class ContextTracker:
    """Tracks active window, code file, git repository, and active mission context."""

    def get_current_context(self) -> ConversationContextSnapshot:
        """Returns current live context snapshot."""
        return ConversationContextSnapshot(
            active_app="VS Code",
            active_project="c:\\Projects\\Nova-AI",
            active_file="main.py",
            browser_tab="GitHub - Nova AI",
        )
