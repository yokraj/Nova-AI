"""Unit and integration tests for Universal Workflow Learning & No-Code Automation Studio.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.workflow_studio.engine import UniversalWorkflowStudioEngine
from app.ai.workflow_studio.mock_provider import MockWorkflowStudioProvider
from app.ai.workflow_studio.models import WorkflowRecordingState


@pytest.mark.anyio
async def test_workflow_recording_flow():
    engine = UniversalWorkflowStudioEngine()
    start_res = await engine.record_workflow("Order Processing")
    assert start_res["status"] == "RECORDING"
    assert engine.recorder.state == WorkflowRecordingState.RECORDING

    stop_res = await engine.stop_recording()
    assert stop_res["name"] == "New Recorded Workflow"
    assert len(stop_res["steps"]) >= 1
    assert len(stop_res["variables"]) >= 1


@pytest.mark.anyio
async def test_workflow_playback_and_history():
    engine = UniversalWorkflowStudioEngine()
    workflows = await engine.list_workflows()
    assert len(workflows) >= 1

    target_id = workflows[0]["workflow_id"]
    play_res = await engine.play_workflow(target_id)
    assert play_res["success"] is True

    history = await engine.workflow_history()
    assert len(history) >= 1


@pytest.mark.anyio
async def test_workflow_editing_and_versioning():
    engine = UniversalWorkflowStudioEngine()
    workflows = await engine.list_workflows()
    target_id = workflows[0]["workflow_id"]

    edited = await engine.edit_workflow(target_id, {"name": "Updated Order Processor"})
    assert edited["name"] == "Updated Order Processor"
    assert edited["version"] == "1.0.1"


@pytest.mark.anyio
async def test_variable_detection_engine():
    engine = UniversalWorkflowStudioEngine()
    text = "Send confirmation email to user@test.com for amount $1250.00 OTP 654321"
    vars_detected = engine.variable_engine.detect_variables(text)
    assert len(vars_detected) == 3
    var_types = [v.var_type for v in vars_detected]
    assert "email" in var_types
    assert "currency" in var_types
    assert "otp" in var_types


@pytest.mark.anyio
async def test_triggers_and_scheduler():
    engine = UniversalWorkflowStudioEngine()
    trig_voice = engine.trigger_engine.create_voice_trigger("Hey Nova, execute order processor")
    assert trig_voice.expression == "Hey Nova, execute order processor"

    cron_job = engine.scheduler.schedule_cron_job("wf_001", "0 9 * * *")
    assert cron_job["status"] == "SCHEDULED"


@pytest.mark.anyio
async def test_export_import_and_sharing():
    engine = UniversalWorkflowStudioEngine()
    exported = await engine.export_workflow("tmpl_001")
    assert "E-Commerce Order Processor" in exported or "name" in exported

    imported = await engine.import_workflow(exported)
    assert "workflow_id" in imported

    shared = await engine.share_workflow(imported["workflow_id"])
    assert shared["status"] == "SHARED"


@pytest.mark.anyio
async def test_marketplace_and_recommendations():
    engine = UniversalWorkflowStudioEngine()
    search_res = engine.marketplace.search_marketplace("Order")
    assert len(search_res) >= 1

    recs = engine.recommendation_engine.generate_recommendations()
    assert len(recs) >= 1


@pytest.mark.anyio
async def test_workflow_studio_health_and_metrics():
    engine = UniversalWorkflowStudioEngine()
    await engine.record_workflow("Health Session")
    await engine.stop_recording()

    health = await engine.check_health()
    assert health.is_healthy is True
    assert health.total_workflows_count >= 1

    metrics = await engine.get_metrics()
    assert metrics.total_recordings >= 1


@pytest.mark.anyio
async def test_mock_workflow_studio_provider():
    mock = MockWorkflowStudioProvider()
    wf = await mock.mock_record_workflow("Mock Session")
    assert wf.name == "Mock Session"

    play = await mock.mock_play_workflow(wf.workflow_id)
    assert play.success is True
