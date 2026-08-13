"""Abstract base contracts for Enterprise Workspace & Remote AI Orchestration Platform.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.workspace.models import (
    RemoteExecutionRequest,
    RemoteExecutionResult,
    WorkspaceDefinition,
    WorkspaceHealth,
    WorkspaceMember,
    WorkspaceMetrics,
    WorkspaceSearchResult,
)


class IWorkspaceManager(ABC):
    """Workspace Manager contract for creating, loading, and deleting workspaces."""

    @abstractmethod
    def create_workspace(self, name: str, workspace_type: str = "personal") -> WorkspaceDefinition:
        """Creates new workspace definition."""
        pass


class ICollaborationEngine(ABC):
    """Collaboration Engine contract for multi-node communication and task sharing."""

    @abstractmethod
    def share_task(self, workspace_id: str, task_title: str, assignee_email: str) -> Dict[str, Any]:
        """Delegates task to team member or remote agent."""
        pass


class IRemoteExecutionEngine(ABC):
    """Remote Execution Engine contract for running automations across remote machines."""

    @abstractmethod
    async def execute_remote(self, request: RemoteExecutionRequest) -> RemoteExecutionResult:
        """Executes remote command on target node device."""
        pass


class ISyncEngine(ABC):
    """Sync Engine contract for delta synchronization of knowledge, models, and workflows."""

    @abstractmethod
    def sync_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Triggers workspace delta synchronization pass."""
        pass


class IWorkspaceSearch(ABC):
    """Workspace Search contract for unified full-text and vector search."""

    @abstractmethod
    def search_workspace(self, workspace_id: str, query: str) -> WorkspaceSearchResult:
        """Executes unified search query across workspace artifacts."""
        pass


class IWorkspaceManagerFacade(ABC):
    """Subsystem Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts workspace manager."""
        pass


class IUniversalWorkspaceEngine(ABC):
    """Central Universal Workspace Engine facade contract."""

    @abstractmethod
    async def create_workspace(self, name: str, workspace_type: str = "personal") -> Dict[str, Any]:
        """Creates a new workspace."""
        pass

    @abstractmethod
    async def join_workspace(self, workspace_id: str, email: str, role: str = "developer") -> Dict[str, Any]:
        """Joins a workspace as member."""
        pass

    @abstractmethod
    async def leave_workspace(self, workspace_id: str, member_id: str) -> bool:
        """Leaves or removes member from workspace."""
        pass

    @abstractmethod
    async def workspace_members(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Lists members of workspace."""
        pass

    @abstractmethod
    async def workspace_search(self, workspace_id: str, query: str) -> Dict[str, Any]:
        """Searches across workspace documents, projects, and workflows."""
        pass

    @abstractmethod
    async def workspace_sync(self, workspace_id: str) -> Dict[str, Any]:
        """Synchronizes workspace knowledge, models, and workflows."""
        pass

    @abstractmethod
    async def remote_execute(self, target_device_id: str, command_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes remote desktop/browser automation or model task."""
        pass

    @abstractmethod
    async def workspace_backup(self, workspace_id: str) -> Dict[str, Any]:
        """Creates full workspace snapshot backup."""
        pass

    @abstractmethod
    async def workspace_restore(self, backup_id: str) -> Dict[str, Any]:
        """Restores workspace from snapshot backup."""
        pass

    @abstractmethod
    async def workspace_activity(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Retrieves real-time workspace activity feed log."""
        pass
