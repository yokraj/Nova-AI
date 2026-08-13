"""Intent Extractor converting raw events into high-level semantic workflow steps.
"""

from typing import List
from app.ai.workflow_studio.interfaces import IIntentExtractor
from app.ai.workflow_studio.models import (
    RecordedEvent,
    WorkflowActionType,
    WorkflowStep,
)


class IntentExtractor(IIntentExtractor):
    """Converts low-level mouse/keyboard events into high-level semantic intent steps."""

    def extract_intents(self, events: List[RecordedEvent]) -> List[WorkflowStep]:
        """Converts events list into semantic workflow steps.

        Args:
            events: List of raw RecordedEvent instances.

        Returns:
            List of WorkflowStep objects.
        """
        steps: List[WorkflowStep] = []
        for evt in events:
            if evt.event_type == "click":
                steps.append(
                    WorkflowStep(
                        action_type=WorkflowActionType.CLICK,
                        description=f"Click control '{evt.target_control or 'Button'}' in {evt.target_app}",
                        target_selector=evt.target_control or "button",
                        parameters={"x": evt.x, "y": evt.y},
                    )
                )
            elif evt.event_type == "type_text":
                steps.append(
                    WorkflowStep(
                        action_type=WorkflowActionType.TYPE_TEXT,
                        description=f"Type text into {evt.target_app}",
                        target_selector="input",
                        parameters={"text": evt.text_value or ""},
                    )
                )
            elif evt.event_type == "browser_navigate":
                steps.append(
                    WorkflowStep(
                        action_type=WorkflowActionType.CLICK,
                        description=f"Navigate to {evt.target_control}",
                        target_selector=evt.target_control or "url",
                        parameters={"url": evt.target_control},
                    )
                )
        return steps
