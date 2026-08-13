"""Telemetry metrics collector for Universal Workflow Learning & No-Code Automation Studio.
"""

import time
from app.ai.workflow_studio.models import WorkflowStudioMetrics


class WorkflowStudioMetricsTracker:
    """Collects recordings, executions, workflows created, and variables detected."""

    def __init__(self) -> None:
        self._total_recordings = 0
        self._total_executions = 0
        self._workflows_created = 0
        self._variables_detected = 0

    def record_session(self) -> None:
        """Records recording session."""
        self._total_recordings += 1

    def record_execution(self) -> None:
        """Records workflow execution."""
        self._total_executions += 1

    def record_workflow_created(self) -> None:
        """Records created workflow."""
        self._workflows_created += 1

    def record_variable_detected(self) -> None:
        """Records detected variable."""
        self._variables_detected += 1

    def get_metrics(self) -> WorkflowStudioMetrics:
        """Returns current WorkflowStudioMetrics snapshot."""
        return WorkflowStudioMetrics(
            total_recordings=self._total_recordings,
            total_executions=self._total_executions,
            workflows_created=self._workflows_created,
            variables_detected=self._variables_detected,
            timestamp=time.time(),
        )
