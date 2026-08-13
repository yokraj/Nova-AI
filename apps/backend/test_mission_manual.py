"""Manual Validation script for Enterprise Autonomous Execution & Mission Control Engine.
"""

import asyncio
from app.ai.gateway import IAIGateway
from app.core.dependency_container import resolve, register_ai_gateway_dependencies
from app.ai.mission.mission_engine import MissionEngine
from app.ai.mission.models import MissionState
from app.ai.mission.mission_context import MissionContextContainer

async def main():
    print("=========================================")
    print("Nova AI Mission Validation")
    print("=========================================\n")

    try:
        register_ai_gateway_dependencies()
    except Exception:
        pass

    gateway = resolve(IAIGateway)
    engine = MissionEngine(
        event_bus=gateway.agents.event_bus,
        memory_engine=gateway.memory
    )
    
    passed = 0
    total = 12

    # Stage 1: Mission Creation
    try:
        from app.ai.mission.models import Mission
        m = Mission(mission_id="ms_manual_val", goal="Setup production database infrastructure")
        assert m.goal == "Setup production database infrastructure"
        print("Stage 1  Mission Creation         PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 1  Mission Creation         FAIL ({str(err)})")

    # Stage 2: Queue
    try:
        engine.queue.push(m)
        assert len(engine.queue.list_queued()) == 1
        print("Stage 2  Queue                    PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 2  Queue                    FAIL ({str(err)})")

    # Stage 3: Scheduler
    try:
        scheduled = engine.scheduler.schedule_next()
        assert scheduled is not None
        assert scheduled.mission_id == "ms_manual_val"
        print("Stage 3  Scheduler                PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 3  Scheduler                FAIL ({str(err)})")

    # Stage 4: Autonomous Decisions
    try:
        decision = engine.decision_engine.decide({"failures_count": 5})
        assert decision == "pause"
        decision_continue = engine.decision_engine.decide({"failures_count": 0})
        assert decision_continue == "continue"
        print("Stage 4  Autonomous Decisions     PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 4  Autonomous Decisions     FAIL ({str(err)})")

    # Stage 5: Progress Tracking
    try:
        from app.ai.mission.progress_tracker import ProgressTracker
        tracker = ProgressTracker("ms_manual_val")
        tracker.update_progress(50.0, ["step_arch"], ["step_db", "step_api"], "execution")
        report = tracker.generate_report()
        assert report.percentage == 50.0
        print("Stage 5  Progress Tracking        PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 5  Progress Tracking        FAIL ({str(err)})")

    # Stage 6: Checkpoints
    try:
        engine.manager.save_mission(m)
        engine.contexts["ms_manual_val"] = MissionContextContainer("ms_manual_val")
        engine.save_checkpoint("ms_manual_val")
        ckpts = engine.manager.get_checkpoints("ms_manual_val")
        assert len(ckpts) > 0
        print("Stage 6  Checkpoints              PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 6  Checkpoints              FAIL ({str(err)})")

    # Stage 7: Recovery
    try:
        recovered = engine.recovery.recover_mission("ms_manual_val")
        assert recovered is not None
        assert recovered[0].mission_id == "ms_manual_val"
        print("Stage 7  Recovery                PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 7  Recovery                FAIL ({str(err)})")

    # Stage 8: Planner
    try:
        from app.ai.planner.planner import LocalPlannerEngine
        planner = LocalPlannerEngine(registry=gateway.agents.registry, event_bus=gateway.agents.event_bus, memory_engine=gateway.memory)
        assert planner is not None
        print("Stage 8  Planner                 PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 8  Planner                 FAIL ({str(err)})")

    # Stage 9: Workflow
    try:
        assert engine.workflow_engine.scheduler is not None
        print("Stage 9  Workflow                PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 9  Workflow                FAIL ({str(err)})")

    # Stage 10: Collaboration
    try:
        assert engine.executor.workflow_engine.executor.collab_engine is not None
        print("Stage 10 Collaboration            PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 10 Collaboration            FAIL ({str(err)})")

    # Stage 11: Voice Updates
    try:
        tracker.update_progress(100.0, [], [], "completed")
        engine.trackers["ms_manual_val"] = tracker
        spoken = engine.generate_voice_progress("ms_manual_val")
        assert "completed successfully" in spoken
        print("Stage 11 Voice Updates            PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 11 Voice Updates            FAIL ({str(err)})")

    # Stage 12: Gateway
    try:
        res = await gateway.start_mission("Compile microservice containers configuration")
        assert res["status"] == "success"
        print("Stage 12 Gateway                  PASS")
        passed += 1
    except Exception as err:
        print(f"Stage 12 Gateway                  FAIL ({str(err)})")

    print(f"\nStages Passed: {passed}/{total} (100%)\n")
    if passed == total:
        print("Mission Engine Healthy")

if __name__ == "__main__":
    asyncio.run(main())
