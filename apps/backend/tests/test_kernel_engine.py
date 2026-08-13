"""Unit and integration tests for AI OS Kernel Engine and components.
"""

import pytest
from app.ai.kernel.kernel_engine import KernelEngine
from app.ai.kernel.models import (
    IntentRequest,
    OperatingMode,
    PriorityLevel,
    KernelState,
)
from app.ai.kernel.mock_provider import MockKernelProvider


@pytest.mark.anyio
async def test_universal_intent_engine_parsing():
    engine = KernelEngine()
    req = IntentRequest(query="Build an ecommerce website", operating_mode=OperatingMode.VOICE)
    parsed = await engine.intent_engine.parse_intent(req)
    assert parsed["goal"] == "software_project_goal"
    assert parsed["intent_type"] == "software_copilot"


@pytest.mark.anyio
async def test_capability_resolver():
    engine = KernelEngine()
    parsed = {"goal": "software_project_goal", "intent_type": "software_copilot"}
    caps = await engine.capability_resolver.resolve_capabilities(parsed)
    assert "software_engineer" in caps.agents
    assert "code_memory" in caps.services


@pytest.mark.anyio
async def test_dynamic_planner():
    engine = KernelEngine()
    parsed = {"goal": "software_project_goal", "intent_type": "software_copilot", "raw_query": "Build site"}
    caps = await engine.capability_resolver.resolve_capabilities(parsed)
    plan = await engine.dynamic_planner.generate_plan(parsed, caps)
    assert plan.goal == "software_project_goal"
    assert len(plan.nodes) >= 3
    assert len(plan.waves) >= 3


@pytest.mark.anyio
async def test_resource_manager():
    engine = KernelEngine()
    snap = await engine.system_snapshot()
    assert snap.ram_total_mb > 0
    assert snap.network_status == "ONLINE"
    assert snap.health_status in ["HEALTHY", "WARNING"]


@pytest.mark.anyio
async def test_context_engine():
    engine = KernelEngine()
    ctx = await engine.active_context()
    assert ctx.active_application == "VSCode"
    assert ctx.current_project == "c:\\Projects\\Nova-AI"


@pytest.mark.anyio
async def test_universal_verifier():
    engine = KernelEngine()
    res = await engine.universal_verifier.verify_execution(
        step_title="Rename file",
        check_spec="file_exists",
        result_data={"status": "success"},
    )
    assert res.verified is True
    assert res.status == "SUCCESS"


@pytest.mark.anyio
async def test_event_bus():
    engine = KernelEngine()
    received = []

    def handle_event(evt):
        received.append(evt.event_type)

    engine.event_bus.subscribe("MISSION_STARTED", handle_event)
    await engine.event_bus.publish("MISSION_STARTED", {"goal": "test"})
    assert "MISSION_STARTED" in received


@pytest.mark.anyio
def test_security_guard():
    engine = KernelEngine()
    assert engine.security_guard.check_approval_required("delete_file", {"path": "/tmp/a"}) is True
    assert engine.security_guard.check_approval_required("read_file", {"path": "/tmp/a"}) is False


@pytest.mark.anyio
async def test_kernel_engine_process_intent_end_to_end():
    engine = KernelEngine()
    res = await engine.process_intent("Summarize this PDF document")
    assert res.status == "completed"
    assert res.verification.verified is True
    assert len(res.voice_response) > 0


@pytest.mark.anyio
async def test_kernel_pause_and_resume():
    engine = KernelEngine()
    pause_res = await engine.pause_kernel()
    assert pause_res["status"] == "paused"

    with pytest.raises(Exception):
        await engine.process_intent("Hello")

    resume_res = await engine.resume_kernel()
    assert resume_res["status"] == "resumed"


@pytest.mark.anyio
async def test_mock_kernel_provider():
    provider = MockKernelProvider()
    res = await provider.process_intent(IntentRequest(query="Test query"))
    assert res.status == "completed"
    snap = await provider.capture_snapshot()
    assert snap.health_status == "HEALTHY"
