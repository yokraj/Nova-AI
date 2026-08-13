"""Telemetry metrics collector for Enterprise Workspace Platform.
"""

import time
from app.ai.workspace.models import WorkspaceMetrics


class WorkspaceMetricsTracker:
    """Collects workspaces, members, remote executions, and sync operations."""

    def __init__(self) -> None:
        self._total_workspaces = 0
        self._total_members = 0
        self._remote_executions = 0
        self._sync_operations = 0

    def record_workspace_created(self) -> None:
        """Records workspace created."""
        self._total_workspaces += 1

    def record_member_joined(self) -> None:
        """Records member joined."""
        self._total_members += 1

    def record_remote_execution(self) -> None:
        """Records remote execution."""
        self._remote_executions += 1

    def record_sync_operation(self) -> None:
        """Records sync operation."""
        self._sync_operations += 1

    def get_metrics(self) -> WorkspaceMetrics:
        """Returns current WorkspaceMetrics snapshot."""
        return WorkspaceMetrics(
            total_workspaces=self._total_workspaces,
            total_members=self._total_members,
            remote_executions=self._remote_executions,
            sync_operations=self._sync_operations,
            timestamp=time.time(),
        )
