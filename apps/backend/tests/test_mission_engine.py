"""Automated unit test suite verifying Mission Control Engine operations.
"""

import pytest
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.mission.mission_engine import MissionEngine
from app.ai.mission.models import MissionState

@pytest.mark.anyio
async def test_mission_engine_flows():
    """Verifies complete mission lifecycles, queue operations, schedulers, decision policies, and recovery."""
    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = MissionEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )

    # 1. Test creation
    mission = engine.builder = engine.mock.simulate_mission_run()
    assert mission["mission_id"] == "mock_mission_123"
    assert mission["state"] == "completed"

    # 2. Test queuing and scheduling
    from app.ai.mission.models import Mission
    m1 = Mission(mission_id="ms_test_1", goal="Design compiler schemas")
    engine.queue.push(m1)
    assert len(engine.queue.list_queued()) == 1
    assert engine.queue.list_queued()[0].mission_id == "ms_test_1"

    # Schedule next
    scheduled = engine.scheduler.schedule_next()
    assert scheduled is not None
    assert scheduled.mission_id == "ms_test_1"
    assert scheduled.state == MissionState.PLANNING

    # 3. Test decision engine
    decision = engine.decision_engine.decide({"failures_count": 5})
    assert decision == "pause"

    decision_ok = engine.decision_engine.decide({"failures_count": 0})
    assert decision_ok == "continue"

    # 4. Test checkpoints and recovery
    from app.ai.mission.mission_context import MissionContextContainer
    engine.manager.save_mission(m1)
    engine.contexts["ms_test_1"] = MissionContextContainer("ms_test_1")
    engine.save_checkpoint("ms_test_1")
    ckpts = engine.manager.get_checkpoints("ms_test_1")
    assert len(ckpts) > 0

    # Recover
    recovered = engine.recovery.recover_mission("ms_test_1")
    assert recovered is not None
    assert recovered[0].mission_id == "ms_test_1"

    # 5. Test gateway lifecycle execution
    res = await gateway.start_mission("Develop CRM customer records backend systems")
    assert res["status"] == "success"
    assert res["state"] == "completed"
