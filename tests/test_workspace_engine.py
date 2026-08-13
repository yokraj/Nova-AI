"""Unit and integration tests for Enterprise Workspace, Team Collaboration & Remote AI Orchestration Platform.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.workspace.engine import UniversalWorkspaceEngine
from app.ai.workspace.mock_provider import MockWorkspaceProvider
from app.ai.workspace.models import MemberRole, WorkspaceType


@pytest.mark.anyio
async def test_workspace_creation_and_member_management():
    engine = UniversalWorkspaceEngine()
    ws = await engine.create_workspace("Enterprise Core Workspace", "enterprise")
    assert ws["name"] == "Enterprise Core Workspace"
    assert ws["workspace_type"] == WorkspaceType.ENTERPRISE.value

    member = await engine.join_workspace(ws["workspace_id"], "engineer@corp.org", "developer")
    assert member["email"] == "engineer@corp.org"
    assert member["role"] == MemberRole.DEVELOPER.value

    members_list = await engine.workspace_members(ws["workspace_id"])
    assert len(members_list) >= 2


@pytest.mark.anyio
async def test_remote_execution_engine():
    engine = UniversalWorkspaceEngine()
    res = await engine.remote_execute("dev_node_01", "desktop_automation", {"action": "click_btn"})
    assert res["success"] is True
    assert "dev_node_01" in res["output"]["result"]


@pytest.mark.anyio
async def test_workspace_sync_and_search():
    engine = UniversalWorkspaceEngine()
    ws = await engine.create_workspace("Research Workspace", "research")

    sync_res = await engine.workspace_sync(ws["workspace_id"])
    assert sync_res["status"] == "SYNCED"

    search_res = await engine.workspace_search(ws["workspace_id"], "Architecture")
    assert search_res["total_results"] >= 1


@pytest.mark.anyio
async def test_shared_resources():
    engine = UniversalWorkspaceEngine()
    wf_shared = engine.shared_workflows.publish_workflow("ws_001", "wf_101", "Order Processor")
    assert wf_shared["title"] == "Order Processor"

    skills = engine.shared_skills.list_team_skills("ws_001")
    assert len(skills) >= 1

    docs = engine.shared_documents.list_documents("ws_001")
    assert len(docs) >= 1


@pytest.mark.anyio
async def test_role_and_permission_manager():
    engine = UniversalWorkspaceEngine()
    can_admin = engine.permission_manager.check_permission(MemberRole.ADMIN, "manage_members")
    assert can_admin is True

    can_viewer = engine.permission_manager.check_permission(MemberRole.VIEWER, "manage_members")
    assert can_viewer is False


@pytest.mark.anyio
async def test_backup_restore_and_export():
    engine = UniversalWorkspaceEngine()
    ws = await engine.create_workspace("Backup Test", "personal")

    backup = await engine.workspace_backup(ws["workspace_id"])
    assert backup["status"] == "COMPLETED"

    restore = await engine.workspace_restore(backup["backup_id"])
    assert restore["status"] == "RESTORED"


@pytest.mark.anyio
async def test_activity_feed_and_audit():
    engine = UniversalWorkspaceEngine()
    ws = await engine.create_workspace("Activity Workspace", "developer")

    activities = await engine.workspace_activity(ws["workspace_id"])
    assert len(activities) >= 1

    audit = engine.audit_engine.log_audit_event("DELETE_PROJECT", "admin@corp.org", "proj_001")
    assert audit["status"] == "AUDITED"


@pytest.mark.anyio
async def test_workspace_health_and_metrics():
    engine = UniversalWorkspaceEngine()
    await engine.create_workspace("Health WS", "enterprise")

    health = await engine.check_health()
    assert health.is_healthy is True
    assert health.total_workspaces_count >= 1

    metrics = await engine.get_metrics()
    assert metrics.total_workspaces >= 1


@pytest.mark.anyio
async def test_mock_workspace_provider():
    mock = MockWorkspaceProvider()
    ws = await mock.mock_create_workspace("Mock WS")
    assert ws.name == "Mock WS"

    exec_res = await mock.mock_remote_execute("mock_dev")
    assert exec_res.success is True
