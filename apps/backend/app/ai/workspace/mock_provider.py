"""Mock Workspace Provider returning deterministic test responses for offline tests and CI.
"""

from typing import Any, Dict
from app.ai.workspace.models import (
    MemberRole,
    RemoteExecutionResult,
    WorkspaceDefinition,
    WorkspaceMember,
    WorkspaceType,
)


class MockWorkspaceProvider:
    """Mock Workspace Provider returning deterministic test responses."""

    async def mock_create_workspace(self, name: str) -> WorkspaceDefinition:
        return WorkspaceDefinition(
            name=name,
            workspace_type=WorkspaceType.PERSONAL,
            members=[WorkspaceMember(name="Owner", email="owner@corp.org", role=MemberRole.ADMIN)],
        )

    async def mock_remote_execute(self, target_device_id: str) -> RemoteExecutionResult:
        return RemoteExecutionResult(
            request_id="req_mock",
            success=True,
            output={"result": f"Executed mock command on {target_device_id}"},
            duration_sec=0.04,
        )
