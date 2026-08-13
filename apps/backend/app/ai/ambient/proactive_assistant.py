"""Proactive Assistant evaluating desktop context and offering real-time suggestions."""

from typing import List
import structlog

from app.ai.ambient.interfaces import IProactiveAssistant
from app.ai.ambient.models import DesktopContextSnapshot, ProactiveSuggestion

logger = structlog.get_logger("proactive_assistant")


class ProactiveAssistant(IProactiveAssistant):
    """Evaluates desktop context snapshots to offer timely, actionable voice and UI suggestions."""

    async def evaluate_context(self, context: DesktopContextSnapshot) -> List[ProactiveSuggestion]:
        """Evaluate snapshot and return proactive ambient suggestions."""
        suggestions: List[ProactiveSuggestion] = []

        if context.is_in_meeting:
            suggestions.append(
                ProactiveSuggestion(
                    category="meeting",
                    title="Teams Meeting Active",
                    message="You're in a Teams meeting. Would you like me to summarize the agenda?",
                    recommended_action="summarize_meeting_agenda",
                    auto_create_mission=True,
                )
            )

        if context.debugging_duration_minutes >= 45.0:
            suggestions.append(
                ProactiveSuggestion(
                    category="debugging",
                    title="Debugging Error Log",
                    message="I noticed you've been debugging this error for 45 minutes. Would you like me to analyze it?",
                    recommended_action="analyze_error_log",
                )
            )

        if context.uncommitted_changes:
            suggestions.append(
                ProactiveSuggestion(
                    category="git",
                    title="Uncommitted Code Changes",
                    message="You haven't committed your code today.",
                    recommended_action="git_commit",
                )
            )

        if any(n.is_low_battery for n in context.notifications):
            suggestions.append(
                ProactiveSuggestion(
                    category="battery",
                    title="Battery Low Alert",
                    message="Battery is low.",
                    recommended_action="connect_charger",
                )
            )

        if context.is_user_idle:
            suggestions.append(
                ProactiveSuggestion(
                    category="idle",
                    title="Inactivity Alert",
                    message="You've been inactive for 1 hour.",
                    recommended_action="pause_session",
                )
            )

        logger.info("Evaluated desktop context for proactive suggestions", count=len(suggestions))
        return suggestions
