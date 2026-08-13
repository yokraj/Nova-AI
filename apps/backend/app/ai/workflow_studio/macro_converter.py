"""Macro Converter converting raw macro streams into clean semantic steps.
"""

from typing import List
from app.ai.workflow_studio.intent_extractor import IntentExtractor
from app.ai.workflow_studio.models import RecordedEvent, WorkflowStep


class MacroConverter:
    """Converts low-level macro recording streams into clean semantic workflow steps."""

    def __init__(self) -> None:
        self.extractor = IntentExtractor()

    def convert_macro(self, raw_events: List[RecordedEvent]) -> List[WorkflowStep]:
        """Converts raw macro stream into semantic steps."""
        return self.extractor.extract_intents(raw_events)
