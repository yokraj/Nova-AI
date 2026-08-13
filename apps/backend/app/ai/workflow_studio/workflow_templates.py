"""Workflow Templates catalog providing pre-built automation blueprints.
"""

from typing import List
from app.ai.workflow_studio.models import (
    WorkflowActionType,
    WorkflowDefinition,
    WorkflowStep,
)


class WorkflowTemplates:
    """Catalog of pre-built workflow templates for common automation scenarios."""

    def get_template_catalog(self) -> List[WorkflowDefinition]:
        """Returns list of pre-packaged template workflows."""
        return [
            WorkflowDefinition(
                name="E-Commerce Order Processor",
                description="Scrapes order invoice, extracts amounts, and sends notification.",
                steps=[
                    WorkflowStep(action_type=WorkflowActionType.CLICK, description="Open Dashboard", target_selector="btn_orders"),
                    WorkflowStep(action_type=WorkflowActionType.TYPE_TEXT, description="Filter Orders", target_selector="input_filter", parameters={"text": "Pending"}),
                ],
            ),
            WorkflowDefinition(
                name="Daily GST Filing Helper",
                description="Opens GST portal, extracts monthly total, files return.",
                steps=[
                    WorkflowStep(action_type=WorkflowActionType.CLICK, description="Open GST Portal", target_selector="nav_gst"),
                ],
            ),
        ]
