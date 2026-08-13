"""Trigger Engine managing Voice, Schedule, File, Clipboard, and Webhook triggers.
"""

from typing import List
from app.ai.workflow_studio.models import WorkflowTrigger, WorkflowTriggerType


class TriggerEngine:
    """Manages workflow execution triggers across Voice, Schedule, File, and Webhook event listeners."""

    def create_voice_trigger(self, voice_phrase: str) -> WorkflowTrigger:
        """Creates voice command trigger."""
        return WorkflowTrigger(
            trigger_type=WorkflowTriggerType.VOICE,
            expression=voice_phrase,
            enabled=True,
        )

    def create_schedule_trigger(self, cron_expression: str) -> WorkflowTrigger:
        """Creates cron schedule trigger."""
        return WorkflowTrigger(
            trigger_type=WorkflowTriggerType.SCHEDULE,
            expression=cron_expression,
            enabled=True,
        )
