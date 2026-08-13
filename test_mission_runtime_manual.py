"""12-Stage Manual Validation Script for M3.4.5 Autonomous Mission & Workflow Engine.
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

from app.ai.mission_runtime import (
    MissionRuntimeEngine,
    MissionRuntimeConfiguration,
    MissionState,
    WorkflowType,
    WorkerStatus,
    MockMissionRuntimeProvider,
)
from app.ai.gateway import AIGateway, ProviderRegistry, ModelRegistry, ProviderFactory, RetryPolicy, TimeoutPolicy


async def run_12_stage_validation():
    print("==================================================================")
    print("M3.4.5 – Autonomous Long-Running Mission Engine Validation")
    print("==================================================================\n")

    engine = MissionRuntimeEngine()

    # Stage 1: Core Package Init & PEP 562 Lazy Loader
    print("Stage 1: Core Package Init & PEP 562 Lazy Loader")
    assert engine.config.enable_voice_notifications is True
    print("  [OK] Mission Runtime package loaded successfully.\n")

    # Stage 2: Mission Manager Lifecycle
    print("Stage 2: Mission Manager (Creation, State Transitions & Cloning)")
    msn = await engine.create_mission("File GST Returns Q3", "Scrape invoices, compute tax, file GST online")
    print(f"  * Mission ID: {msn.mission_id}")
    print(f"  * Goal: '{msn.goal}'")
    print(f"  * Initial State: {msn.state.value}")
    print(f"  * Workflow Tasks Count: {len(msn.workflow.tasks)}")
    assert msn.state == MissionState.RUNNING

    paused = await engine.pause_mission(msn.mission_id)
    print(f"  * State after Pause: {paused.state.value}")
    assert paused.state == MissionState.PAUSED

    resumed = await engine.resume_mission(msn.mission_id)
    print(f"  * State after Resume: {resumed.state.value}")
    assert resumed.state == MissionState.RUNNING

    cloned = await engine.clone_mission(msn.mission_id)
    print(f"  * Cloned Mission Name: '{cloned.name}'")
    assert cloned.name == f"Copy of {msn.name}"
    print("  [OK] Mission Manager lifecycle verified.\n")

    # Stage 3: Dynamic Workflow Engine Execution
    print("Stage 3: Workflow Engine (Sequential & Dynamic Execution)")
    dyn_wf = await engine.workflow_engine.generate_dynamic_workflow("Build automated customer support bot")
    wf_res = await engine.workflow_engine.execute_workflow(dyn_wf, msn.mission_id)
    print(f"  * Workflow Type: {dyn_wf.type.value}")
    print(f"  * Tasks Executed: {len(wf_res['task_results'])}")
    assert wf_res["status"] == "completed"
    print("  [OK] Workflow Engine executed dynamic workflow pipeline.\n")

    # Stage 4: Task Scheduler
    print("Stage 4: Task Scheduler (Priority Queue & Cron Execution)")
    from app.ai.mission_runtime.models import TaskItem
    t1 = TaskItem(title="Scrape monthly bank statements", action_type="cron_task")
    await engine.task_scheduler.schedule_task(t1, delay_seconds=0.0)
    ready = engine.task_scheduler.get_pending_tasks()
    print(f"  * Pending Tasks Ready: {len(ready)}")
    print(f"  * Task Title: '{ready[0].title}'")
    assert len(ready) == 1
    print("  [OK] Task Scheduler enqueued and dispatched priority task.\n")

    # Stage 5: Mission Checkpoints
    print("Stage 5: Mission Checkpoint Engine (State Snapshots)")
    chk = await engine.checkpoint_engine.save_checkpoint(msn.mission_id, {
        "task_id": msn.workflow.tasks[0].task_id,
        "state": MissionState.RUNNING,
        "variables": {"invoice_count": 42, "total_tax": 18500.0},
    })
    print(f"  * Checkpoint ID: {chk.checkpoint_id}")
    print(f"  * Variables Saved: {chk.variables}")
    loaded_chk = await engine.checkpoint_engine.load_latest_checkpoint(msn.mission_id)
    assert loaded_chk is not None
    assert loaded_chk.variables["invoice_count"] == 42
    print("  [OK] Checkpoint Engine persisted state snapshot.\n")

    # Stage 6: Recovery Engine
    print("Stage 6: Recovery Engine (Browser & System Crash Restoration)")
    rec = await engine.recovery_engine.recover_mission(msn.mission_id, "browser_crash")
    print(f"  * Crash Type: {rec.crash_type}")
    print(f"  * Root Cause: {rec.root_cause}")
    print(f"  * Action Taken: {rec.action_taken}")
    assert rec.success is True
    print("  [OK] Recovery Engine restored state after simulated browser crash.\n")

    # Stage 7: Approval Queue
    print("Stage 7: Approval Queue (Human Approval Hold)")
    appr = await engine.approval_queue.request_approval(msn.mission_id, "Pay GST Tax Amount", "₹18,500 via NetBanking")
    print(f"  * Approval ID: {appr.approval_id}")
    print(f"  * Requested Action: '{appr.action_title}' ({appr.amount_or_details})")
    print(f"  * Status Before User Response: {appr.status}")

    approved = await engine.approval_queue.approve(appr.approval_id)
    print(f"  * Status After User Approval: {approved.status}")
    assert approved.status == "approved"
    print("  [OK] Approval Queue managed human-in-the-loop verification.\n")

    # Stage 8: Background Workers
    print("Stage 8: Background Workers (Concurrent Execution Thread Pool)")
    w_status = await engine.background_workers.dispatch_worker(msn.mission_id)
    active_workers = engine.background_workers.get_active_workers_count()
    print(f"  * Worker Status: {w_status.value}")
    print(f"  * Active Background Workers Count: {active_workers}")
    assert active_workers >= 1
    print("  [OK] Background Workers executing concurrently.\n")

    # Stage 9: Progress Engine
    print("Stage 9: Progress Engine (% Complete & ETA Calculation)")
    prog = await engine.mission_progress(msn.mission_id)
    print(f"  * Percent Complete: {prog.percent_complete:.1f}%")
    print(f"  * ETA: {prog.eta_seconds:.1f} seconds")
    print(f"  * Tasks Summary: Completed {prog.completed_tasks}, Remaining {prog.remaining_tasks}")
    print(f"  * Voice Progress Summary: '{prog.status_summary}'")
    assert prog.percent_complete > 0.0
    print("  [OK] Progress Engine calculated progress metrics.\n")

    # Stage 10: Notification Engine
    print("Stage 10: Notification Engine (Multi-Channel Alerts)")
    n_voice = await engine.notification_engine.send_notification("Voice Progress", "Filing GST return step 3 complete", channel="voice")
    n_desktop = await engine.notification_engine.send_notification("Desktop Toast", "Approval required for payment", channel="desktop")
    print(f"  * Voice Alert: '{n_voice.title}' -> {n_voice.body}")
    print(f"  * Desktop Toast: '{n_desktop.title}' -> {n_desktop.body}")
    assert len(engine.notification_engine.get_history()) >= 3
    print("  [OK] Notification Engine dispatched voice & desktop alerts.\n")

    # Stage 11: Dashboard API & Workflow Recorder
    print("Stage 11: Dashboard API & Workflow Recorder (Macro Recording)")
    dash = await engine.mission_dashboard()
    rec_wf = await engine.workflow_recorder.record_workflow([
        {"type": "navigate", "description": "Open GST Portal"},
        {"type": "click", "description": "Click Login"},
        {"type": "submit", "description": "Submit Return"},
    ], name="Recorded GST Filing Workflow")
    print(f"  * Dashboard Timeline Events: {len(dash['timeline'])}")
    print(f"  * Recorded Macro Name: '{rec_wf.name}' ({len(rec_wf.tasks)} steps)")
    assert len(dash["timeline"]) > 0
    assert len(rec_wf.tasks) == 3
    print("  [OK] Dashboard API & Workflow Recorder verified.\n")

    # Stage 12: End-to-End Autonomous Mission Execution
    print("Stage 12: End-to-End Voice Mission ('Hey Nova, perform weekly backup')")
    voice_msn = await engine.create_mission("Weekly System Backup", "Perform system file backup & verify integrity")
    print(f"  * Mission ID: {voice_msn.mission_id}")
    print(f"  * Priority: {voice_msn.priority.value}")
    print(f"  * State: {voice_msn.state.value}")
    assert voice_msn.state == MissionState.RUNNING
    print("  [OK] Voice-driven long-running mission initialized successfully.\n")

    print("==================================================================")
    print("  ALL 12 STAGES PASSED SUCCESSFULLY!")
    print("  Autonomous Long-Running Mission Engine Healthy.")
    print("==================================================================")


if __name__ == "__main__":
    asyncio.run(run_12_stage_validation())
