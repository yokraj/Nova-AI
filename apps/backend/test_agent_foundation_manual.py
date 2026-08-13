"""Manual Validation script for the Multi-Agent Foundation.
"""

import asyncio
from app.ai.agents.configuration import MultiAgentFoundationConfiguration
from app.ai.agents.manager import AgentManager
from app.ai.agents.models import AgentMetadata, AgentDescriptor, AgentCapability
from app.ai.agents.state_machine import AgentStateValue
from app.ai.agents.permissions import PermissionProfile

async def main():
    print("===========================================")
    print("Nova AI Multi-Agent Foundation Validation")
    print("===========================================")

    passed = 0
    total = 12

    # Initialize manager
    manager = AgentManager()

    # Meta and descriptor
    meta = AgentMetadata(
        id="manual_agent",
        name="ManualAgent",
        type="manual",
        capabilities=[AgentCapability(name="doing_work", description="does manual validation work")],
        permissions=[PermissionProfile.READ_ONLY]
    )
    desc = AgentDescriptor(
        class_path="app.ai.agents.implementations.mock_agent.MockAgent",
        dependencies=[]
    )

    # Stage 1: Registry
    try:
        manager.registry.register(desc, meta)
        assert manager.registry.exists("manual_agent") is True
        print(f"{'Stage 1   Registry':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 1   Registry':<35} FAIL ({str(err)})")

    # Stage 2: Manager
    try:
        await manager.start_agent("manual_agent")
        assert manager.get_agent("manual_agent") is not None
        print(f"{'Stage 2   Manager':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 2   Manager':<35} FAIL ({str(err)})")

    # Stage 3: Factory
    try:
        agent = manager.get_agent("manual_agent")
        assert agent is not None
        assert agent.name == "ManualAgent"
        print(f"{'Stage 3   Factory':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 3   Factory':<35} FAIL ({str(err)})")

    # Stage 4: Lifecycle
    try:
        res = await agent.execute("manual test task")
        assert res.status == "success"
        print(f"{'Stage 4   Lifecycle':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 4   Lifecycle':<35} FAIL ({str(err)})")

    # Stage 5: State Machine
    try:
        assert agent.state == AgentStateValue.READY
        try:
            agent.state_machine.transition_to(AgentStateValue.CREATED)
            print(f"{'Stage 5   State Machine':<35} FAIL (allowed illegal transition)")
        except Exception:
            print(f"{'Stage 5   State Machine':<35} PASS")
            passed += 1
    except Exception as err:
        print(f"{'Stage 5   State Machine':<35} FAIL ({str(err)})")

    # Stage 6: Event Bus
    try:
        received = []
        async def listener(agent_id: str) -> None:
            received.append(agent_id)
        manager.event_bus.subscribe("CustomEvent", listener)
        await manager.event_bus.publish("CustomEvent", agent_id="test")
        assert received == ["test"]
        print(f"{'Stage 6   Event Bus':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 6   Event Bus':<35} FAIL ({str(err)})")

    # Stage 7: Dependency Injection
    try:
        assert manager.container.resolve("registry") == manager.registry
        print(f"{'Stage 7   Dependency Injection':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 7   Dependency Injection':<35} FAIL ({str(err)})")

    # Stage 8: Scheduler
    try:
        scheduler_run = False
        async def sched_task() -> None:
            nonlocal scheduler_run
            scheduler_run = True
        manager.scheduler.schedule_immediate(sched_task())
        await asyncio.sleep(0.01)
        assert scheduler_run is True
        print(f"{'Stage 8   Scheduler':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 8   Scheduler':<35} FAIL ({str(err)})")

    # Stage 9: Permissions
    try:
        from app.ai.agents.permissions import PermissionsSystem
        permissions = PermissionsSystem()
        permissions.check_clearance(PermissionProfile.DEVELOPER, PermissionProfile.READ_ONLY)
        try:
            permissions.check_clearance(PermissionProfile.READ_ONLY, PermissionProfile.DEVELOPER)
            print(f"{'Stage 9   Permissions':<35} FAIL (allowed escalation)")
        except Exception:
            print(f"{'Stage 9   Permissions':<35} PASS")
            passed += 1
    except Exception as err:
        print(f"{'Stage 9   Permissions':<35} FAIL ({str(err)})")

    # Stage 10: Heartbeat
    try:
        pulse = manager.heartbeat.generate_heartbeat(agent)
        assert pulse.agent_id == "manual_agent"
        print(f"{'Stage 10  Heartbeat':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 10  Heartbeat':<35} FAIL ({str(err)})")

    # Stage 11: Memory
    try:
        await manager.memory.store_event("manual_agent", "TestEvent", "Offline manual verification log")
        print(f"{'Stage 11  Memory':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 11  Memory':<35} FAIL ({str(err)})")

    # Stage 12: Health
    try:
        from app.ai.agents.health import AgentHealthMonitor
        monitor = AgentHealthMonitor(
            manager.registry,
            manager,
            manager.container,
            manager.event_bus,
            manager.scheduler
        )
        health = await monitor.check_health()
        assert health["status"] == "healthy"
        print(f"{'Stage 12  Health':<35} PASS")
        passed += 1
    except Exception as err:
        print(f"{'Stage 12  Health':<35} FAIL ({str(err)})")

    await manager.shutdown()

    print(f"\nStages Passed: {passed}/{total} ({int(passed/total*100)}%)")
    if passed == total:
        print("\nMulti-Agent Foundation Healthy")
    else:
        print("\nMulti-Agent Foundation Unhealthy")

if __name__ == "__main__":
    asyncio.run(main())
