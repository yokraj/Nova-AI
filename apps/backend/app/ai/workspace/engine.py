"""Central Universal Workspace Engine facade unifying multi-user workspaces, remote execution, and team sync.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.workspace.activity_feed import ActivityFeed
from app.ai.workspace.audit_engine import AuditEngine
from app.ai.workspace.cache import WorkspaceCache
from app.ai.workspace.collaboration_engine import CollaborationEngine
from app.ai.workspace.configuration import WorkspaceConfiguration
from app.ai.workspace.conflict_resolver import ConflictResolver
from app.ai.workspace.device_manager import DeviceManager
from app.ai.workspace.health import WorkspaceHealthMonitor
from app.ai.workspace.interfaces import IUniversalWorkspaceEngine
from app.ai.workspace.knowledge_sync import KnowledgeSync
from app.ai.workspace.manager import WorkspaceManagerFacade
from app.ai.workspace.member_manager import MemberManager
from app.ai.workspace.metrics import WorkspaceMetricsTracker
from app.ai.workspace.models import (
    MemberRole,
    RemoteExecutionRequest,
    RemoteExecutionResult,
    WorkspaceDefinition,
    WorkspaceHealth,
    WorkspaceMetrics,
    WorkspaceType,
)
from app.ai.workspace.notification_center import NotificationCenter
from app.ai.workspace.organization_manager import OrganizationManager
from app.ai.workspace.permission_manager import PermissionManager
from app.ai.workspace.presence_manager import PresenceManager
from app.ai.workspace.recommendation_engine import RecommendationEngine
from app.ai.workspace.remote_agent_manager import RemoteAgentManager
from app.ai.workspace.remote_execution import RemoteExecution
from app.ai.workspace.role_manager import RoleManager
from app.ai.workspace.security_engine import SecurityEngine
from app.ai.workspace.session_manager import SessionManager
from app.ai.workspace.shared_documents import SharedDocuments
from app.ai.workspace.shared_missions import SharedMissions
from app.ai.workspace.shared_models import SharedModels
from app.ai.workspace.shared_plugins import SharedPlugins
from app.ai.workspace.shared_projects import SharedProjects
from app.ai.workspace.shared_skills import SharedSkills
from app.ai.workspace.shared_workflows import SharedWorkflows
from app.ai.workspace.sync_engine import SyncEngine
from app.ai.workspace.task_assignment import TaskAssignment
from app.ai.workspace.team_manager import TeamManager
from app.ai.workspace.workspace_backup import WorkspaceBackup
from app.ai.workspace.workspace_context import WorkspaceContext
from app.ai.workspace.workspace_export import WorkspaceExport
from app.ai.workspace.workspace_import import WorkspaceImport
from app.ai.workspace.workspace_manager import WorkspaceManager
from app.ai.workspace.workspace_memory import WorkspaceMemory
from app.ai.workspace.workspace_restore import WorkspaceRestore
from app.ai.workspace.workspace_search import WorkspaceSearch


class UniversalWorkspaceEngine(IUniversalWorkspaceEngine):
    """The central Enterprise Workspace & Remote AI Orchestration Platform runtime for Nova AI."""

    def __init__(self, config: Optional[WorkspaceConfiguration] = None) -> None:
        self.config = config or WorkspaceConfiguration()
        self.manager_facade = WorkspaceManagerFacade(self.config)

        self.workspace_manager = WorkspaceManager()
        self.organization_manager = OrganizationManager()
        self.team_manager = TeamManager()
        self.member_manager = MemberManager()
        self.role_manager = RoleManager()
        self.permission_manager = PermissionManager()

        self.workspace_memory = WorkspaceMemory()
        self.workspace_context = WorkspaceContext()
        self.knowledge_sync = KnowledgeSync()

        self.shared_workflows = SharedWorkflows()
        self.shared_skills = SharedSkills()
        self.shared_plugins = SharedPlugins()
        self.shared_models = SharedModels()
        self.shared_documents = SharedDocuments()
        self.shared_projects = SharedProjects()
        self.shared_missions = SharedMissions()

        self.task_assignment = TaskAssignment()
        self.collaboration_engine = CollaborationEngine()
        self.presence_manager = PresenceManager()
        self.notification_center = NotificationCenter()
        self.activity_feed = ActivityFeed()
        self.audit_engine = AuditEngine()
        self.security_engine = SecurityEngine()

        self.remote_agent_manager = RemoteAgentManager()
        self.remote_execution = RemoteExecution()
        self.device_manager = DeviceManager()
        self.session_manager = SessionManager()

        self.sync_engine = SyncEngine()
        self.conflict_resolver = ConflictResolver()
        self.workspace_search_engine = WorkspaceSearch()

        self.backup_engine = WorkspaceBackup()
        self.restore_engine = WorkspaceRestore()
        self.export_engine = WorkspaceExport()
        self.import_engine = WorkspaceImport()
        self.recommendation_engine = RecommendationEngine()

        self.metrics_tracker = WorkspaceMetricsTracker()
        self.health_monitor = WorkspaceHealthMonitor()
        self.cache = WorkspaceCache(ttl_seconds=self.config.cache_ttl_seconds)

        self._registered_workspaces: Dict[str, WorkspaceDefinition] = {}

        # Default Personal Workspace
        default_ws = self.workspace_manager.create_workspace("Personal Workspace", "personal")
        self.member_manager.add_member(default_ws, "Owner", "owner@nova-ai.org", MemberRole.ADMIN)
        self.device_manager.register_device("Primary Desktop Node", "127.0.0.1", "desktop_pc")
        self._registered_workspaces[default_ws.workspace_id] = default_ws

    async def create_workspace(self, name: str, workspace_type: str = "personal") -> Dict[str, Any]:
        """Creates a new workspace."""
        ws = self.workspace_manager.create_workspace(name, workspace_type)
        self.member_manager.add_member(ws, "Owner", "owner@nova-ai.org", MemberRole.ADMIN)
        self._registered_workspaces[ws.workspace_id] = ws
        self.activity_feed.record_activity(ws.workspace_id, "owner@nova-ai.org", f"Created workspace '{name}'")
        self.metrics_tracker.record_workspace_created()
        return ws.model_dump(mode="json")

    async def join_workspace(self, workspace_id: str, email: str, role: str = "developer") -> Dict[str, Any]:
        """Joins a workspace as member."""
        ws = self._registered_workspaces.get(workspace_id)
        if not ws:
            ws = list(self._registered_workspaces.values())[0]

        mrole = MemberRole.DEVELOPER
        try:
            mrole = MemberRole(role.lower())
        except ValueError:
            pass

        member = self.member_manager.add_member(ws, email.split("@")[0].capitalize(), email, mrole)
        self.activity_feed.record_activity(ws.workspace_id, email, f"Joined workspace as {mrole.value}")
        self.metrics_tracker.record_member_joined()
        return member.model_dump(mode="json")

    async def leave_workspace(self, workspace_id: str, member_id: str) -> bool:
        """Leaves or removes member from workspace."""
        ws = self._registered_workspaces.get(workspace_id)
        if not ws:
            ws = list(self._registered_workspaces.values())[0]
        return self.member_manager.remove_member(ws, member_id)

    async def workspace_members(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Lists members of workspace."""
        ws = self._registered_workspaces.get(workspace_id) or list(self._registered_workspaces.values())[0]
        return [m.model_dump(mode="json") for m in ws.members]

    async def workspace_search(self, workspace_id: str, query: str) -> Dict[str, Any]:
        """Searches across workspace documents, projects, and workflows."""
        res = self.workspace_search_engine.search_workspace(workspace_id, query)
        return res.model_dump(mode="json")

    async def workspace_sync(self, workspace_id: str) -> Dict[str, Any]:
        """Synchronizes workspace knowledge, models, and workflows."""
        res = self.sync_engine.sync_workspace(workspace_id)
        self.knowledge_sync.sync_knowledge_collections(workspace_id)
        self.metrics_tracker.record_sync_operation()
        return res

    async def remote_execute(self, target_device_id: str, command_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes remote desktop/browser automation or model task."""
        req = RemoteExecutionRequest(target_device_id=target_device_id, command_type=command_type, payload=payload)
        res = await self.remote_execution.execute_remote(req)
        self.metrics_tracker.record_remote_execution()
        return res.model_dump(mode="json")

    async def workspace_backup(self, workspace_id: str) -> Dict[str, Any]:
        """Creates full workspace snapshot backup."""
        return self.backup_engine.create_backup(workspace_id)

    async def workspace_restore(self, backup_id: str) -> Dict[str, Any]:
        """Restores workspace from snapshot backup."""
        return self.restore_engine.restore_backup(backup_id)

    async def workspace_activity(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Retrieves real-time workspace activity feed log."""
        return self.activity_feed.get_activities(workspace_id)

    async def check_health(self) -> WorkspaceHealth:
        """Retrieves workspace platform health diagnostics."""
        ws_count = len(self._registered_workspaces)
        members_count = sum(len(ws.members) for ws in self._registered_workspaces.values())
        return self.health_monitor.check_health(ws_count, members_count, 2)

    async def get_metrics(self) -> WorkspaceMetrics:
        """Retrieves telemetry metrics."""
        return self.metrics_tracker.get_metrics()
