"""12-Stage Manual Validation Script for M3.4.2 AI Operating System Kernel.
"""

import asyncio
import os
import sys

# Ensure UTF-8 output encoding for Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add apps/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "apps/backend")))

from app.ai.kernel import (
    KernelEngine,
    KernelConfiguration,
    KernelState,
    OperatingMode,
    PriorityLevel,
    IntentRequest,
    MockKernelProvider,
)
from app.ai.gateway import AIGateway, ProviderRegistry, ModelRegistry, ProviderFactory, RetryPolicy, TimeoutPolicy


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.2 – AI Operating System Kernel & Universal Intent Orchestrator")
    print("==================================================================\n")

    engine = KernelEngine()

    # Stage 1: Core Kernel Init & PEP 562 Lazy Loading
    print("Stage 1: Core Kernel Init & PEP 562 Lazy Loader")
    assert engine.config.operating_mode == "VOICE"
    print("  [OK] Core Kernel package loaded successfully.\n")

    # Stage 2: Universal Intent Engine
    print("Stage 2: Universal Intent Engine Parse")
    queries = [
        ("Build an ecommerce website", "software_project_goal"),
        ("Summarize this PDF document", "document_analysis_goal"),
        ("Book train tickets for Tokyo", "travel_automation_goal"),
        ("Deploy my backend service to docker", "devops_goal"),
        ("Open Photoshop", "desktop_automation_goal"),
    ]
    for q, expected_goal in queries:
        req = IntentRequest(query=q)
        parsed = await engine.intent_engine.parse_intent(req)
        assert parsed["goal"] == expected_goal
        print(f"  * Raw: '{q}' -> Goal: '{parsed['goal']}' (Domain: {parsed['intent_type']})")
    print("  [OK] Universal Intent Engine parsed all natural language queries.\n")

    # Stage 3: Capability Resolver
    print("Stage 3: Capability Resolver")
    parsed_goal = {"goal": "software_project_goal", "intent_type": "software_copilot"}
    caps = await engine.capability_resolver.resolve_capabilities(parsed_goal)
    print(f"  * Agents: {caps.agents}")
    print(f"  * Services: {caps.services}")
    print(f"  * Memory Stores: {caps.memory_stores}")
    print(f"  * Execution Runtime: {caps.execution_runtime}")
    assert "software_engineer" in caps.agents
    print("  [OK] Capability Resolver matched required workforce & services.\n")

    # Stage 4: Dynamic Planner
    print("Stage 4: Dynamic Planner DAG Generation")
    plan = await engine.dynamic_planner.generate_plan(parsed_goal, caps)
    print(f"  * Plan ID: {plan.plan_id}")
    print(f"  * DAG Nodes Count: {len(plan.nodes)}")
    print(f"  * Execution Waves: {plan.waves}")
    assert len(plan.nodes) >= 3
    print("  [OK] Dynamic Planner built execution DAG with parallel waves.\n")

    # Stage 5: System Resource Manager
    print("Stage 5: System Resource Manager Snapshot")
    snap = await engine.system_snapshot()
    print(f"  * RAM Total: {snap.ram_total_mb:.1f} MB (Used: {snap.ram_used_mb:.1f} MB)")
    print(f"  * Network: {snap.network_status} | Health: {snap.health_status}")
    assert snap.ram_total_mb > 0
    print("  [OK] System Resource Manager snapshot captured.\n")

    # Stage 6: Context Engine
    print("Stage 6: Context Engine Unified OS Context")
    ctx = await engine.active_context()
    print(f"  * Active App: {ctx.active_application}")
    print(f"  * Current Project: {ctx.current_project}")
    print(f"  * Browser Tab: {ctx.browser_state.get('active_tab')}")
    assert ctx.active_application == "VSCode"
    print("  [OK] Context Engine unified conversation, desktop, browser, and memory.\n")

    # Stage 7: Runtime Coordinator
    print("Stage 7: Runtime Coordinator Execution")
    coord_res = await engine.runtime_coordinator.execute_plan(plan, ctx)
    print(f"  * Executed Plan: {coord_res['plan_id']} ({coord_res['nodes_executed']} nodes executed)")
    assert coord_res["status"] == "completed"
    print("  [OK] Runtime Coordinator executed DAG nodes across subsystems.\n")

    # Stage 8: Universal Verifier
    print("Stage 8: Universal Verification Check")
    ver_res = await engine.universal_verifier.verify_execution("Rename file", "file_exists", {"status": "success"})
    print(f"  * Verified: {ver_res.verified} | Status: {ver_res.status}")
    assert ver_res.verified is True
    print("  [OK] Universal Verifier validated post-execution condition.\n")

    # Stage 9: Event Bus
    print("Stage 9: Central Event Bus Pub-Sub")
    events_log = []
    engine.event_bus.subscribe("MISSION_STARTED", lambda e: events_log.append(e.event_type))
    await engine.event_bus.publish("MISSION_STARTED", {"goal": "Audit Security"})
    assert "MISSION_STARTED" in events_log
    print(f"  * Published & received event: {events_log[0]}")
    print("  [OK] Central Event Bus pub-sub dispatched events.\n")

    # Stage 10: OS Memory
    print("Stage 10: OS Memory State & Audit Trail")
    await engine.os_memory.record_action("test_action", {"detail": "manual_validation"})
    mem_state = await engine.os_memory.get_state()
    print(f"  * Audit Trail Entries: {len(mem_state.recent_actions)}")
    assert len(mem_state.recent_actions) > 0
    print("  [OK] OS Memory maintained active state and audit trail.\n")

    # Stage 11: Voice-First Orchestration Pipeline
    print("Stage 11: Voice-First Pipeline (Wake Word -> Response)")
    intent_res = await engine.process_intent("Deploy my backend service")
    print(f"  * Intent Status: {intent_res.status}")
    print(f"  * Spoken Voice Response: '{intent_res.voice_response}'")
    assert intent_res.status == "completed"
    assert len(intent_res.voice_response) > 0
    print("  [OK] Voice-First pipeline completed end-to-end.\n")

    # Stage 12: Security Guard Checkpoints
    print("Stage 12: Security Guard Approval Enforcement")
    sec_intent = await engine.process_intent("Delete all files in database")
    print(f"  * Sensitive Action Status: {sec_intent.status}")
    assert sec_intent.status == "approval_required"
    print("  [OK] Security Guard blocked sensitive action for user approval.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  AI Operating System Kernel & Universal Intent Orchestrator Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
