"""Unit and integration tests for Autonomous Long-Running Mission & Workflow Engine.
"""

import pytest
from app.ai.mission_runtime.runtime_engine import MissionRuntimeEngine
from app.ai.mission_runtime.mock_provider import MockMissionRuntimeProvider
from app.ai.mission_runtime.models import (
    MissionState,
    WorkflowType,
    WorkerStatus,
)


@pytest.mark.anyio
async def test_mission_manager_lifecycle():
    engine = MissionRuntimeEngine()
    mission = await engine.create_mission("Test Long Mission", "Automate weekly report filing")
    assert mission.mission_id.startswith("msn_")
    assert mission.state == MissionState.RUNNING
    assert len(mission.workflow.tasks) >= 3

    paused = await engine.pause_mission(mission.mission_id)
    assert paused.state == MissionState.PAUSED

    resumed = await engine.resume_mission(mission.mission_id)
    assert resumed.state == MissionState.RUNNING

    cloned = await engine.clone_mission(mission.mission_id)
    assert cloned.name == f"Copy of {mission.name}"


@pytest.mark.anyio
async def test_workflow_engine_execution():
    engine = MissionRuntimeEngine()
    wf = await engine.workflow_engine.generate_dynamic_workflow("Build e-commerce backend")
    assert wf.type == WorkflowType.DYNAMIC
    assert len(wf.tasks) == 4

    res = await engine.workflow_engine.execute_workflow(wf, "msn_test123")
    assert res["status"] == "completed"
    assert len(res["task_results"]) == 4


@pytest.mark.anyio
async def test_checkpoint_and_recovery_engine():
    engine = MissionRuntimeEngine()
    chk = await engine.checkpoint_engine.save_checkpoint("msn_chk123", {
        "task_id": "tsk_1",
        "state": MissionState.RUNNING,
        "variables": {"step": 1},
    })
    assert chk.checkpoint_id.startswith("chk_")

    loaded = await engine.checkpoint_engine.load_latest_checkpoint("msn_chk123")
    assert loaded is not None
    assert loaded.task_id == "tsk_1"

    rec = await engine.recovery_engine.recover_mission("msn_chk123", "browser_crash")
    assert rec.success is True
    assert rec.crash_type == "browser_crash"


@pytest.mark.anyio
async def test_approval_queue():
    engine = MissionRuntimeEngine()
    appr = await engine.approval_queue.request_approval("msn_appr123", "Transfer Funds", "₹10,000 to Account X")
    assert appr.status == "pending"

    pending = await engine.approval_queue.list_pending_approvals()
    assert len(pending) == 1

    approved = await engine.approval_queue.approve(appr.approval_id)
    assert approved.status == "approved"


@pytest.mark.anyio
async def test_task_scheduler():
    engine = MissionRuntimeEngine()
    from app.ai.mission_runtime.models import TaskItem
    t1 = TaskItem(title="Task Scheduled")
    await engine.task_scheduler.schedule_task(t1, delay_seconds=0.0)
    assert engine.task_scheduler.get_queue_size() == 1

    ready = engine.task_scheduler.get_pending_tasks()
    assert len(ready) == 1
    assert ready[0].title == "Task Scheduled"


@pytest.mark.anyio
async def test_background_workers_and_progress():
    engine = MissionRuntimeEngine()
    status = await engine.background_workers.dispatch_worker("msn_bg123")
    assert status == WorkerStatus.WORKING

    prog = await engine.mission_progress("msn_bg123")
    assert prog.percent_complete == 60.0
    assert prog.eta_seconds >= 0.0


@pytest.mark.anyio
async def test_notification_engine_and_memory():
    engine = MissionRuntimeEngine()
    msg = await engine.notification_engine.send_notification("Title", "Body", channel="voice")
    assert msg.channel == "voice"

    await engine.mission_memory.log_event("msn_mem123", "step_complete", {"task": "Task 1"})
    logs = await engine.mission_memory.get_logs("msn_mem123")
    assert len(logs) == 1

    sug = await engine.mission_memory.get_optimization_suggestions("msn_mem123")
    assert len(sug) > 0


@pytest.mark.anyio
async def test_dashboard_api_and_recorder():
    engine = MissionRuntimeEngine()
    dash = await engine.mission_dashboard()
    assert "active_missions_count" in dash
    assert len(dash["timeline"]) > 0

    actions = [{"type": "click", "description": "Click GST login"}]
    wf = await engine.workflow_recorder.record_workflow(actions, "GST Filing Macro")
    assert wf.name == "GST Filing Macro"
    assert len(wf.tasks) == 1


@pytest.mark.anyio
async def test_mock_mission_runtime_provider():
    mock = MockMissionRuntimeProvider()
    msn = await mock.create_mission("Mock Mission", "Test goal")
    assert msn.mission_id == "msn_mock123"

    prog = await mock.mission_progress("msn_mock123")
    assert prog.percent_complete == 50.0

    health = await mock.check_health()
    assert health.is_healthy is True
