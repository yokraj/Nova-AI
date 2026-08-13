"""Unit and integration tests for AI Operating System Core & Always-On Voice Runtime.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.os_runtime.engine import NovaOperatingSystemEngine
from app.ai.os_runtime.mock_provider import MockOSRuntimeProvider
from app.ai.os_runtime.models import OSState


@pytest.mark.anyio
async def test_start_and_stop_os():
    engine = NovaOperatingSystemEngine()
    boot_diag = await engine.start_os()
    assert boot_diag.success is True
    assert len(boot_diag.subsystems_loaded) >= 20

    stop_res = await engine.stop_os()
    assert stop_res["status"] == "SHUTDOWN_COMPLETED"


@pytest.mark.anyio
async def test_os_lifecycle_transitions():
    engine = NovaOperatingSystemEngine()
    state_pause = await engine.pause_os()
    assert state_pause == OSState.PAUSED

    state_resume = await engine.resume_os()
    assert state_resume == OSState.RUNNING


@pytest.mark.anyio
async def test_always_on_voice_runtime():
    engine = NovaOperatingSystemEngine()
    voice_res = await engine.voice_runtime.process_voice_turn()
    assert voice_res["wake_word_detected"] is True
    assert voice_res["tts_audio_generated"] is True

    engine.voice_runtime.set_privacy_pause(True)
    paused_res = await engine.voice_runtime.process_voice_turn()
    assert paused_res["status"] == "PRIVACY_PAUSED"


@pytest.mark.anyio
async def test_context_runtime_observation():
    engine = NovaOperatingSystemEngine()
    context = await engine.context_runtime.get_unified_context_snapshot()
    assert "active_window" in context
    assert "hardware_telemetry" in context


@pytest.mark.anyio
async def test_global_event_runtime_pubsub():
    engine = NovaOperatingSystemEngine()
    event_received = []

    def subscriber(evt):
        event_received.append(evt)

    engine.event_runtime.subscribe("TEST_EVENT", subscriber)
    evt = await engine.event_runtime.publish_event("TEST_EVENT", {"data": "test"})
    assert evt.event_type == "TEST_EVENT"
    assert len(event_received) == 1


@pytest.mark.anyio
async def test_unified_scheduler_runtime():
    engine = NovaOperatingSystemEngine()
    job = await engine.scheduler_runtime.schedule_job("Backup Database", category="backup", interval_seconds=3600)
    assert job.name == "Backup Database"
    assert len(engine.scheduler_runtime.list_jobs()) >= 1


@pytest.mark.anyio
async def test_decision_loop_runtime():
    engine = NovaOperatingSystemEngine()
    cycle_res = await engine.decision_runtime.execute_cycle()
    assert cycle_res["phase"] == "DECISION_CYCLE_COMPLETED"


@pytest.mark.anyio
async def test_speech_interrupt_barge_in():
    engine = NovaOperatingSystemEngine()
    barge = await engine.interrupt_runtime.handle_user_barge_in()
    assert barge["tts_paused"] is True
    assert barge["listening_active"] is True

    resume = await engine.interrupt_runtime.resume_after_interrupt()
    assert resume["automation_resumed"] is True


@pytest.mark.anyio
async def test_idle_optimization_runtime():
    engine = NovaOperatingSystemEngine()
    idle_res = await engine.idle_runtime.run_idle_optimization()
    assert idle_res["status"] == "IDLE_OPTIMIZATION_COMPLETED"


@pytest.mark.anyio
async def test_proactive_recommendations_runtime():
    engine = NovaOperatingSystemEngine()
    recs = await engine.proactive_runtime.generate_recommendations()
    assert len(recs) >= 1
    assert "rec_id" in recs[0]


@pytest.mark.anyio
async def test_session_runtime_and_workspace_switching():
    engine = NovaOperatingSystemEngine()
    session = await engine.session_runtime.get_active_session()
    assert session.user_id == "owner@nova-ai.org"

    switched = await engine.session_runtime.switch_workspace("Dev Workspace")
    assert switched.active_workspace == "Dev Workspace"


@pytest.mark.anyio
async def test_self_healing_recovery_runtime():
    engine = NovaOperatingSystemEngine()
    recovery = await engine.recovery_runtime.recover_subsystem("Desktop Automation", "Driver crashed")
    assert recovery["recovered"] is True
    assert recovery["status"] == "SELF_HEALED"


@pytest.mark.anyio
async def test_dashboard_and_telemetry_runtime():
    engine = NovaOperatingSystemEngine()
    dash = await engine.os_dashboard()
    assert dash.os_state == OSState.RUNNING
    assert dash.health_score == 100.0


@pytest.mark.anyio
async def test_notification_runtime():
    engine = NovaOperatingSystemEngine()
    notif = await engine.notification_runtime.notify("Test Alert", "Mission Completed")
    assert notif.title == "Test Alert"


@pytest.mark.anyio
async def test_resource_optimization_runtime():
    engine = NovaOperatingSystemEngine()
    res = await engine.resource_runtime.optimize_resources()
    assert res["status"] == "RESOURCES_OPTIMIZED"


@pytest.mark.anyio
async def test_security_policy_runtime():
    engine = NovaOperatingSystemEngine()
    policy = await engine.security_runtime.get_policy()
    assert policy.enforce_approval_holds is True


@pytest.mark.anyio
async def test_plugin_hot_reload_runtime():
    engine = NovaOperatingSystemEngine()
    plugin_res = await engine.plugin_runtime.hot_reload_plugin("skill_vscode")
    assert plugin_res["status"] == "HOT_RELOADED"


@pytest.mark.anyio
async def test_distributed_node_orchestration():
    engine = NovaOperatingSystemEngine()
    node_res = await engine.distributed_runtime.orchestrate_node("node_linux_01", "check_gpu")
    assert node_res["orchestrated"] is True


@pytest.mark.anyio
async def test_emergency_stop_kill_switch():
    engine = NovaOperatingSystemEngine()
    stop_res = await engine.emergency_stop()
    assert stop_res["kill_switch_activated"] is True
    assert stop_res["state"] == OSState.EMERGENCY_STOP


@pytest.mark.anyio
async def test_mock_os_runtime_provider():
    mock = MockOSRuntimeProvider()
    boot = await mock.mock_boot_system()
    assert boot.success is True

    health = await mock.mock_get_health()
    assert health.is_healthy is True
